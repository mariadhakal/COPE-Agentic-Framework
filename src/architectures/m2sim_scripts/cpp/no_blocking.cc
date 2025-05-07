#include <iostream>
#include <fstream>
#include <ctime>
#include <cstdlib>

#include "mat-mat.hh"

using namespace std;

// This function multiplies mat1[][] and mat2[][], and stores the result in res[][]
void multiply(int **mat1, int **mat2, int **res, int N) {
    int i, j, k;
    for (i = 0; i < N; i++) {
        for (j = 0; j < N; j++) { 
            res[i][j] = 0;
            for (k = 0; k < N; k++)
                res[i][j] += mat1[i][k] * mat2[k][j];
        }
    }
}

// Driver Code
int main(int argc, char * argv[]) {
    if (argc != 1) {
        cout << "Usage: " << argv[0] << endl;
        return -1;
    }
    int **res = new int*[N]; // To store result
    int **mat1 = new int*[N]; // To store result
    int **mat2 = new int*[N]; // To store result
    for(int i = 0; i < N; i++) {
        res[i]= new int[N];
        mat1[i]= new int[N];
        mat2[i]= new int[N];
        for(int j = 0; j < N; j++) {
            res[i][j] = 0;
            mat1[i][j] = matrices[2 * i * N + 2 * j];
            mat2[i][j] = matrices[2 * i * N + 2 * j + 1];
        }
    }
    cout << "[INFO] Done loading data." << endl;
    multiply(mat1, mat2, res, N);

    cout << "[INFO] Computation is complete!" << endl;
    return 0;
}
