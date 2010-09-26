#include <Profile/Profiler.h>
/**
 * threadtest.c
 */

#include <stdio.h>
#include <pthread.h>

void parent() {

	TAU_PROFILE_TIMER(tautimer, "void parent() C [{threadtest.c} {8,1}-{11,1}]", " ", TAU_USER);
	TAU_PROFILE_START(tautimer);

{
  sleep(4);
  printf("Parent\n");

}
	
	TAU_PROFILE_STOP(tautimer);

}

void child(void* args) {

	TAU_PROFILE_TIMER(tautimer, "void child(void *) C [{threadtest.c} {13,1}-{16,1}]", " ", TAU_USER);
	TAU_PROFILE_START(tautimer);

{
  sleep(6);
  printf("Child\n");

}
	
	TAU_PROFILE_STOP(tautimer);

}


int main(int argc, char **argv) {

	TAU_PROFILE_TIMER(tautimer, "int main(int, char **) C [{threadtest.c} {19,1}-{26,1}]", " ", TAU_DEFAULT);
  TAU_INIT(&argc, &argv); 
#ifndef TAU_MPI
#ifndef TAU_SHMEM
  TAU_PROFILE_SET_NODE(0);
#endif /* TAU_SHMEM */
#endif /* TAU_MPI */
	TAU_PROFILE_START(tautimer);

{
  pthread_t th;
  int tid;
  tid = pthread_create(&th, NULL, (void*)(child), NULL);
  parent();
  pthread_join(th, NULL);
  { int tau_ret_val =  0;  TAU_PROFILE_STOP(tautimer); return (tau_ret_val); }


}
	
	TAU_PROFILE_STOP(tautimer);

}
