#include <stdio.h>
#include <signal.h>
#include <semaphore.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/wait.h>

#define SEM_NAME "/mysem"
#define SEM_FLAGS S_IRUSR | S_IWUSR

int main(int argc, char** argv) {

  sem_t *sem;

  sem = sem_open(SEM_NAME, O_CREAT | O_EXCL, SEM_FLAGS, 0);

  pid_t pid = fork();

  if(pid == -1) { perror("Error forking"); return 1; }
  if(pid == 0) {
    sem_wait(sem);
    printf("Filho\n");
    sem_close(sem);
  }
  else {
    printf("Pai\n");
    sem_post(sem);
    sem_close(sem);
    sem_unlink(SEM_NAME);
    wait(0);
  }

  return 0;
}
