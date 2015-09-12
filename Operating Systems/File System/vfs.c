#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <time.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <readline/readline.h>
#include <readline/history.h>

#define MAXARGS 100
#define CHECK_NUMBER 9999
#define TYPE_DIR 'D'
#define TYPE_FILE 'F'
#define MAX_NAME_LENGHT 20

#define FAT_ENTRIES(TYPE) (TYPE == 7 ? 128 : TYPE == 8 ? 256 : TYPE == 9 ? 512 : 1024)
#define FAT_SIZE(TYPE) (FAT_ENTRIES(TYPE) * sizeof(int))
#define BLOCK(N) (blocks + N * sb->block_size)
#define DIR_ENTRIES_PER_BLOCK (sb->block_size / sizeof(dir_entry))

typedef struct command {
  char *cmd;              // string apenas com o comando
  int argc;               // n�mero de argumentos
  char *argv[MAXARGS+1];  // vector de argumentos do comando
} COMMAND;

typedef struct superblock_entry {
  int check_number;   // n�mero que permite identificar o sistema como v�lido
  int block_size;     // tamanho de um bloco {128, 256(default), 512 ou 1024 bytes}
  int fat_type;       // tipo de FAT {7, 8(default), 9 ou 10}
  int root_block;     // n�mero do 1� bloco a que corresponde o direct�rio raiz
  int free_block;     // n�mero do 1� bloco da lista de blocos n�o utilizados
  int n_free_blocks;  // total de blocos n�o utilizados
} superblock;

typedef struct directory_entry {
  char type;                   // tipo da entrada (TYPE_DIR ou TYPE_FILE)
  char name[MAX_NAME_LENGHT];  // nome da entrada
  unsigned char day;           // dia em que foi criada (entre 1 e 31)
  unsigned char month;         // mes em que foi criada (entre 1 e 12)
  unsigned char year;          // ano em que foi criada (entre 0 e 255 - 0 representa o ano de 1900)
  int size;                    // tamanho em bytes (0 se TYPE_DIR)
  int first_block;             // primeiro bloco de dados
} dir_entry;

static const char mon_name[][4] = {
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
};

// vari�veis globais
superblock *sb;   // superblock do sistema de ficheiros
int *fat;         // apontador para a FAT
char *blocks;     // apontador para a regi�o dos dados
int current_dir;  // bloco do direct�rio corrente

// fun��es auxiliares
COMMAND parse(char*);
void parse_argv(int, char*[]);
void init_filesystem(int, int, char*);
void init_superblock(int, int);
void init_fat(void);
void init_dir_block(int, int);
void init_dir_entry(dir_entry*, char, char*, int, int);
void exec_com(COMMAND);

// fun��es de manipula��o de direct�rios
void vfs_ls(void);
void vfs_mkdir(char*);
void vfs_cd(char*);
void vfs_pwd(void);
void vfs_rmdir(char*);

// fun��es de manipula��o de ficheiros
void vfs_get(char*, char*);
void vfs_put(char*, char*);
void vfs_cat(char*);
void vfs_cp(char*, char*);
void vfs_mv(char*, char*);
void vfs_rm(char*);


int main(int argc, char *argv[]) {
  char *linha;
  COMMAND com;

  parse_argv(argc, argv);
  while (1) {
    if ((linha = readline("vfs$ ")) == NULL)
    exit(0);
    if (strlen(linha) != 0) {
      add_history(linha);
      com = parse(linha);
      exec_com(com);
    }
    free(linha);
  }
  return 0;
}


COMMAND parse(char *linha) {
  int i = 0;
  COMMAND com;

  com.cmd = strtok(linha, " ");
  com.argv[0] = com.cmd;
  while ((com.argv[++i] = strtok(NULL, " ")) != NULL);
  com.argc = i;
  return com;
}


