/**
 * forktest.c
 */

#include <unistd.h>
#include <stdio.h>
#include <Profile/Profiler.h>


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
    TAU_REGISTER_FORK(1, TAU_EXCLUDE_PARENT_DATA);
    child();
  }
  return 0;
}
