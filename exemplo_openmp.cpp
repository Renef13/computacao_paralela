#include <iostream>
#include <omp.h>

int main() {
    // Define o número de threads (opcional, o padrão é o total de núcleos)
    omp_set_num_threads(4);

    #pragma omp parallel
    {
        int id = omp_get_thread_num();
        int total = omp_get_num_threads();
        printf("Olá da thread %d de um total de %d\n", id, total);
    }

    return 0;
}
