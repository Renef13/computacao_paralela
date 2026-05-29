#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// No Colab, 10000x10000 de doubles consome cerca de 800MB de RAM.
#define MAX 10000

int main() {
    int i, j;
    struct timespec start, end;
    double time_row, time_col;

    // Alocação dinâmica para garantir que o Colab gerencie a memória no Heap
    double **A = (double **)malloc(MAX * sizeof(double *));
    for (i = 0; i < MAX; i++) A[i] = (double *)malloc(MAX * sizeof(double));
    double *x = (double *)malloc(MAX * sizeof(double));
    double *y = (double *)malloc(MAX * sizeof(double));

    // Inicialização dos dados
    for (i = 0; i < MAX; i++) {
        x[i] = i * 0.5;
        y[i] = 0;
        for (j = 0; j < MAX; j++) {
            A[i][j] = (i + j) * 0.1;
        }
    }

    printf("Iniciando testes com matriz %d x %d...\n\n", MAX, MAX);

    // --- FORMA 1: ACESSO POR LINHA (Eficiente / Cache Friendly) ---
    // Baseado no "First pair of loops" da image_765e51.jpg
    clock_gettime(CLOCK_MONOTONIC, &start);
    for (i = 0; i < MAX; i++) {
        for (j = 0; j < MAX; j++) {
            y[i] += A[i][j] * x[j];
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    time_row = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    printf("Tempo (Acesso por Linha - Sugerido): %f segundos\n", time_row);

    // Reset de y
    for (i = 0; i < MAX; i++) y[i] = 0;

    // --- FORMA 2: ACESSO POR COLUNA (Ineficiente / Cache Miss) ---
    // Baseado no "Second pair of loops" da image_765e51.jpg
    clock_gettime(CLOCK_MONOTONIC, &start);
    for (j = 0; j < MAX; j++) {
        for (i = 0; i < MAX; i++) {
            y[i] += A[i][j] * x[j];
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    time_col = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    printf("Tempo (Acesso por Coluna - Lento):     %f segundos\n", time_col);

    printf("\nO acesso por coluna foi %.2fx mais lento.\n", time_col / time_row);

    // Liberação de memória
    for (i = 0; i < MAX; i++) free(A[i]);
    free(A); free(x); free(y);

    return 0;
}
