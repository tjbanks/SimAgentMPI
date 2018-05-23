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
                - initial_snapshot.zip
                - results.zip
                 
"""

import os
import json
import time
import datetime
import subprocess

from ServerInterface import ServerInterface

class SimJob(object):
    properties_file = "sim.properties"
    log_file = "sim.log"
    notes_file = "sim_notes.txt"
    version = "1.0"
    default_log_text = "Write notes about this job here..."
    
    def __init__(self, sim_directory_object, job_directory):
        self.sim_directory_object = sim_directory_object
        self.job_directory = job_directory
        self.sim_name = os.path.basename(self.job_directory)
        self.job_directory_absolute = os.path.join(sim_directory_object.sim_results_dir,self.sim_name)
        
        #Names for the JSON file
        self.propname_version = "version"
        self.propname_log = "log"
        self.propname_notes = "notes"
        self.propname_status = "status"
        self.propname_snapshotzip = "snapshot_zip"
        self.propname_resultzip = "result_zip"
        self.propname_resultdir = "result_dir"
        self.propname_batch_file = "batch_file"
        self.propname_update_interval = "update_interval"
        self.propname_server_connector = "server_connector"
        self.propname_server_nodes = "server_nodes"
        self.propname_server_cores = "server_cores"
        self.propname_server_nsg_tool = "server_nsg_tool"
        self.propname_server_ssh_tool = "server_ssh_tool"
        self.propname_server_nsg_python = "server_nsg_python"
        self.propname_server_mpi_partition = "server_ssh_mpi_partition"
        self.propname_server_max_runtime = "server_max_runtime"
        self.propname_server_email = "email_addr"
        self.propname_server_status_email = "server_status_email"
        self.propname_server_remote_identifier = "server_remote_identifier"
        self.propname_sim_start_time = "sim_start_time"
        
        self.file_snapshotzip = ""
        self.file_resultszip = ""
        self.file_properties = SimJob.properties_file
        self.dir_results = ""
        
        self.version = SimJob.version
        self.log = SimJob.log_file
        self.notes = SimJob.notes_file
        self.status = ""
        self.batch_file = ""
        self.update_interval = "60"
        self.server_connector = ""
        self.server_nodes = ""
        self.server_cores = ""
        self.server_nsg_tool = "NONE"
        self.server_ssh_tool = "sbatch"
        self.server_nsg_python = "1"
        self.server_mpi_partition = ""
        self.server_max_runtime = "1"
        self.server_email = ""
        self.server_status_email = "false"
        self.server_remote_identifier = ""
        self.sim_start_time = ""
        
        self.full_properties_path = os.path.join(self.sim_directory_object.sim_results_dir, self.job_directory,self.file_properties)
        
        
        self.read_properties()
        return
    
    def create_sim_directory(self, dir_=None):
        if not dir_:
            dir_ = self.sim_directory_object.sim_results_dir
        path = os.mkdir(os.path.join(dir_,self.sim_name))
        print(path)
        
    def open_sim_directory(self):
        subprocess.call("start "+self.job_directory, shell=True)
        
    def write_notes(self, text):
        full_notes_path = os.path.join(self.sim_directory_object.sim_results_dir,self.sim_name,self.notes)
        append_write = 'w'
        
        f = open(full_notes_path,append_write)
        f.write(text)
        f.close()
        
        return
    
    def append_log(self, text):
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%y-%m-%d %H:%M:%S')
        
        full_log_path = os.path.join(self.sim_directory_object.sim_results_dir,self.sim_name,self.log)
        append_write = ''
        if os.path.exists(full_log_path):
            append_write = 'a' # append if already exists
        else:
            append_write = 'w' # make a new file if not
        
        f = open(full_log_path,append_write)
        if isinstance(text,list):
            for i,line in enumerate(text):
                if i == 0:
                    f.write(st + ' > ' + line)
                else:
                    f.write(line)
        else:
            f.write(st + ' > ' + text+'\n')
        f.close()
        
        return
        
    def get_notes(self):
        f = open(os.path.join(self.job_directory_absolute,self.notes_file),"r")
        string = f.read()
        f.close()
        return string
    
    
    def get_log(self):
        f = open(os.path.join(self.job_directory_absolute,self.log_file),"r")
        string = f.read()
        f.close()
        return string
    
    def read_properties(self):
        if(os.path.isfile(self.full_properties_path)):
            with open(self.full_properties_path) as json_file:  
                data = json.load(json_file)
                self.version = data[self.propname_version]
                self.log = data[self.propname_log]
                self.notes = data[self.propname_notes]
                self.status = data[self.propname_status]
                self.file_snapshotzip = data[self.propname_snapshotzip]
                self.file_resultszip = data[self.propname_resultzip]
                self.dir_results = data[self.propname_resultdir]
                self.batch_file = data[self.propname_batch_file]
                self.update_interval = data[self.propname_update_interval]
                self.server_connector = data[self.propname_server_connector]
                self.server_nodes = data[self.propname_server_nodes]
                self.server_cores = data[self.propname_server_cores]
                self.server_nsg_tool = data[self.propname_server_nsg_tool]
                self.server_ssh_tool = data[self.propname_server_ssh_tool]
                self.server_nsg_python = data[self.propname_server_nsg_python]
                self.server_mpi_partition = data[self.propname_server_mpi_partition]
                self.server_max_runtime = data[self.propname_server_max_runtime]
                self.server_email = data[self.propname_server_email]
                self.server_status_email = data[self.propname_server_status_email]
                self.server_remote_identifier = data[self.propname_server_remote_identifier]
                self.sim_start_time = data[self.propname_sim_start_time]
            
        return
    
    def write_properties(self):
        data = {}
        data[self.propname_version] = self.version
        data[self.propname_log] = self.log
        data[self.propname_notes] = self.notes
        data[self.propname_status] = self.status
        data[self.propname_snapshotzip] = self.file_snapshotzip
        data[self.propname_resultzip] = self.file_resultszip
        data[self.propname_resultdir] = self.dir_results
        data[self.propname_batch_file] = self.batch_file
        data[self.propname_update_interval] = self.update_interval
        data[self.propname_server_connector] = self.server_connector
        data[self.propname_server_nodes] = self.server_nodes
        data[self.propname_server_cores] = self.server_cores
        data[self.propname_server_nsg_tool] = self.server_nsg_tool
        data[self.propname_server_ssh_tool] = self.server_ssh_tool
        data[self.propname_server_nsg_python] = self.server_nsg_python
        data[self.propname_server_mpi_partition] = self.server_mpi_partition
        data[self.propname_server_max_runtime] = self.server_max_runtime
        data[self.propname_server_email] = self.server_email
        data[self.propname_server_status_email] = self.server_status_email
        data[self.propname_server_remote_identifier] = self.server_remote_identifier
        data[self.propname_sim_start_time] = self.sim_start_time
        
        with open(os.path.join(self.sim_directory_object.sim_results_dir, self.job_directory,self.file_properties), 'w') as outfile:  
            json.dump(data, outfile)
            
        self.write_notes(SimJob.default_log_text)
        return
    
    
    def clone(self):
        return
    
    def create_snapshot(self):
        #snapshot of project, put in this directory to be sent to server
        #ts = time.time()
        #st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d-%H%M%S')
        self.file_snapshotzip = self.sim_name #-" + st
        self.sim_directory_object.take_snapshotzip(os.path.join(self.sim_directory_object.sim_results_dir,self.job_directory,self.file_snapshotzip))
        self.file_snapshotzip = self.file_snapshotzip +".zip" #for later use
            
    def run(self):
        self.append_log("Run initiated")
        self.append_log("Creating directory snapshot")
        self.create_snapshot()
        self.append_log(self.file_snapshotzip + " created")
        
        ServerInterface().start_simjob(self)
        #search status for remote identifer and update the properties file
        #set self start time here
        return
    
    def stop(self):
        self.append_log("Attempting to stop")
        ServerInterface().stop_simjob(self)
        return
    
    def update(self):
        if self.status == ServerInterface.ssh_status[0]:
            ServerInterface().update_for_completion(self)
            
        if self.status == ServerInterface.ssh_status[1]:
            ServerInterface().download_results_simjob(self)
        
        
        return