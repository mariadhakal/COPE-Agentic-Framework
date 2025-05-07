#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <assert.h>
#include <sys/time.h>
#include <math.h>
#include <string.h>

// Driver Code
int main(int argc, char * argv[])
{
	 int accsum = 0*atoi(argv[1]);

	 for(int i = 0; i < 1000; i++){
		 accsum+=i;
	 }

    printf("Hello, World! %d", accsum);

    return 0;
}