void parse_argv(int argc, char *argv[]) {
  int i, block_size, fat_type;

  block_size = 256; // valor por omiss�o
  fat_type = 8;    // valor por omiss�o
  if (argc < 2 || argc > 4) {
    printf("vfs: invalid number of arguments\n");
    printf("Usage: vfs [-b[128|256|512|1024]] [-f[7|8|9|10]] FILESYSTEM\n");
    exit(1);
  }
  for (i = 1; i < argc - 1; i++) {
    if (argv[i][0] == '-') {
      if (argv[i][1] == 'b') {
        block_size = atoi(&argv[i][2]);
        if (block_size != 128 && block_size != 256 && block_size != 512 && block_size != 1024) {
          printf("vfs: invalid block size (%d)\n", block_size);
          printf("Usage: vfs [-b[128|256|512|1024]] [-f[7|8|9|10]] FILESYSTEM\n");
          exit(1);
        }
      } else if (argv[i][1] == 'f') {
        fat_type = atoi(&argv[i][2]);
        if (fat_type != 7 && fat_type != 8 && fat_type != 9 && fat_type != 10) {
          printf("vfs: invalid fat type (%d)\n", fat_type);
          printf("Usage: vfs [-b[128|256|512|1024]] [-f[7|8|9|10]] FILESYSTEM\n");
          exit(1);
        }
      } else {
        printf("vfs: invalid argument (%s)\n", argv[i]);
        printf("Usage: vfs [-b[128|256|512|1024]] [-f[7|8|9|10]] FILESYSTEM\n");
        exit(1);
      }
    } else {
      printf("vfs: invalid argument (%s)\n", argv[i]);
      printf("Usage: vfs [-b[128|256|512|1024]] [-f[7|8|9|10]] FILESYSTEM\n");
      exit(1);
    }
  }
  init_filesystem(block_size, fat_type, argv[argc-1]);
  return;
}


void init_filesystem(int block_size, int fat_type, char *filesystem_name) {
  int fsd, filesystem_size;

  if ((fsd = open(filesystem_name, O_RDWR)) == -1) {
    // o sistema de ficheiros n�o existe --> � necess�rio cri�-lo e format�-lo
    if ((fsd = open(filesystem_name, O_CREAT | O_TRUNC | O_RDWR, S_IRWXU)) == -1) {
      printf("vfs: cannot create filesystem (%s)\n", filesystem_name);
      printf("Usage: vfs [-b[128|256|512|1024]] [-f[7|8|9|10]] FILESYSTEM\n");
      exit(1);
    }

    // calcula o tamanho do sistema de ficheiros
    filesystem_size = block_size + FAT_SIZE(fat_type) + FAT_ENTRIES(fat_type) * block_size;
    printf("vfs: formatting virtual file-system (%d bytes) ... please wait\n", filesystem_size);

    // estende o sistema de ficheiros para o tamanho desejado
    lseek(fsd, filesystem_size - 1, SEEK_SET);
    write(fsd, "", 1);

    // faz o mapeamento do sistema de ficheiros e inicia as vari�veis globais
    if ((sb = (superblock *) mmap(NULL, filesystem_size, PROT_READ | PROT_WRITE, MAP_SHARED, fsd, 0)) == MAP_FAILED) {
      printf("vfs: cannot map filesystem (mmap error)\n");
      close(fsd);
      exit(1);
    }
    fat = (int *) ((unsigned long int) sb + block_size);
    blocks = (char *) ((unsigned long int) fat + FAT_SIZE(fat_type));

    // inicia o superblock
    init_superblock(block_size, fat_type);

    // inicia a FAT
    init_fat();

    // inicia o bloco do direct�rio raiz '/'
    init_dir_block(sb->root_block, sb->root_block);
  } else {
    // calcula o tamanho do sistema de ficheiros
    struct stat buf;
    stat(filesystem_name, &buf);
    filesystem_size = buf.st_size;

    // faz o mapeamento do sistema de ficheiros e inicia as vari�veis globais
    if ((sb = (superblock *) mmap(NULL, filesystem_size, PROT_READ | PROT_WRITE, MAP_SHARED, fsd, 0)) == MAP_FAILED) {
      printf("vfs: cannot map filesystem (mmap error)\n");
      close(fsd);
      exit(1);
    }
    fat = (int *) ((unsigned long int) sb + sb->block_size);
    blocks = (char *) ((unsigned long int) fat + FAT_SIZE(sb->fat_type));

    // testa se o sistema de ficheiros � v�lido
    if (sb->check_number != CHECK_NUMBER || filesystem_size != sb->block_size + FAT_SIZE(sb->fat_type) + FAT_ENTRIES(sb->fat_type) * sb->block_size) {
      printf("vfs: invalid filesystem (%s)\n", filesystem_name);
      printf("Usage: vfs [-b[128|256|512|1024]] [-f[7|8|9|10]] FILESYSTEM\n");
      munmap(sb, filesystem_size);
      close(fsd);
      exit(1);
    }
  }
  close(fsd);

  // inicia o direct�rio corrente
  current_dir = sb->root_block;
  return;
}


