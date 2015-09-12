#include <stdio.h>
#include <stdlib.h>
#include <readline/readline.h>
#include <readline/history.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <assert.h>

#define MAXARGS 100
#define PIPE_READ 0
#define PIPE_WRITE 1

/* As cores standard que podemos utilizar */
#define ANSI_COLOR_RED     "\x1b[31m"
#define ANSI_COLOR_GREEN   "\x1b[32m"
#define ANSI_COLOR_YELLOW  "\x1b[33m"
#define ANSI_COLOR_BLUE    "\x1b[34m"
#define ANSI_COLOR_MAGENTA "\x1b[35m"
#define ANSI_COLOR_CYAN    "\x1b[36m"
#define ANSI_COLOR_RESET   "\x1b[0m"

typedef struct command {
  char *cmd;              // string apenas com o comando
  int argc;               // número de argumentos
  char *argv[MAXARGS+1];  // vector de argumentos do comando
  struct command *next;   // apontador para o próximo comando
} COMMAND;

// variáveis globais
char* inputfile = NULL;	    // nome de ficheiro (em caso de redireccionamento da entrada padrão)
char* outputfile = NULL;    // nome de ficheiro (em caso de redireccionamento da saída padrão)
int background_exec = 0;    // indicação de execução concorrente com a mini-shell (0/1)

// declaração de funções
COMMAND* parse(char* linha);
void print_parse(COMMAND* commlist);
void execute_commands(COMMAND* commlist);
void free_commlist(COMMAND* commlist);
void child_handler(int sig);

// include do código do parser da linha de comandos
#include "parser.c"

int main(int argc, char* argv[]) {
  char *linha;
  COMMAND *com;

  while (1) {
    if ((linha = readline(ANSI_COLOR_RED "Chuck Norris Shell $ " ANSI_COLOR_RESET)) == NULL)
      exit(0);
    if (strlen(linha) != 0) {
      if(strcmp(linha, "exit") == 0) exit(0);
      add_history(linha);
      com = parse(linha);
      if (com) {
        print_parse(com);
        execute_commands(com);
        free_commlist(com);
      }
    }
    free(linha);
    inputfile = NULL;
    outputfile = NULL;
  }
  return 0;
}

void print_parse(COMMAND* commlist) {
  int n, i;

  printf("---------------------------------------------------------\n");
  printf("BG: %d IN: %s OUT: %s\n", background_exec, inputfile, outputfile);
  n = 1;
  while (commlist != NULL) {
    printf("#%d: cmd '%s' argc '%d' argv[] '", n, commlist->cmd, commlist->argc);
    i = 0;
    while (commlist->argv[i] != NULL) {
      printf("%s,", commlist->argv[i]);
      i++;
    }
    printf("%s'\n", commlist->argv[i]);
    commlist = commlist->next;
    n++;
  }
  printf("---------------------------------------------------------\n");
}

void free_commlist(COMMAND *commlist){
  COMMAND *temp;
  while(commlist){
    temp = commlist;
    free(commlist);
    commlist = temp->next;
  }
  /*
  * Necessário para quando se utiliza & na linha de comandos mas nao se quer guardar para a proxima iteração
  */
  background_exec = 0;
}

void execute_commands(COMMAND *commlist) {
  int prevRead = -1, fd[2];
  pid_t last_pid = 0;

  COMMAND *temp = commlist;

  while(temp){

    if(temp->next) if( pipe(fd) == -1 ) { perror("Error creating pipe!"); exit(1); }

    pid_t pid = fork();

    if(pid < 0) { perror("Error forking"); exit(1); }

    if( pid == 0 ) {

      if(temp == commlist) {
        if(inputfile) {
          int in = open(inputfile, O_RDONLY);
          if(in < 0) { perror("Error opening file"); exit(1); }
          prevRead = in;
        }
        else prevRead = PIPE_READ;
      }

      dup2(prevRead, PIPE_READ);

      if(temp->next) {
        dup2(fd[PIPE_WRITE], PIPE_WRITE);
      }
      else {
        if(outputfile) {
          int out = open(outputfile, O_WRONLY | O_CREAT | O_TRUNC, 0644);
          if(out < 0) { perror("Error creating file"); exit(1); }
          dup2(out, PIPE_WRITE);
        }
      }

      if(execvp(temp->cmd, temp->argv) < 0) exit(1);
    }
    else {
      if(temp->next) {
        close(fd[PIPE_WRITE]);
        close(prevRead);
        prevRead = fd[PIPE_READ];
      }
      else last_pid = pid;
    }
    temp = temp->next;
  }
  if (!background_exec)
    waitpid(last_pid, NULL, 0);
}
