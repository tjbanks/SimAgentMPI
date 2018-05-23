# -*- coding: utf-8 -*-
"""
Created on Wed May 23 10:53:53 2018

@author: tjbanks
"""

from cx_Freeze import setup, Executable

base = None    

executables = [Executable("SimAgentMPI/main.py", base=base)]

packages = ["idna","time","re","subprocess","threading","tempfile","shutil","os","random","numpy","pandas","paramiko","zipfile","tkinter","tarfile"]
options = {
    'build_exe': {    
        'packages':packages,
    },    
}

setup(
    name = "SimAgentMPI",
    options = options,
    version = "1",
    description = 'SimAgentMPI Nair Lab (Banks)',
    executables = executables
)