void init_superblock(int block_size, int fat_type) {
  sb->check_number = CHECK_NUMBER;
  sb->block_size = block_size;
  sb->fat_type = fat_type;
  sb->root_block = 0;
  sb->free_block = 1;
  sb->n_free_blocks = FAT_ENTRIES(fat_type) - 1;
  return;
}


void init_fat(void) {
  int i;

  fat[0] = -1;
  for (i = 1; i < sb->n_free_blocks; i++)
  fat[i] = i + 1;
  fat[sb->n_free_blocks] = -1;
  return;
}


void init_dir_block(int block, int parent_block) {
  dir_entry *dir = (dir_entry *) BLOCK(block);
  // o n�mero de entradas no direct�rio (inicialmente 2) fica guardado no campo size da entrada "."
  init_dir_entry(&dir[0], TYPE_DIR, ".", 2, block);
  init_dir_entry(&dir[1], TYPE_DIR, "..", 0, parent_block);
  return;
}


void init_dir_entry(dir_entry *dir, char type, char *name, int size, int first_block) {
  time_t cur_time = time(NULL);
  struct tm *cur_tm = localtime(&cur_time);

  dir->type = type;
  strcpy(dir->name, name);
  dir->day = cur_tm->tm_mday;
  dir->month = cur_tm->tm_mon + 1;
  dir->year = cur_tm->tm_year;
  dir->size = size;
  dir->first_block = first_block;
  return;
}

void exec_com(COMMAND com) {
  // para cada comando invocar a fun��o que o implementa
  if (!strcmp(com.cmd, "exit"))
  exit(0);
  if (!strcmp(com.cmd, "ls")) {
    // falta tratamento de erros
    vfs_ls();
  } else if (!strcmp(com.cmd, "mkdir")) {
    // falta tratamento de erros
    vfs_mkdir(com.argv[1]);
  } else if (!strcmp(com.cmd, "cd")) {
    // falta tratamento de erros
    vfs_cd(com.argv[1]);
  } else if (!strcmp(com.cmd, "pwd")) {
    // falta tratamento de erros
    vfs_pwd();
  } else if (!strcmp(com.cmd, "rmdir")) {
    // falta tratamento de erros
    vfs_rmdir(com.argv[1]);
  } else if (!strcmp(com.cmd, "get")) {
    // falta tratamento de erros
    vfs_get(com.argv[1], com.argv[2]);
  } else if (!strcmp(com.cmd, "put")) {
    // falta tratamento de erros
    vfs_put(com.argv[1], com.argv[2]);
  } else if (!strcmp(com.cmd, "cat")) {
    // falta tratamento de erros
    vfs_cat(com.argv[1]);
  } else if (!strcmp(com.cmd, "cp")) {
    // falta tratamento de erros
    vfs_cp(com.argv[1], com.argv[2]);
  } else if (!strcmp(com.cmd, "mv")) {
    // falta tratamento de erros
    vfs_mv(com.argv[1], com.argv[2]);
  } else if (!strcmp(com.cmd, "rm")) {
    // falta tratamento de erros
    vfs_rm(com.argv[1]);
  } else
  printf("ERROR(input: command not found)\n");
  return;
}

int get_free_block() {
  int nblock = -1;
  if(sb->n_free_blocks > 0) {
    nblock = sb->free_block;
    sb->free_block = fat[sb->free_block];
    fat[nblock] = -1;
    sb->n_free_blocks--;
    return nblock;
  }

  fprintf(stderr, "No more free blocks to alloc data.");
  return nblock;
}

