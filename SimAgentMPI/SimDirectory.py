# -*- coding: utf-8 -*-
"""
Created on Sun May 20 16:46:40 2018

@author: Tyler
"""

"""
Directory structure
    Project
        |
        = SimAgentResults
            |
            = Project-NameOfJob  (Jobs can have names or random numbers)
            = Project-RandNumber
                |
                = extracted_results_zip
                - .properties            (Properties of the job to be stored, like status)
                - .logfile               (log to be displayed on main console)
                - .notes                 (notes that can be edited from the main console)
                - initial_snapshot.zip
                - results.zip
                 
"""

from SimAgentMPI.SimJob import SimJob
import os,errno
import zipfile
import json
import shutil
from tkinter import messagebox
from pathlib import Path


class SimDirectory(object):
    results_folder_name = "SimAgentResults"
    properties_file = "dir.properties"
    version = "1.0"
     
    def __init__(self, directory, initialize=False):
        self.sim_directory = directory
        self.sim_directory_relative = os.path.basename(self.sim_directory)
        self.sim_jobs = []
        
        self.sim_results_dir = os.path.join(self.sim_directory, SimDirectory.results_folder_name)
        
        self.propname_version = "version"
        self.propname_custom_tool = "custom_tool"
        self.propname_update_enabled = "update_enabled"
        self.propname_update_interval = "update_interval_seconds"
        
        self.version_num = SimDirectory.version
        self.custom_tool = ""     
        self.update_enabled = "1"
        self.update_interval_seconds = 60
        
        
        self.full_properties_path = os.path.join(self.sim_results_dir,SimDirectory.properties_file)
        
        """ DETECTION """
        #Determine what files are present in the directory
                
        #If the directory isn't there we want to create it, can check with is_valid.. by callers
        if(not os.path.isdir(self.sim_results_dir)):
            self.is_valid_sim_directory = False
            if(initialize):
                if(messagebox.askquestion("", "SimAgent has not used this directory before. Do you want to initialize it? This will create an empty folder named "+SimDirectory.results_folder_name+" to store results in.", icon='warning') == 'yes'):
                    self.initialize()
            else:
                return
        
        """ CREATE JOBS """
        #Grab all the data we need
        
        results_dir_files = os.listdir(self.sim_results_dir)
        results_dir_folder_names = []
        for file in results_dir_files:
            if(os.path.isdir(os.path.join(self.sim_results_dir,file))):
                results_dir_folder_names.append(file)
        
        #Initialize all jobs
        for job_folder in results_dir_folder_names:
            try:
                self.add_new_job(SimJob(self, os.path.join(self.sim_results_dir, job_folder)))
            except Exception as e:
                messagebox.showinfo("Load Error","Could not load simjob " + job_folder + ". See the console for info. Continuing...")
                print(e)
        
        self.read_properties()
        
        return
    
    def initialize(self):
        try:
            os.makedirs(self.sim_results_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        self.write_properties()
        self.is_valid_sim_directory = True
        
        return
    
    def zipdir(self, path, ziph, foldername):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                dir_ = root.split(self.sim_directory_relative, 1)[-1]
                if(len(dir_) and dir_[0] == "\\"):
                    dir_ = dir_[1:]
                if(dir_.startswith(SimDirectory.results_folder_name) or dir_.startswith(".git")):#only want files in root dir and not results
                    continue
                #print(os.path.join(self.sim_directory_relative,dir_,file))
                ziph.write(os.path.join(root, file), arcname=os.path.join(foldername,dir_,file))
        return
    
    def delete_job(self, job):
        shutil.rmtree(job.job_directory_absolute)
        self.sim_jobs.remove(job)
        return
    
    def take_snapshotzip(self, save_to_file):
        #Zip up everything except results foldername
        zipf = zipfile.ZipFile(save_to_file+".zip", 'w', zipfile.ZIP_DEFLATED)
        dir_path = self.sim_directory
        self.zipdir(dir_path, zipf, foldername=os.path.basename(save_to_file)) #must be in format file.zip -> file (folder) -> sim stuff
        zipf.close()
        return
    
    def add_new_job(self,simjob):
        self.sim_jobs.append(simjob)
        return
    
    def get_job(self, job_name):
        for job in self.sim_jobs:
            if job.sim_name == job_name:
                return job
        return None
        
    def read_properties(self):
        if(os.path.isfile(self.full_properties_path)):
            with open(self.full_properties_path) as json_file:  
                data = json.load(json_file)
                self.custom_tool = data[self.propname_custom_tool] 
                self.version_num = data[self.propname_version]
                self.update_enabled = data[self.propname_update_enabled]
                self.update_interval_seconds = data[self.propname_update_interval]
        return

    def write_properties(self):
        data = {}
        data[self.propname_custom_tool] = self.custom_tool      
        data[self.propname_version] = self.version_num
        data[self.propname_update_enabled] = self.update_enabled
        data[self.propname_update_interval] = self.update_interval_seconds
        with open(self.full_properties_path, 'w') as outfile:  
            json.dump(data, outfile)
            
        return
    
    def is_update_enabled(self):
        self.read_properties()
        if self.update_enabled == "1":
            return True
        else:
            return False
        
    def set_update_enabled(self, val):
        if val:
            self.update_enabled = "1"
        else:
            self.update_enabled = "0"
        self.write_properties()
    
    def add_results_to_gitignore(self):
        gitignore = ".gitignore"
        gitignore_file = os.path.join(self.sim_directory,gitignore)
        gi = Path(gitignore_file)
        if not gi.is_file():
            open(gitignore_file, 'a').close()
            
        if not SimDirectory.results_folder_name in open(gitignore_file).read():
            f = open(gitignore_file, 'a')
            f.write("\n" + SimDirectory.results_folder_name + "/\n")
            f.close()
            
        return
    
"""    
def test():
    directory = "C:\\Users\\Tyler\\Desktop\\git_stage\\Sample_Model"
    sd = SimDirectory(directory, None, initialize=True)    
    #sd.take_snapshotzip("C:\\Users\\Tyler\\Desktop\\git_stage\\Sample_Model\\SimAgentResults\\Sample_Model-00538\\snapshott.zip")
    
test()
"""
    