#!/bin/bash
#MV2_USE_CUDA=1 MV2_ENABLE_AFFINITY=0 MV2_SMP_USE_CMA=0
#SBATCH -p Pixel
#SBATCH --gres=gpu:1
#SBATCH --nodelist=HK-IDC2-10-1-75-58
#SBATCH --job-name=video2rgb
#SBATCH -o ./logs/%j.txt
srun --mpi=pmi2 sh video2rgb.sh