// ls - lista o conte�do do direct�rio actual
void vfs_ls(void) {
  dir_entry *dir;
  int n_entradas, i;
  char typeP[5];

  dir = (dir_entry *) BLOCK(current_dir);

  n_entradas = dir[0].size;

  for (i = 0; i < n_entradas; i++) {
    if(dir[i].type == TYPE_DIR) strcpy(typeP, "DIR");
    else strcpy(typeP, "FILE");

    printf("%s\t %d-%s-%d [%s|%d]\n", dir[i].name, dir[i].day, mon_name[dir[i].month-1], 1900 + dir[i].year, typeP, dir[i].size);
  }
  return;
}


// mkdir dir - cria um subdirect�rio com nome dir no direct�rio actual
void vfs_mkdir(char *nome_dir) {
  int i, n_entradas, freeblock, pos;
  dir_entry *dir = (dir_entry *) BLOCK(current_dir);

  if(strlen(nome_dir) > MAX_NAME_LENGHT) { fprintf(stderr, "Directory name exceeded max limit of %d characters.\n", MAX_NAME_LENGHT); return; }

  n_entradas = dir[0].size;
  for(i = 0; i < n_entradas; i++){
    if(strcmp(dir[i].name, nome_dir) == 0) { fprintf(stderr, "There is already a folder with that name.\n"); return; }
  }

  if(n_entradas == DIR_ENTRIES_PER_BLOCK) { fprintf(stderr, "Directory has no more blocks available.\n"); return; }

  freeblock = get_free_block();
  pos = dir[0].size;
  init_dir_block(freeblock, current_dir);
  init_dir_entry(&dir[pos], TYPE_DIR, nome_dir, 0, freeblock);
  dir[0].size++;
  return;
}


// cd dir - move o direct�rio actual para dir.
void vfs_cd(char *nome_dir) {
  dir_entry *dir;
  dir = (dir_entry *) BLOCK(current_dir);
  int n_entradas = dir[0].size, i;

  for(i = 0; i < n_entradas; i++) {
    if(strcmp(dir[i].name, nome_dir) == 0 && dir[i].type == TYPE_DIR) { current_dir = dir[i].first_block; return; }
  }

  fprintf(stderr, "No directory with that name.\n");
  return;
}

void pwd_aux(int actual, int parent){
  dir_entry *dir;
  dir = (dir_entry *) BLOCK(parent);

  if(actual == sb->root_block) { printf("/"); return; }

  int n_entradas = dir[0].size, i;

  for(i = 0; i < n_entradas; i++){
    if(dir[i].first_block == actual) break;
  }

  pwd_aux(parent, dir[1].first_block);
  printf("%s/", dir[i].name);

  return;
}

// pwd - escreve o caminho absoluto do directório actual
void vfs_pwd(void) {
  dir_entry *dir;
  dir = (dir_entry *) BLOCK(current_dir);

  pwd_aux(dir[0].first_block, dir[1].first_block);
  putchar('\n');

  return;
}

void free_block(int x){
  fat[x] = sb->free_block;
  sb->n_free_blocks++;
  sb->free_block = x;
}

// rmdir dir - remove o subdirect�rio dir (se vazio) do direct�rio actual
void vfs_rmdir(char *nome_dir) {
  dir_entry *dir;
  dir = (dir_entry *) BLOCK(current_dir);
  int i, n_entradas = dir[0].size;

  for( i = 0; i < n_entradas; i++){
    if(strcmp(nome_dir, dir[i].name) == 0 && dir[i].type == TYPE_DIR) break;
  }

  if(strcmp(dir[i].name, "..") == 0 || strcmp(dir[i].name, ".") == 0) { fprintf(stderr, "Cannot remove directory.\n"); return; }
  else if(i == n_entradas) { fprintf(stderr, "Directory was not found.\n"); return; }

  free_block(dir[i].first_block);
  dir[i] = dir[n_entradas-1];
  dir[0].size--;

  return;
}


