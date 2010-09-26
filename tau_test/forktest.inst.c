#include <Profile/Profiler.h>
/**
 * forktest.c
 */

#include <unistd.h>


void parent() {

	TAU_PROFILE_TIMER(tautimer, "void parent() C [{forktest.c} {8,1}-{10,1}]", " ", TAU_USER);
	TAU_PROFILE_START(tautimer);

{
  printf("Parent\n");

}
	
	TAU_PROFILE_STOP(tautimer);

}

void child() {

	TAU_PROFILE_TIMER(tautimer, "void child() C [{forktest.c} {12,1}-{14,1}]", " ", TAU_USER);
	TAU_PROFILE_START(tautimer);

{
  printf("Child\n");

}
	
	TAU_PROFILE_STOP(tautimer);

}

int main(int argc, char **argv) {

	TAU_PROFILE_TIMER(tautimer, "int main(int, char **) C [{forktest.c} {16,1}-{25,1}]", " ", TAU_DEFAULT);
  TAU_INIT(&argc, &argv); 
#ifndef TAU_MPI
#ifndef TAU_SHMEM
  TAU_PROFILE_SET_NODE(0);
#endif /* TAU_SHMEM */
#endif /* TAU_MPI */
	TAU_PROFILE_START(tautimer);

{
  pid_t pid;
  pid = fork();
  if (pid) { /* parent */
    parent();
  } else { /* child */
    child();
  }
  { int tau_ret_val =  0;  TAU_PROFILE_STOP(tautimer); return (tau_ret_val); }


}
	
	TAU_PROFILE_STOP(tautimer);

}
