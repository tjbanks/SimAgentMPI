#! /bin/bash

#--------------------------this------------------------------------------------
#  SBATCH CONFIG
#  https://slurm.schedmd.com/sbatch.html
#  Generated by SimAgentMPI
#  Remove the first # to use the field
#--------------------------------------------------------------------------------

#SBATCH --job-name=Neuron-Code # (-J) Job's custom name
#SBATCH --partition=General # (-p) Uses the General partition
#SBATCH --nodes=2 # (-N) Number of nodes
#SBATCH --ntasks=1 # (-n) Number of codes (tasks)
#SBATCH --time=0-2:00 # (-t) Maximum time limit for job run

##SBATCH --mem-per-cpu= # Memory allocated for each cpu
##SBATCH --ntasks-per-node= # Maximum ntasks be invoked on each node

#SBATCH --output=out%j.txt # (-o) Job output custom name
#SBATCH --error=err%j.txt # (-e) Job error custom name

##SBATCH --gres= # (name[[:type]:count) Comma delimited list of consumable resources
##SBATCH --licenses= # (-l) Licenses which must be allocated to this job, multiple = license:1,bar:1,...
##SBATCH --mail-user= # (-m) A valid user to email on mail-type events
#SBATCH --mail-type=END # Valid type values are NONE, BEGIN, END, FAIL, REQUEUE, ALL,STAGE_OUT,TIME_LIMIT_90(mail when 90% of time limit, 80...)


echo "### Starting at: $(date) ###"


module list

# Commands with srun prepended will run on all cores in the allocation
echo $(hostname)
srun echo $(hostname)


echo "### Ended at: $(date) ###"