// get fich1 fich2 - copia um ficheiro normal UNIX fich1 para um ficheiro no nosso sistema fich2
void vfs_get(char *nome_orig, char *nome_dest) {
  dir_entry *dir = (dir_entry *) BLOCK(current_dir);
  int n_entries = dir[0].size;

  struct stat statbuf;
  if (stat(nome_orig, &statbuf) == -1) { printf("ERROR(get: input file not found)\n"); return; }

  int req_size = (int)statbuf.st_size;
  int req_blocks = (n_entries % DIR_ENTRIES_PER_BLOCK == 0) + (req_size + sb->block_size - 1) / sb->block_size;

  if (sb->n_free_blocks < req_blocks) { printf("ERROR(get: memory full)\n"); return; }

  req_blocks -= (n_entries % DIR_ENTRIES_PER_BLOCK == 0);

  dir[0].size++;

  int first_block = get_free_block();
  int new_block, next_block = first_block;
  int finput = open(nome_orig, O_RDONLY), count_block = 1, n;
  char msg[4200];
  while ((n = read(finput, msg, sb->block_size)) > 0) {
    if (count_block != req_blocks) {
      count_block++;
      new_block = get_free_block();
      fat[next_block] = new_block;
    }

    strcpy(BLOCK(next_block), msg);
    next_block = new_block;
  }

  int cur_block = current_dir;
  while (fat[cur_block] != -1)
  cur_block = fat[cur_block];

  if (n_entries % DIR_ENTRIES_PER_BLOCK == 0) {
    int next_block = get_free_block();
    fat[cur_block] = next_block;
    cur_block = next_block;
  }

  dir = (dir_entry *) BLOCK(cur_block);
  init_dir_entry(&dir[n_entries % DIR_ENTRIES_PER_BLOCK], TYPE_FILE, nome_dest, req_size, first_block);

  return;
}

// put fich1 fich2 - copia um ficheiro do nosso sistema fich1 para um ficheiro normal UNIX fich2
void vfs_put(char *nome_orig, char *nome_dest) {
  dir_entry *dir = (dir_entry *) BLOCK(current_dir);
  int n_entries = dir[0].size, i;

  int cur_block = current_dir;
  for (i = 0; i < n_entries; i++) {
    if (i % DIR_ENTRIES_PER_BLOCK == 0 && i) {
      cur_block = fat[cur_block];
      dir = (dir_entry *) BLOCK(cur_block);
    }

    int block_i = i % DIR_ENTRIES_PER_BLOCK;

    if (dir[block_i].type == TYPE_FILE && strcmp(dir[block_i].name, nome_orig) == 0) {
      int foutput = open(nome_dest, O_CREAT|O_TRUNC|O_WRONLY, 0644);
      int cur = dir[block_i].first_block;

      write(foutput, BLOCK(cur), sb->block_size);
      while (fat[cur] != -1) {
        cur = fat[cur];
        write(foutput, BLOCK(cur), sb->block_size);
      }

      return;
    }
  }

  printf("ERROR(put: file not found)\n");

  return;
}


// cat fich - escreve para o ecr� o conte�do do ficheiro fich
void vfs_cat(char *nome_fich) {
  dir_entry *dir = (dir_entry *) BLOCK(current_dir);
  int n_entries = dir[0].size, i;

  int cur_block = current_dir;
  for (i = 0; i < n_entries; i++) {
    if (i % DIR_ENTRIES_PER_BLOCK == 0 && i) {
      cur_block = fat[cur_block];
      dir = (dir_entry *) BLOCK(cur_block);
    }

    int block_i = i % DIR_ENTRIES_PER_BLOCK;

    if (dir[block_i].type == TYPE_FILE && strcmp(dir[block_i].name, nome_fich) == 0) {
      int next_block = dir[block_i].first_block;
      write(1, BLOCK(next_block), sb->block_size);

      while (fat[next_block] != -1) {
        next_block = fat[next_block];

        int write_size = sb->block_size;
        if (fat[next_block] == -1)
        write_size = dir[block_i].size % sb->block_size;

        write(1, BLOCK(next_block), write_size);
      }

      return;
    }
  }

  printf("ERROR(cat: file not found)\n");

  return;
}


