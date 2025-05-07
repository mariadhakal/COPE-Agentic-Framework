#include <iostream>
#include <fstream>
#include <ctime>
#include <cstdlib>

#include "mat-mat.hh"

using namespace std;

// This function multiplies mat1[][] and mat2[][], and stores the result in res[][]
void blocking_multiply(int **mat1, int **mat2, int **res, int B, int N) {
    for (int ii = 0; ii < N; ii += B) {
        for (int jj = 0; jj < N; jj += B) {
            for (int kk = 0; kk < N; kk += B) {
                for (int i = ii; i < ii + B; i++) {
                    for (int j = jj; j < jj + B; j++) {
                        for (int k = kk; k < kk + B; k++) {
                            res[i][j] += mat1[i][k] * mat2[k][j];
                        }
                    }
                }
            }
        }
    }
}

// Driver Code
int main(int argc, char * argv[])
{
    int B = 1;
    if (argc != 2) {
        cout << "Usage: " << argv[0] << " <blocking_parameter>" << endl;
        return -1;
    }
    B = atoi(argv[1]);
    if (B <= 0) {
        cout << "[ERROR] Blocking parameter must be a positive integer." << endl;
        return -2;
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
    blocking_multiply(mat1, mat2, res, B, N);

    cout << "[INFO] Computation is complete!" << endl;
    return 0;
}
