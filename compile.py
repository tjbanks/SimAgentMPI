# -*- coding: utf-8 -*-
"""
Created on Wed May 23 10:53:53 2018

@author: tjbanks
"""

from cx_Freeze import setup, Executable

base = None    

executables = [Executable("SimAgentMPI.py", base=base)]

packages = ["idna","requests","time","re","subprocess","threading","tempfile","shutil","os","random","numpy","pandas","paramiko","zipfile","tkinter","tarfile","SimAgentMPI.MainWindow","SimAgentMPI.NewJobWindow","SimAgentMPI.NewServerConfig","SimAgentMPI.SimDirectory","SimAgentMPI.SimJob","SimAgentMPI.SimServer","SimAgentMPI.tktable","SimAgentMPI.Utils","SimAgentMPI.ParametricSweep","SimAgentMPI.nsg.nsgclient","SimAgentMPI.nsg.pyjavaproperties"]
folders = ['SimAgentMPI/']
options = {
    'build_exe': {    
        'packages':packages,
        'include_files':folders
    },    
}

setup(
    name = "SimAgentMPI",
    options = options,
    version = "1",
    description = 'SimAgentMPI Nair Lab (Tyler Banks)',
    executables = executables
)