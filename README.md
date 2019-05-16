# SimAgentMPI

https://tjbanks.github.io/SimAgentMPI/

Sim Agent MPI is an easy to use tool that takes the difficulty of running Neuron HOC code or MPI/sbatch based jobs on supercomputers.
It currently supports connections to the NSG-R API and connections using SSH to servers running Slurm.

## Linux and Mac Users
Upon cloning this repository you will need to change to the linux branch. Linux has issues with the way .ico files are handled, causing the master branch to crash.
```
git clone https://github.com/tjbanks/SimAgentMPI
cd SimAgentMPI
git checkout linux
python SimAgentMPI.py
```
