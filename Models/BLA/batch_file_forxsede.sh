#!/bin/bash

#SBATCH --partition normal
#SBATCH --nodes=30
#SBATCH -A TG-CCR140046
#SBATCH --ntasks-per-node=20
#SBATCH --cpus-per-task=1

#SBATCH --time 0-03:00
#SBATCH --qos=normal
#SBATCH --job-name=CE_HOC_AUTO
#SBATCH --output=results-BLA-auto-%j.out

mpirun nrniv -mpi BLA_main_Drew_reordingimem_simplify_big_saveLFPimem_noDANE_extrinsic_XSEDE_vecstim_invivo_multielec.hoc