// cp fich1 fich2 - copia o ficheiro fich1 para fich2
// cp fich dir - copia o ficheiro fich para o subdirect�rio dir
void vfs_cp(char *nome_orig, char *nome_dest) {
  dir_entry *dir = (dir_entry *) BLOCK(current_dir);
  int n_entries = dir[0].size, i, inp_block = -1, exp_dir = current_dir;

  int block_i;
  int cur_block = current_dir;
  for (i = 0; i < n_entries; i++) {
    if (i % DIR_ENTRIES_PER_BLOCK == 0 && i) {
      cur_block = fat[cur_block];
      dir = (dir_entry *) BLOCK(cur_block);
    }

    block_i = i % DIR_ENTRIES_PER_BLOCK;

    if (strcmp(dir[block_i].name, nome_orig) == 0) {
      inp_block = dir[block_i].first_block;
      break;
    }
  }

  if (inp_block == -1) { printf("ERROR(cp: input file not found)\n"); return; }

  int req_size = dir[block_i].size;

  dir = (dir_entry *) BLOCK(current_dir);
  cur_block = current_dir;
  for (i = 0; i < n_entries; i++) {
    if (i % DIR_ENTRIES_PER_BLOCK == 0 && i) {
      cur_block = fat[cur_block];
      dir = (dir_entry *) BLOCK(cur_block);
    }

    block_i = i % DIR_ENTRIES_PER_BLOCK;

    if (strcmp(dir[block_i].name, nome_dest) == 0) {
      if (dir[block_i].type == TYPE_DIR) {
        exp_dir = dir[block_i].first_block;
        strcpy(nome_dest, nome_orig);
      }
      else vfs_rm(nome_dest);
      break;
    }
  }

  dir_entry *cur_dir = (dir_entry *) BLOCK(exp_dir);
  n_entries = cur_dir[0].size;
  int req_blocks = (n_entries % DIR_ENTRIES_PER_BLOCK == 0) + (req_size + sb->block_size - 1) / sb->block_size;

  if (sb->n_free_blocks < req_blocks)
  {
    printf("ERROR(cp: memory full)\n");
    return;
  }

  req_blocks -= (n_entries % DIR_ENTRIES_PER_BLOCK == 0);

  cur_dir[0].size++;

  int first_block = get_free_block();
  int new_block, next_block = first_block;
  int count_block = 1, cur = inp_block;

  strcpy(BLOCK(next_block), BLOCK(cur));
  while (fat[cur] != -1)
  {
    if (count_block != req_blocks)
    {
      count_block++;
      new_block = get_free_block();
      fat[next_block] = new_block;
    }

    cur = fat[cur];
    strcpy(BLOCK(next_block), BLOCK(cur));

    next_block = new_block;
  }

  cur_block = exp_dir;
  while (fat[cur_block] != -1)
  cur_block = fat[cur_block];

  if (n_entries % DIR_ENTRIES_PER_BLOCK == 0)
  {
    int next_block = get_free_block();
    fat[cur_block] = next_block;
    cur_block = next_block;
  }

  dir = (dir_entry *) BLOCK(cur_block);
  init_dir_entry(&dir[n_entries % DIR_ENTRIES_PER_BLOCK], TYPE_FILE, nome_dest, req_size, first_block);


  return;
}


