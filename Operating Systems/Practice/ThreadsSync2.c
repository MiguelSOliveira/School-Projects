#include <stdio.h>
#include <signal.h>
#include <semaphore.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/wait.h>

#define SEM_NAME "/mysem"
#define SEM_NAME2 "/mysem2"
#define SEM_FLAGS S_IRUSR | S_IWUSR

int main(int argc, char** argv) {
  sem_t *sem, *sem2;

  sem = sem_open(SEM_NAME, O_CREAT | O_EXCL, SEM_FLAGS, 1);
  sem2 = sem_open(SEM_NAME2, O_CREAT | O_EXCL, SEM_FLAGS, 0);

  int i = 0;

  pid_t pid = fork();

  if(pid == 0) {
    i = 1;
    while(i <= 20) {
      sem_wait(sem);
      printf("filho: %d\n", i);
      sem_post(sem2);
      i+=2;
    }
  }
  else {
    i = 2;
    while(i <= 20) {
      sem_wait(sem2);
      printf("Pai: %d\n", i);
      sem_post(sem);
      i+=2;
    }
  }
  sem_close(sem);
  sem_unlink(SEM_NAME);
  sem_close(sem2);
  sem_unlink(SEM_NAME2);
  return 0;
}
