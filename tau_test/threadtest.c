/**
 * threadtest.c
 */

#include <stdio.h>
#include <pthread.h>

void parent() {
  sleep(4);
  printf("Parent\n");
}

void child(void* args) {
  sleep(6);
  printf("Child\n");
}


int main(int argc, char **argv) {
  pthread_t th;
  int tid;
  tid = pthread_create(&th, NULL, (void*)(child), NULL);
  parent();
  pthread_join(th, NULL);
  return 0;
}
