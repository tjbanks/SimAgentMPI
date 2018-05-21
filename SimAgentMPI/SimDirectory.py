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

from SimJob import SimJob
import os,errno
import zipfile

class SimDirectory(object):
    results_folder_name = "SimAgentResults"
     
    def __init__(self, directory, servers_file_obj, initialize=False):
        self.servers_file_obj = servers_file_obj
        self.sim_directory = directory
        self.sim_directory_relative = os.path.basename(self.sim_directory)
        self.sim_jobs = []
        
        self.sim_results_dir = os.path.join(self.sim_directory, SimDirectory.results_folder_name)
        
        
        """ DETECTION """
        #Determine what files are present in the directory
                
        #If the directory isn't there we want to create it, can check with is_valid.. by callers
        if(not os.path.isdir(self.sim_results_dir)):
            self.is_valid_sim_directory = False
            if(initialize):
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
            self.sim_jobs.append(SimJob(self, os.path.join(self.sim_results_dir, job_folder)))
        
        
        return
    
    def initialize(self):
        try:
            os.makedirs(self.sim_results_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
                
        self.is_valid_sim_directory = True
        
        return
    
    def zipdir(self, path, ziph, foldername):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                dir_ = root.split(self.sim_directory_relative, 1)[-1]
                if(len(dir_) and dir_[0] == "\\"):
                    dir_ = dir_[1:]
                if(dir_.startswith(SimDirectory.results_folder_name)):#only want files in root dir and not results
                    continue
                #print(os.path.join(self.sim_directory_relative,dir_,file))
                ziph.write(os.path.join(root, file), arcname=os.path.join(foldername,dir_,file))
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
    
"""    
def test():
    directory = "C:\\Users\\Tyler\\Desktop\\git_stage\\Sample_Model"
    sd = SimDirectory(directory, None, initialize=True)    
    #sd.take_snapshotzip("C:\\Users\\Tyler\\Desktop\\git_stage\\Sample_Model\\SimAgentResults\\Sample_Model-00538\\snapshott.zip")
    
test()
"""
    