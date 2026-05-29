from mpi4py import MPI
import numpy as np
import math
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Configuração do vetor global (apenas no processo ROOT)
N = 100000000
vetor_global = None

if rank == 0:
    # Cria um vetor com números de 1 a 100 (Soma esperada = 5050)
    vetor_global = np.arange(1, N + 1, dtype=int)
    print(f"[ROOT] Iniciando processamento com {size} processos.", flush=True)

# --- DISTRIBUIÇÃO DOS DADOS (Scatter) ---
# Calcula o tamanho do pedaço de cada processo
local_n = N // size
resto = N % size

# Vetor local que armazenará o pedaço de cada processo
if rank < resto:
    local_size = local_n + 1
    start_idx = rank * local_size
else:
    local_size = local_n
    start_idx = rank * local_size + resto

end_idx = start_idx + local_size

# Distribuição manual via fatiamento para suportar qualquer tamanho de vetor
vetor_local = None
if rank == 0:
    for i in range(1, size):
        i_local_n = local_n + (1 if i < resto else 0)
        i_start = i * i_local_n + (0 if i < resto else resto)
        if i >= resto:
            i_start = i * local_n + resto
        comm.send(vetor_global[i_start:i_start+i_local_n], dest=i)
    vetor_local = vetor_global[start_idx:end_idx]
else:
    vetor_local = comm.recv(source=0)

# Cada processo calcula sua soma local inicial
soma_local = int(np.sum(vetor_local))

# Sincronização para iniciar os testes de tempo de forma justa
comm.Barrier()

# ==========================================
# ESTRATÉGIA 1: Naive (Root centraliza tudo)
# ==========================================
t_start_naive = time.perf_counter()

if rank == 0:
    soma_final_naive = soma_local
    for i in range(1, size):
        parcial = comm.recv(source=i, tag=11)
        soma_final_naive += parcial
else:
    comm.send(soma_local, dest=0, tag=11)

comm.Barrier()
if rank == 0:
  t_end_naive = time.perf_counter()
  tempo_naive = t_end_naive - t_start_naive


# ==========================================
# ESTRATÉGIA 2: Árvore Binária
# ==========================================
comm.Barrier()
t_start_tree = time.perf_counter()

soma_arvore = soma_local
passos = int(math.log2(size))

# Loop baseado em divisões sucessivas por 2 (log2)
for passo in range(passos):
    divisor = 2 ** (passo + 1)
    sub_passo = 2 ** passo

    # Verifica se o processo é o acumulador (par no nível atual) ou o emissor (ímpar)
    if rank % divisor == 0:
        # Nó receptor recebe do seu par da direita (rank + sub_passo)
        origem = rank + sub_passo
        if origem < size:
            parcial_recebida = comm.recv(source=origem, tag=22)
            soma_arvore += parcial_recebida
    elif rank % sub_passo == 0:
        # Nó emissor envia para o seu acumulador da esquerda (rank - sub_passo)
        destino = rank - sub_passo
        comm.send(soma_arvore, dest=destino, tag=22)
        # Uma vez que enviou, o nó sai da árvore de computação nas próximas iterações
        break

comm.Barrier()
if rank == 0:
    t_end_tree = time.perf_counter()
    tempo_tree = t_end_tree - t_start_tree

    # Exibição dos Resultados Consolidados
    print("\n" + "="*40)
    print("      RESULTADOS COMPARTILHADOS", flush=True)
    print("="*40)
    print(f"Estratégia 1 (Naive):  Soma = {soma_final_naive} | Tempo = {tempo_naive:.7f}s", flush=True)
    print(f"Estratégia 2 (Árvore): Soma = {soma_arvore} | Tempo = {tempo_tree:.7f}s", flush=True)
    print("="*40)
