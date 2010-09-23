/**
 * profcheck.c
 */

#include <stdlib.h>

void f() {
  sleep(1);
}

void g() {
  sleep(2);
}

int main(int argc, char **argv) {
  int i;
  int N = 20;
  for (i = 0; i < N; i++) {
    f();
    g();
  }
  return 0;
}

