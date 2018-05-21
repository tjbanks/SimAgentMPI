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

from ServerInterface import ServerInterface

class SimJob(object):
    properties_file = ".properties"
    version = "1.0"
    
    def __init__(self, sim_directory_object, job_directory):
        self.sim_directory_object = sim_directory_object
        self.job_directory = job_directory
        self.sim_name = os.path.basename(self.job_directory)
        
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
        self.propname_server_nsg_python = "server_nsg_python"
        self.propname_server_mpi_partition = "server_ssh_mpi_partition"
        self.propname_server_max_runtime = "server_max_runtime"
        self.propname_server_email = "email_addr"
        self.propname_server_status_email = "server_status_email"
        self.propname_server_remote_identifier = "server_remote_identifier"
        
        self.file_snapshotzip = ""
        self.file_resultszip = ""
        self.file_properties = SimJob.properties_file
        self.dir_results = ""
        
        self.version = SimJob.version
        self.log = ""
        self.notes = ""
        self.status = ""
        self.batch_file = ""
        self.update_interval = "60"
        self.server_connector = ""
        self.server_nodes = ""
        self.server_cores = ""
        self.server_nsg_tool = "NONE"
        self.server_nsg_python = "1"
        self.server_mpi_partition = ""
        self.server_max_runtime = ""
        self.server_email = ""
        self.server_status_email = "false"
        self.server_remote_identifier = ""
        self.write_properties()
        return
    
    
    def read_properties(self):
        with open(os.path.join(self.job_directory,self.file_properties)) as json_file:  
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
            self.server_nsg_python = data[self.propname_server_nsg_python]
            self.server_mpi_partition = data[self.propname_server_mpi_partition]
            self.server_max_runtime = data[self.propname_server_max_runtime]
            self.server_remote_identifier = data[self.propname_server_remote_identifier]
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
        data[self.propname_server_nsg_python] = self.server_nsg_python
        data[self.propname_server_mpi_partition] = self.server_mpi_partition
        data[self.propname_server_max_runtime] = self.server_max_runtime 
        data[self.propname_server_max_runtime] = self.server_remote_identifier
        
        with open(os.path.join(self.job_directory,self.file_properties), 'w') as outfile:  
            json.dump(data, outfile)
        return
    
    def clone(self):
        return
    
    def create_snapshot(self):
        #snapshot of project, put in this directory to be sent to server
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d-%H%M%S')
        self.file_snapshotzip = self.sim_name + "-snap-" + st
        self.sim_directory_object.take_snapshotzip(os.path.join(self.job_directory,self.file_snapshotzip))
        self.file_snapshotzip = self.file_snapshotzip +".zip" #for later use
        
    def validate():
        return
    
    def run(self):
        self.create_snapshot()
        status = ServerInterface().start_simjob(self)
        #search status for remote identifer and update the properties file
        return
    
    def stop(self):
        
        return
    
    def watch(self):
        
        return