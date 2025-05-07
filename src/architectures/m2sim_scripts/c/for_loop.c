#include <stdio.h>
#include <stdlib.h>

int factorial(int n){
    int result = 1;
	
    for(int i = 2; i <= n; i++)
		result *= i;

    return result;
}


int main(int argc, char* argv[]){

    int NUM_FACTS = 100;
    for(int i = 0; i < NUM_FACTS; i++)
		printf( "%d! is %d", i, factorial(i));

    return 0;
}