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

from SimAgentMPI.ServerInterface import ServerInterface
from SimAgentMPI.SimServer import ServersFile

class SimJob(object):
    properties_file = "sim.properties"
    log_file = "sim.log"
    stdout_file = "STDOUT"
    stderr_file = "STDERR"
    notes_file = "sim_notes.txt"
    version = "1.0"
    default_log_text = "Write notes about this job here..."
    created_status = "SIMJOB_CREATED"
    
    def __init__(self, sim_directory_object, job_directory,write_new=True):
        self.sim_directory_object = sim_directory_object
        self.job_directory = job_directory
        self.sim_name = os.path.basename(self.job_directory)
        self.job_directory_absolute = os.path.join(sim_directory_object.sim_results_dir,self.sim_name)
        self.write_new = write_new
        
        try:
            self.create_sim_directory()
        except:
            pass
        
        #Names for the JSON file
        self.propname_version = "version"
        self.propname_created = "created"
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
        self.propname_server_stdout_file = "server_stdout_file"
        self.propname_server_stderr_file = "server_stderr_file"
        self.propname_server_max_runtime = "server_max_runtime"
        self.propname_server_email = "email_addr"
        self.propname_server_status_email = "server_status_email"
        self.propname_server_remote_identifier = "server_remote_identifier"
        self.propname_sim_start_time = "sim_start_time"
        self.propname_sim_last_update_time = "sim_last_update_time"
        self.propname_sim_delete_remote_on_finish = "sim_delete_remote_on_finish"
        
        self.file_snapshotzip = ""
        self.file_resultszip = ""
        self.file_properties = SimJob.properties_file
        self.dir_results = ""
        
        self.version = SimJob.version
        self.created = time.time()
        self.log = SimJob.log_file
        self.notes = SimJob.notes_file
        self.status = SimJob.created_status
        self.batch_file = ""
        self.update_interval = "60"
        self.server_connector = ""
        self.server_nodes = ""
        self.server_cores = ""
        self.server_nsg_tool = "NONE"
        self.server_ssh_tool = "sbatch"
        self.server_nsg_python = "0"
        self.server_mpi_partition = ""
        self.server_stdout_file = "stdout.txt"
        self.server_stderr_file = "stderr.txt"
        self.server_max_runtime = "1"
        self.server_email = ""
        self.server_status_email = False
        self.server_remote_identifier = ""
        self.sim_start_time = ""
        self.sim_last_update_time = ""
        self.sim_delete_remote_on_finish = True
        
        self.full_properties_path = os.path.join(self.sim_directory_object.sim_results_dir, self.job_directory,self.file_properties)
        
        self.read_properties()
        return
    
    def create_sim_directory(self, dir_=None):
        if not dir_:
            dir_ = self.sim_directory_object.sim_results_dir
        os.mkdir(os.path.join(dir_,self.sim_name))
        #print(path)
        
    def open_sim_directory(self):
        subprocess.call("start \"\" \""+self.job_directory+"\"", shell=True)
        
    def open_sim_results_directory(self):
        res_path = os.path.join(self.sim_directory_object.sim_results_dir, self.job_directory,self.dir_results,self.sim_name)
        subprocess.call("start \"\" \""+res_path+"\"", shell=True)
        
    def write_notes(self, text):
        full_notes_path = os.path.join(self.sim_directory_object.sim_results_dir,self.sim_name,self.notes)
        append_write = 'w'
        try:
            f = open(full_notes_path,append_write)
            f.write(text)
            f.close()
        except Exception as e:
            print("Could not write notes to " + full_notes_path)
            print("Directory could be deleted")
            print(e)
        
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
        try:
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
        except Exception as e:
            print("Could not append log" + full_log_path)
            print("Directory could be deleted")
            print(e)
        
        return
    
    def clear_notes(self):
        full_notes_path = os.path.join(self.sim_directory_object.sim_results_dir,self.sim_name,self.notes)
        if os.path.isfile(full_notes_path):
            os.remove(full_notes_path)
        self.write_notes("")
    
    def append_notes(self, text):
        
        full_notes_path = os.path.join(self.sim_directory_object.sim_results_dir,self.sim_name,self.notes)
        append_write = ''
        if os.path.exists(full_notes_path):
            append_write = 'a' # append if already exists
        else:
            append_write = 'w' # make a new file if not
        try:
            f = open(full_notes_path,append_write)
            if isinstance(text,list):
                for i,line in enumerate(text):
                    if i == 0:
                        f.write(line)
                    else:
                        f.write(line)
            else:
                f.write(text+'\n')
            f.close()
        except Exception as e:
            print("Could not append notes" + full_notes_path)
            print("Directory could be deleted")
            print(e)
        
        return
    
    def run_custom(self):
        tool = self.sim_directory_object.custom_tool
        
        if ("../" in tool)==True or ("..\\" in tool)==True or ("./" in tool)==True or (".\\" in tool)==True :
            parts = tool.split(" ")
            for i, part in enumerate(parts):
                if ("../" in tool)==True or ("..\\" in tool)==True:
                    parts[i] = os.path.join(self.sim_directory_object.sim_directory,part)
            tool = ' '.join(parts)
        #os.path.abspath("mydir/myfile.txt")
        
        res_dir = os.path.join(self.job_directory_absolute,self.dir_results,self.sim_name)
        self.cmd = "cd \""+ res_dir + "\"" + " && start " + tool + " && exit"
        #print(self.cmd)
        #threading.Thread(target=self.start_cmd)
        self.append_log("Executed " + self.cmd)
        subprocess.call(self.cmd, shell=True)
        
    def start_cmd(self):
        if self.cmd:
            subprocess.call(self.cmd, shell=True)
        
    def get_notes(self):
        string = ""
        notes_file = os.path.join(self.job_directory_absolute,self.notes_file)
        if os.path.isfile(notes_file):
            f = open(notes_file,"r")
            string = f.read()
            f.close()
        return string
    
    
    def get_log(self):
        f = open(os.path.join(self.job_directory_absolute,self.log_file),"r")
        string = f.read()
        f.close()
        return string
    
    def get_log_stdout(self):
        out = os.path.join(self.job_directory_absolute,self.stdout_file)
        if not os.path.isfile(out):
            return ""
        f = open(os.path.join(self.job_directory_absolute,self.stdout_file),"r")
        string = f.read()
        f.close()
        return string
    
    def get_log_stderr(self):
        err = os.path.join(self.job_directory_absolute,self.stderr_file)
        if not os.path.isfile(err):
            return ""
        f = open(err,"r")
        string = f.read()
        f.close()
        return string
    
    def read_properties(self):
        if(os.path.isfile(self.full_properties_path)):
            with open(self.full_properties_path) as json_file:  
                data = json.load(json_file)
                self.version = data[self.propname_version]
                self.created = data[self.propname_created]
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
                self.server_stdout_file = data.get(self.propname_server_stdout_file, "stdout.txt")
                self.server_stderr_file = data.get(self.propname_server_stderr_file,"stderr.txt")
                self.server_max_runtime = data[self.propname_server_max_runtime]
                self.server_email = data[self.propname_server_email]
                self.server_status_email = data[self.propname_server_status_email]
                self.server_remote_identifier = data[self.propname_server_remote_identifier]
                self.sim_start_time = data[self.propname_sim_start_time]
                self.sim_last_update_time = data[self.propname_sim_last_update_time]
                self.sim_delete_remote_on_finish = data.get(self.propname_sim_delete_remote_on_finish,True)
        else:
            if self.write_new:
                self.write_properties()
                self.append_log("")
        return
    
    def write_properties(self):
        data = {}
        data[self.propname_version] = self.version
        data[self.propname_created] = self.created
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
        data[self.propname_server_stdout_file] = self.server_stdout_file
        data[self.propname_server_stderr_file] = self.server_stderr_file
        data[self.propname_server_max_runtime] = self.server_max_runtime
        data[self.propname_server_email] = self.server_email
        data[self.propname_server_status_email] = self.server_status_email
        data[self.propname_server_remote_identifier] = self.server_remote_identifier
        data[self.propname_sim_start_time] = self.sim_start_time
        data[self.propname_sim_last_update_time] = self.sim_last_update_time
        data[self.propname_sim_delete_remote_on_finish] = self.sim_delete_remote_on_finish
        
        with open(os.path.join(self.sim_directory_object.sim_results_dir, self.job_directory,self.file_properties), 'w') as outfile:  
            json.dump(data, outfile)
            
        #self.write_notes(SimJob.default_log_text)
        return
    
    def get_server(self):
        sf = ServersFile()
        if self.server_connector != "":
            return sf.get_server_byname(self.server_connector)
        return None
    
    def delete_remote(self):
        self.append_log("Delete remote initiated")        
        ServerInterface().delete_remote_results(self)
        return
    
    def download_remote(self):
        self.append_log("Download remote results initiated")        
        try:
            ServerInterface().download_results_simjob(self)
        except Exception as e:
            self.append_log("Couldn't download the files: " + e)
        return
    
    #ssh_status = ["SSH_sbatch_RUNNING","SSH_sbatch_COMPLETED","SSH_sbatch_DOWNLOADED","SSH_batch_CANCELLED","SSH_sbatch_DOWNLOADING","SSH_STARTING"]
    #nsg_status = ["NSG_RUNNING","NSG_COMPLETED","NSG_DOWNLOADED","NSG_CANCELLED","NSG_DOWNLOADING","NSG_STARTING"]
    def is_running(self):
        if self.status == ServerInterface.ssh_status[0] or self.status == ServerInterface.nsg_status[0]:
            return True
        return False
    
    def is_complete(self):
        if self.status == ServerInterface.ssh_status[1] or self.status == ServerInterface.nsg_status[1] or \
            ServerInterface.ssh_status[2] or self.status == ServerInterface.nsg_status[2] or \
            ServerInterface.ssh_status[3] or self.status == ServerInterface.nsg_status[3]:
            return True
        return False
    
    def is_ready_to_submit(self):
        if self.status not in ServerInterface.ssh_status and self.status not in ServerInterface.nsg_status:
            return True
        return False
    
    def create_snapshot(self):
        #snapshot of project, put in this directory to be sent to server
        #ts = time.time()
        #st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d-%H%M%S')
        self.file_snapshotzip = self.sim_name #-" + st
        self.sim_directory_object.take_snapshotzip(os.path.join(self.sim_directory_object.sim_results_dir,self.job_directory,self.file_snapshotzip))
        self.file_snapshotzip = self.file_snapshotzip +".zip" #for later use
        
    def set_snapshot(self):
        self.file_snapshotzip = self.sim_name +".zip" #for later use
            
    def run(self,create_snap=True):
        self.append_log("Run initiated")
        
        if create_snap:
            self.append_log("Creating directory snapshot")
            self.create_snapshot()
            self.append_log(self.file_snapshotzip + " created")
        else:
            self.set_snapshot()
                
        ServerInterface().start_simjob(self)
        return
    
    def stop(self):
        if self.status == ServerInterface.ssh_status[0] or self.status == ServerInterface.nsg_status[0]:
            self.append_log("Attempting to stop")
            ServerInterface().stop_simjob(self)
        
        return
    
    def download_server_output(self):
        ServerInterface.download_status_simjob(self)
        return
    
    def update(self, nsg_job_list=None, ssh_connection=None, update_server_output=True):
        if self.status == ServerInterface.ssh_status[0] or self.status == ServerInterface.nsg_status[0]: 
            ServerInterface().update_for_completion(self,nsg_job_list=nsg_job_list,ssh_connection=ssh_connection)
            if update_server_output:
                ServerInterface().download_status_simjob(self,nsg_job_list=nsg_job_list,ssh_connection=ssh_connection)
            self.sim_last_update_time = time.time()
            self.write_properties()
            
        if self.status == ServerInterface.ssh_status[1] or self.status == ServerInterface.nsg_status[1]:
            ServerInterface().download_results_simjob(self,nsg_job_list=nsg_job_list,ssh_connection=ssh_connection)
            if self.sim_delete_remote_on_finish:
                ServerInterface().delete_remote_results(self,nsg_job_list=nsg_job_list, ssh_connection=ssh_connection)            
            self.sim_last_update_time = time.time()
            self.write_properties()
        
        
        return
    
    def clone(self, name,write_new=True):
        simjob = SimJob(self.sim_directory_object, name, write_new=write_new)
        simjob.batch_file = self.batch_file
        simjob.update_interval = self.update_interval
        simjob.server_connector = self.server_connector
        simjob.server_nodes = self.server_nodes
        simjob.server_cores = self.server_cores
        simjob.server_stdout_file = self.server_stdout_file
        simjob.server_stderr_file = self.server_stderr_file
        simjob.server_nsg_tool = self.server_nsg_tool
        simjob.server_ssh_tool = self.server_ssh_tool
        simjob.server_nsg_python = self.server_nsg_python
        simjob.server_mpi_partition = self.server_mpi_partition
        simjob.server_max_runtime = self.server_max_runtime
        simjob.server_status_email = self.server_status_email
        simjob.sim_delete_remote_on_finish = self.sim_delete_remote_on_finish
        
        return simjob