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
from SimAgentMPI.ServerInterface import ServerInterface
from SimAgentMPI.nsg.nsgclient import Client
from SimAgentMPI.ParametricSweep import ParametricSweep
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
     
    def __init__(self, directory, initialize=False,prompt=True, init_results= True, init_sweeps=False):
        self.sim_directory = directory
        self.sim_directory_relative = os.path.basename(self.sim_directory)
        self.sim_jobs = []
        self.sim_sweeps = []
        
        self.sim_results_dir = os.path.join(self.sim_directory, SimDirectory.results_folder_name)
        self.sim_sweeps_dir = os.path.join(self.sim_results_dir, ParametricSweep.sweeps_folder_name)
        
        self.propname_version = "version"
        self.propname_custom_tool = "custom_tool"
        self.propname_update_enabled = "update_enabled"
        self.propname_update_server_output = "update_server_output"
        self.propname_update_interval = "update_interval_seconds"
        
        self.version_num = SimDirectory.version
        self.custom_tool = ""     
        self.update_enabled = "1"
        self.update_server_output = False
        self.update_interval_seconds = 60
        
        
        self.full_properties_path = os.path.join(self.sim_results_dir,SimDirectory.properties_file)
        
        """ DETECTION """
        #Determine what files are present in the directory
                
        #If the directory isn't there we want to create it, can check with is_valid.. by callers
        if(not os.path.isdir(self.sim_results_dir)):
            self.is_valid_sim_directory = False
            if initialize:
                if prompt:
                    if(messagebox.askquestion("", "SimAgent has not used this directory before. Do you want to initialize it? This will create an empty folder named "+SimDirectory.results_folder_name+" to store results in.", icon='warning') == 'yes'):
                        self.initialize()
                else:
                    self.initialize()
            else:
                return
        
        """ CREATE JOBS """
        #Grab all the data we need
        if init_results:
            results_dir_files = os.listdir(self.sim_results_dir)
            results_dir_folder_names = []
            for file in results_dir_files:
                if(os.path.isdir(os.path.join(self.sim_results_dir,file))):
                    if(file != ParametricSweep.sweeps_folder_name):
                        results_dir_folder_names.append(file)
            
            #Initialize all jobs
            for job_folder in results_dir_folder_names:
                try:
                    self.add_new_job(SimJob(self, os.path.join(self.sim_results_dir, job_folder)))
                    print("loaded dir")
                    print(os.path.join(self.sim_results_dir, job_folder))
                except Exception as e:
                    messagebox.showinfo("Load Error","Could not load simjob " + job_folder + ". See the console for info. Continuing...")
                    print(e)
                
        
        """ CREATE SWEEPS """
        if init_sweeps and os.path.isdir(self.sim_sweeps_dir):
            sweep_dir_files = os.listdir(self.sim_sweeps_dir)
            sweep_dir_folder_names = []
            for file in sweep_dir_files:
                if(os.path.isdir(os.path.join(self.sim_sweeps_dir,file))):
                    if(file != ParametricSweep.sweeps_folder_name):
                        sweep_dir_folder_names.append(file)
            
            
            for sweep_folder in sweep_dir_folder_names:
                try:
                    self.add_new_sweep(ParametricSweep(self, sweep_folder))
                    print("loaded sweep:")
                    print(os.path.join(self.sim_sweeps_dir, sweep_folder))
                except Exception as e:
                    messagebox.showinfo("Load Error","Could not load sweep " + sweep_folder + ". See the console for info. Continuing...")
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
    
    def delete_all_jobs(self):
        for j in self.sim_jobs:
            self.delete_job(j)
        return
    
    def take_snapshotzip(self, save_to_file):
        #Zip up everything except results foldername
        zipf = zipfile.ZipFile(save_to_file+".zip", 'w', zipfile.ZIP_DEFLATED)
        dir_path = self.sim_directory
        self.zipdir(dir_path, zipf, foldername=os.path.basename(save_to_file)) #must be in format file.zip -> file (folder) -> sim stuff
        zipf.close()
        return
    
    def add_new_sweep(self,sweep):
        if not self.get_sweep(sweep.name):
            self.sim_sweeps.append(sweep)
        return
    
    def get_sweep_names(self):
        sweeps = []
        for s in self.sim_sweeps:
            sweeps.append(s.name)
        return sweeps
    
    def get_sweep(self, sweep_name):
        for sweep in self.sim_sweeps:
            if sweep.name == sweep_name:
                sweep.reload()
                return sweep
        return None
    
    def delete_sweep(self, sweep_name):
        s = self.get_sweep(sweep_name)
        if not s:
            return
        
        shutil.rmtree(s.sweep_dir)
        self.sim_sweeps.remove(s)
        
    
    def add_new_job(self,simjob):
        if not self.get_job(simjob.sim_name):
            self.sim_jobs.append(simjob)
        return
    
    def get_job(self, job_name):
        for job in self.sim_jobs:
            if job.sim_name == job_name:
                return job
        return None
    
    def update_all_jobs(self):
    
        nsg_job_lists = {}
        ssh_conns = {}
        
        for job in self.sim_jobs:
            if(job.status==ServerInterface.ssh_status[0]):
                
                ssh_conn = ssh_conns.get(job.server_connector)
                if not ssh_conn:
                    server = job.get_server()
                    try:
                        ssh_conn = ServerInterface().connect_ssh(server,job)
                        ssh_conns[job.server_connector] = ssh_conn
                    except Exception as e:
                        job.append_log('SimDirectory.update_all_jobs() Caught exception: %s: %s' % (e.__class__, e))
                        #traceback.print_exc()
                        try:
                            ssh_conn.close()
                        except:
                            pass
                        
                job.update(ssh_connection=ssh_conn, update_server_output=self.update_server_output)
                job.read_properties()
            
            if(job.status==ServerInterface.nsg_status[0]):
                
                nsg_list = nsg_job_lists.get(job.server_connector)
                if not nsg_list:
                    server = job.get_server()
                    nsg = Client(server.nsg_api_appname, server.nsg_api_appid, server.user, server.password, server.nsg_api_url)
                    nsg_job_lists[job.server_connector] = nsg.listJobs()
                
                job.update(nsg_job_list=nsg_list, update_server_output=self.update_server_output)
                job.read_properties()
                     
        
        for key, ssh_conn in ssh_conns.items():#clean up ssh connections
            try:
                ssh_conn.close()
            except Exception as e:
                print('SimDirectory.update_all_jobs() Caught exception while attempting to close connections: %s: %s' % (e.__class__, e))
                pass
            
        
        return
        

    def read_properties(self):
        if(os.path.isfile(self.full_properties_path)):
            with open(self.full_properties_path) as json_file:  
                data = json.load(json_file)
                self.custom_tool = data[self.propname_custom_tool] 
                self.version_num = data[self.propname_version]
                self.update_enabled = data[self.propname_update_enabled]
                self.update_interval_seconds = data[self.propname_update_interval]
                self.update_server_output = data.get(self.propname_update_server_output, False)
        return

    def write_properties(self):
        data = {}
        data[self.propname_custom_tool] = self.custom_tool      
        data[self.propname_version] = self.version_num
        data[self.propname_update_enabled] = self.update_enabled
        data[self.propname_update_interval] = self.update_interval_seconds
        data[self.propname_update_server_output] = self.update_server_output
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
    
    def set_update_enabled_server(self, val):
        self.update_server_output = val
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
    