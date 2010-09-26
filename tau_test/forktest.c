/**
 * forktest.c
 */

#include <unistd.h>


void parent() {
  printf("Parent\n");
}

void child() {
  printf("Child\n");
}

int main(int argc, char **argv) {
  pid_t pid;
  pid = fork();
  if (pid) { /* parent */
    parent();
  } else { /* child */
    child();
  }
  return 0;
}