// mv fich1 fich2 - move o ficheiro fich1 para fich2
// mv fich dir - move o ficheiro fich para o subdirect�rio dir
void vfs_mv(char *nome_orig, char *nome_dest) {
  dir_entry *dir = (dir_entry *) BLOCK(current_dir);
  int n_entries = dir[0].size, i, inp_block = -1, exp_dir = current_dir, req_size = -1;

  int block_i;
  int cur_block = current_dir;
  for (i = 0; i < n_entries; i++) {
    if (i % DIR_ENTRIES_PER_BLOCK == 0 && i) {
      cur_block = fat[cur_block];
      dir = (dir_entry *) BLOCK(cur_block);
    }

    block_i = i % DIR_ENTRIES_PER_BLOCK;

    if (strcmp(dir[block_i].name, nome_orig) == 0) {
      int last_block = cur_block;
      while (fat[last_block] != -1)
      last_block = fat[last_block];
      dir_entry *last_dir_block = (dir_entry *) BLOCK(last_block);
      dir_entry last_dir = last_dir_block[(n_entries - 1 + DIR_ENTRIES_PER_BLOCK) % DIR_ENTRIES_PER_BLOCK];

      if ((n_entries - 1 + DIR_ENTRIES_PER_BLOCK) % DIR_ENTRIES_PER_BLOCK == 0)
      free_block(last_block);

      req_size = dir[block_i].size;

      dir[block_i].type = last_dir.type;
      strcpy(dir[block_i].name, last_dir.name);
      dir[block_i].day = last_dir.day;
      dir[block_i].month = last_dir.month;
      dir[block_i].year = last_dir.year;
      dir[block_i].size = last_dir.size;
      dir[block_i].first_block = last_dir.first_block;

      dir = (dir_entry *) BLOCK(current_dir);
      dir[0].size--;

      inp_block = dir[block_i].first_block;
      break;
    }
  }

  if (inp_block == -1) {
    printf("ERROR(mv: input file not found)\n");
    return;
  }

  dir = (dir_entry *) BLOCK(current_dir);
  cur_block = current_dir;
  for (i = 0; i < n_entries; i++) {
    if (i % DIR_ENTRIES_PER_BLOCK == 0 && i) {
      cur_block = fat[cur_block];
      dir = (dir_entry *) BLOCK(cur_block);
    }

    block_i = i % DIR_ENTRIES_PER_BLOCK;

    if (strcmp(dir[block_i].name, nome_dest) == 0) {
      if (dir[block_i].type == TYPE_DIR) {
        exp_dir = dir[block_i].first_block;
        strcpy(nome_dest, nome_orig);
      }
      else
      vfs_rm(nome_dest);

      break;
    }
  }

  dir_entry *cur_dir = (dir_entry *) BLOCK(exp_dir);
  n_entries = cur_dir[0].size;
  cur_dir[0].size++;

  cur_block = exp_dir;
  while (fat[cur_block] != -1)
  cur_block = fat[cur_block];

  if (n_entries % DIR_ENTRIES_PER_BLOCK == 0) {
    int next_block = get_free_block();
    fat[cur_block] = next_block;
    cur_block = next_block;
  }

  dir = (dir_entry *) BLOCK(cur_block);
  init_dir_entry(&dir[n_entries % DIR_ENTRIES_PER_BLOCK], TYPE_FILE, nome_dest, req_size, inp_block);

  return;
}


// rm fich - remove o ficheiro fich
void vfs_rm(char *nome_fich) {
  dir_entry *dir = (dir_entry *) BLOCK(current_dir);
  int n_entries = dir[0].size, i;

  int cur_block = current_dir;
  for (i = 0; i < n_entries; i++){
    if (i % DIR_ENTRIES_PER_BLOCK == 0 && i){
      cur_block = fat[cur_block];
      dir = (dir_entry *) BLOCK(cur_block);
    }

    int block_i = i % DIR_ENTRIES_PER_BLOCK;

    if (dir[block_i].type == TYPE_FILE && strcmp(dir[block_i].name, nome_fich) == 0) {
      int next_block = dir[block_i].first_block, count = 1;

      while (fat[next_block] != -1) {
        next_block = fat[next_block];
        count++;
      }

      sb->n_free_blocks += count;
      fat[next_block] = sb->free_block;
      sb->free_block = dir[block_i].first_block;

      int last_block = cur_block;
      while (fat[last_block] != -1)
      last_block = fat[last_block];
      dir_entry *last_dir_block = (dir_entry *) BLOCK(last_block);
      dir_entry last_dir = last_dir_block[(n_entries - 1 + DIR_ENTRIES_PER_BLOCK) % DIR_ENTRIES_PER_BLOCK];

      if ((n_entries - 1 + DIR_ENTRIES_PER_BLOCK) % DIR_ENTRIES_PER_BLOCK == 0)
      free_block(last_block);

      dir[block_i].type = last_dir.type;
      strcpy(dir[block_i].name, last_dir.name);
      dir[block_i].day = last_dir.day;
      dir[block_i].month = last_dir.month;
      dir[block_i].year = last_dir.year;
      dir[block_i].size = last_dir.size;
      dir[block_i].first_block = last_dir.first_block;

      dir = (dir_entry *) BLOCK(current_dir);
      dir[0].size--;

      return;
    }
  }

  printf("ERROR(rm: file not found)\n");
  return;
}
