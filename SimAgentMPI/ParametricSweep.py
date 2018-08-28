# -*- coding: utf-8 -*-
"""
Created on Wed May 30 21:01:24 2018

@author: Tyler
"""
import json
import os
import errno
import zipfile
import shutil
import datetime, time
import SimAgentMPI
from SimAgentMPI.SimJob import SimJob
from SimAgentMPI.Utils import StoppableThread

from tempfile import mkstemp
from shutil import move
from os import fdopen, remove


class ParametricSweep(object):
    '''
    (PS_CREATE) --(PS_BUILD)--> (PS_READY) --(PS_SUBMITTING) <-> (PS_RUNNING) --> (PS_COMPLETE)
          ^                         V                                V
          |<---(PS_DECONSTRUCT)-----|                                |
                       ^                                             |
                       |------ (PS_CANCELLED) <-- (PS_CANCELLING) ---|
          
    '''
    
    state = ["PS_CREATE", "PS_BUILD", "PS_READY", "PS_DECONSTRUCT",
             "PS_SUBMITTING", "PS_RUNNING", "PS_CANCELLING", "PS_CANCELLED",
             "PS_COMPLETE"]
    sweeps_folder_name = "_sweeps"
    properties_file = "sweep.properties"
    original_extension = ""
    working_extension = "-working"
    job_template_name = "_template_"
    version = 1
    
    """
    project_dir : SimDirectory
    name : String
    """
    def __init__(self, project_dir, name, initialize=True, external_state_var=None, init_callback = None):
        self.version = ParametricSweep.version
        
        self.name = name
        
        self.project_dir = project_dir
        self.sweep_project_dir = None
        
        self.initialize = initialize
        
        self.parent_sweep_dir = os.path.join(self.project_dir.sim_results_dir, ParametricSweep.sweeps_folder_name)
        self.sweep_dir = os.path.join(self.parent_sweep_dir, self.name)
        
        self.origdir = self.project_dir.sim_directory_relative + ParametricSweep.original_extension
        self.workdir = self.project_dir.sim_directory_relative + ParametricSweep.working_extension
        
        self.sweep_dir_original = os.path.join(self.parent_sweep_dir, self.name, self.origdir)
        self.sweep_dir_working = os.path.join(self.parent_sweep_dir, self.name, self.workdir)
        self.full_properties_path = os.path.join(self.sweep_dir, ParametricSweep.properties_file)
        
        self.snapzip = self.sweep_dir_original + ".zip"
        
        self.propname_maxjobs = "maxjobs"
        self.propname_version = "version"
        self.propname_state = "state"
        self.propname_parameters = "parameters"
        self.propname_is_and_sweep = "is_and_sweep"
        
        self.maxjobs = 1
        self.model_job = None
        self.parameters = []#objects of some sort
        self.is_and_sweep = True #Sweep can either be an or (p1.1 * p2.1 * pn.m) or an and (p1.1 + p2.1 + pn)
        
        self.current_running_jobs = 0
        self.completed_jobs = 0
        self.cancel_initiated = False #If we're in a submitting state
        
        self.is_in_working_state = False #will write this to file everytime state changes so we restart state if app closes
        
        self.state = ""
        self.external_state_var = None
        if external_state_var:
            self.external_state_var = external_state_var
            self.external_state_var.set(self.state)
            
        self.init(init_callback)
         
        return
    
    def add_parameter(self, container):
        self.parameters.append(container)
        return
    
    def update_parameter(self, container):
        old_cont = self.get_parameter(container.id)
        if not old_cont:
            return
        old_cont.filename = container.filename
        old_cont.filehash = container.filehash
        old_cont.location_start = container.location_start
        old_cont.location_end = container.location_end
        old_cont.parameters = container.parameters
        self.write_properties()
    
    def del_parameter(self, container):
        c_id = container.id
        self.parameters.remove(container)
        
        for p in self.parameters:#re-assign ids to keep consitant
            if p.id > c_id:
                p.id = int(p.id)-1
                
        return
    
    def get_parameter(self, id_):
        for p in self.parameters:
            if str(p.id) == str(id_):
                return p
            
    def get_parameters_sorted(self):
        #The thinking behind this is: if the same file has multiple edits we want 
        #to change later parameters first, as to to not mess with line numbers and row 
        #numbers of later params
        #tertiary (column number)
        s = sorted(self.parameters, key = lambda x: int(x.location_start.split(".")[1]), reverse=True) 
        #secondary (line row number)
        s = sorted(s, key = lambda x: int(x.location_start.split(".")[0]), reverse=True) 
        #primary (filename)
        s = sorted(s, key = lambda x: int(x.id))
        
        return s
    
    def get_next_parameter_id(self):
        maximum = 0
        for p in self.parameters:
            if int(p.id) > maximum:
                maximum = int(p.id)
        
        return maximum + 1
    
    def set_external_state_var(self, external_state_var):
        self.external_state_var = external_state_var
        self.external_state_var.set(self.state)
    
    def reload(self):
        return self.init(None)
    
    def init(self,init_callback):
        
        if(self.initialize):
            if(not os.path.isdir(self.parent_sweep_dir)):
                try:
                    os.makedirs(self.parent_sweep_dir)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise
                        
            if(not os.path.isdir(self.sweep_dir)):
                try:
                    os.makedirs(self.sweep_dir)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise
            if(os.path.isfile(self.full_properties_path)):
                self.initialize = False
                self.init(init_callback) #Don't want to write all the end at the end again, same diff
            else:
                self.write_properties()
                self._set_state(ParametricSweep.state[0])
        else:
            if(os.path.isfile(self.full_properties_path)):
                self.read_properties(from_cold=True)
            if os.path.isdir(self.sweep_dir_working):
                self.sweep_project_dir = SimAgentMPI.SimDirectory.SimDirectory(self.sweep_dir_working, initialize=True,prompt=False)

        
        if init_callback:
            init_callback()    
            
        return
    state = ["PS_CREATE", "PS_BUILD", "PS_READY", "PS_DECONSTRUCT",
             "PS_SUBMITTING", "PS_RUNNING", "PS_CANCELLING", "PS_CANCELLED",
             "PS_COMPLETE"]
    def _set_state(self, state, from_cold=False):
        if from_cold:
            if state == ParametricSweep.state[1] or state == ParametricSweep.state[3]: #If we were in the middle of running a build or deconstructing, destroy everything set to create
                state = ParametricSweep.state[0]
            elif state == ParametricSweep.state[4]: #If we were submitting just start submitting again
                state = ParametricSweep.state[5]
            elif state == ParametricSweep.state[6]: #If we're cancelling check all jobs state, if any still running stop
                state = ParametricSweep.state[7]
                    
        #print("Parametric sweep {} now in state {}".format(self.name, state))
        self.state = state
        if self.external_state_var:
            self.external_state_var.set(self.state)
            
        if not from_cold:
            self.write_properties()
        return
    
    def get_state(self):
        return self.state
    
    
    def take_project_snapshot(self):
        self.project_dir.take_snapshotzip(self.sweep_dir_original)
        
        
        #unzip
        zip_ref = zipfile.ZipFile(self.snapzip, 'r')
        #zip_ref.extractall(self.sweep_dir_original)
        zip_ref.extractall(self.sweep_dir_working)
        zip_ref.close()
        #move everything in the directory up a level
        
        source = os.path.join(self.sweep_dir_working, self.origdir)
        dest1 = os.path.join(source, "../")
        
        files = []
        
        for (dirpath, dirnames, files) in os.walk(source):
            for f in files:
                src = os.path.join(dirpath, f)
                frel = os.path.relpath(src, source)
                dst = os.path.abspath(os.path.join(dest1,frel))
                #print("SRC: {}\nDST: {}\n\n".format(src, dst))
                dstpath = os.path.dirname(dst)
                if not os.path.exists(dstpath):
                    os.mkdir(dstpath)
                shutil.move(src,dst)
        
        shutil.rmtree(source,ignore_errors=True)
        
        return
    
    def delete_project_snapshot_results(self):
        if os.path.isdir(self.sweep_dir_working):
            shutil.rmtree(self.sweep_dir_working, ignore_errors=True)
        if os.path.isfile(self.snapzip):
            os.remove(self.snapzip)
            
    def rm_all_jobs(self):
        template_job = self.sweep_project_dir.get_job(ParametricSweep.job_template_name)
        self.sweep_project_dir.delete_all_jobs(exclude=[template_job])
        return
    
    def initialize_sweep(self):
        self.take_project_snapshot()
        self.sweep_project_dir = SimAgentMPI.SimDirectory.SimDirectory(self.sweep_dir_working, initialize=True,prompt=False)
        return
    
    def create_new_jobs(self):
        
        def recurse_params(i=0,path_="",param_path=[]):
            
            if not len(self.parameters):
                return
            if i == len(self.parameters): #Base case
                path_ = path_[1:]#get rid of first -
                path_arr = path_.split("-")
                s = sorted(path_arr, key = lambda x: int(x.split(".")[1]), reverse=False) 
                path_n = sorted(s, key = lambda x: int(x.split(".")[0]), reverse=False) 
                path_ = '-'.join(str(x) for x in path_n)
                #simjob = SimJob(self.sweep_project_dir, "job-{}".format(path_))
                template_job = self.sweep_project_dir.get_job(ParametricSweep.job_template_name)
                if template_job:
                    simjob = template_job.clone("job-{}".format(path_))
                    simjob.write_properties()
                else: #Should never happen, but will create jobs
                    simjob = SimJob(self.sweep_project_dir, "job-{}".format(path_))
                
                simjob.clear_notes()
                for p in param_path:
                    parameter = self.get_parameters_sorted()[p[0]]
                    notes_text = parameter.apply_change(self.sweep_project_dir.sim_directory, p[1])#make changes
                    simjob.append_notes(notes_text)
                   
                simjob.create_snapshot()#copy changes
                self.take_project_snapshot()#reset changes
                self.sweep_project_dir.add_new_job(simjob)
                return simjob
            
            parameter = self.get_parameters_sorted()[i]
            for j, p in enumerate(parameter.parameters):
                path_n = path_ + "-{}.{}".format(parameter.id,j+1)
                param_path_n = list(param_path)
                param_path_n.append([i,j])
                recurse_params(i=i+1,path_=path_n,param_path=param_path_n)
           
            return 
        
        
        if self.is_and_sweep:
            recurse_params()
        else:
            for i, param in enumerate(self.get_parameters_sorted()):
                for j, sub_param in enumerate(param.parameters):
                    ###simjob = SimJob(self.sweep_project_dir, "j{}.{}".format(i+1,j+1))
                    #simjob = SimJob(self.sweep_project_dir, "job-{}.{}".format(param.id,j+1))
                    template_job = self.sweep_project_dir.get_job(ParametricSweep.job_template_name)
                    if template_job:
                        simjob = template_job.clone("job-{}.{}".format(param.id,j+1))
                        simjob.write_properties()
                    else:
                        simjob = SimJob(self.sweep_project_dir, "job-{}.{}".format(param.id,j+1))
                    notes_text = param.apply_change(self.sweep_project_dir.sim_directory, j)#make changes
                    simjob.clear_notes()
                    simjob.append_notes(notes_text)
                    simjob.create_snapshot()#copy changes
                    self.take_project_snapshot()#reset changes
                    self.sweep_project_dir.add_new_job(simjob)
            
    def get_num_running_jobs(self):
        return self.sweep_project_dir.get_num_running_jobs()
    
    """
    Create snapshot of project_dir
    Create all simjobs in the sweep_dir
    """
    def build(self, callback=None):
        
        if self.state == ParametricSweep.state[0]: #If we're done creating
            self.is_in_working_state = True
            self._set_state(ParametricSweep.state[1])  #We're now building
            
            #Threaded stuff here
            self.create_new_jobs()
            #simjob = SimJob(self.sweep_project_dir, "{}-run".format(1))
            #self.sweep_project_dir.add_new_job(simjob)
                            
            self._set_state(ParametricSweep.state[2])  #We've built the Sweep
            self.is_in_working_state = False
            if callback:
                callback()
        return
    
    """
    Delete all simjobs in sweep_dir
    """
    def deconstruct(self, callback=None):
        if self.state == ParametricSweep.state[2] or self.state == ParametricSweep.state[7]: #If we're built or cancelled
            self.is_in_working_state = True
            self._set_state(ParametricSweep.state[3])   #We're now deconstructing
            #Threaded stuff here
            #self.delete_project_snapshot_results()
            self.rm_all_jobs()
            #self.sweep_project_dir = None
            
            self._set_state(ParametricSweep.state[0])  #Deconstructing complete
            self.is_in_working_state = False
            if callback:
                callback()
        return
    
    """
    Loop through all simjobs and submit
    """
    def submit(self, finish_callback=None,each_run_callback=None):
        
        class SubmitThread(StoppableThread):
            def run(self):
                self.ref.is_in_working_state = True
                self.ref._set_state(ParametricSweep.state[4]) # We're going to be submitting new jobs now
                
                for j in self.ref.sweep_project_dir.get_displayable_jobs():
                    if self.stopped():
                        break
                    
                    if self.ref.get_num_running_jobs() < int(self.ref.maxjobs):
                        if(j.is_ready_to_submit()):
                            j.run(create_snap=False)
                            if self.ref.each_run_callback:
                                self.ref.each_run_callback()
                    else:
                        break
                self.ref._set_state(ParametricSweep.state[5]) # We're done sumbitting for now
                self.ref.is_in_working_state = False
                
                if self.ref.cancel_initiated:
                    self.ref.cancel()
                
                if self.ref.finish_callback:
                    self.ref.finish_callback()
                    
                return
        
        self.each_run_callback = each_run_callback
        self.finish_callback = finish_callback
        
        if self.state == ParametricSweep.state[2] or self.state==ParametricSweep.state[5]: #If we're in a ready state or running
            if not self.is_in_working_state and not self.cancel_initiated:
                print("Completed: {}\nTotal: {}".format(self.sweep_project_dir.get_num_completed_jobs(),self.sweep_project_dir.get_num_total_jobs()))
                if self.sweep_project_dir.get_num_completed_jobs() == self.sweep_project_dir.get_num_total_jobs():
                    self._set_state(ParametricSweep.state[8])
                    
                elif self.get_num_running_jobs() < int(self.maxjobs):
                    
                    #Threaded stuff here
                    submit_thread = SubmitThread(ref=self)#Strongly untyped, be careful
                    submit_thread.setDaemon(True)
                    submit_thread.start()
                    
                    return submit_thread
        
        return None
    
    """
    Loop through all simjobs and cancel
    """
    def cancel(self, callback=None):
                
        class CancelThread(StoppableThread):
            def run(self):
                self.ref.is_in_working_state = True
                self.ref._set_state(ParametricSweep.state[6])
                
                for j in self.ref.sweep_project_dir.sim_jobs:
                    if self.stopped():
                        break
                    
                    if j.is_running():
                        j.stop()
                
                self.ref._set_state(ParametricSweep.state[7])
                self.ref.is_in_working_state = False
                if self.ref.callback:
                    self.ref.callback()
                
                return
            
        self.callback = callback
        
        if self.state == ParametricSweep.state[4] or self.state == ParametricSweep.state[5]:
            if not self.is_in_working_state:
                
                #Threaded stuff here
                    cancel_thread = CancelThread(ref=self)#Strongly untyped, be careful
                    cancel_thread.setDaemon(True)
                    cancel_thread.start()
                    
                    return cancel_thread
                
            else:
                self.cancel_initiated = True
                #Run a thread to keep trying to cancel, since we're probably in the mid of submitting
                
        return None
    
    def read_properties(self, from_cold=False):
        if(os.path.isfile(self.full_properties_path)):
            with open(self.full_properties_path) as json_file:  
                data = json.load(json_file)
                self.maxjobs = data[self.propname_maxjobs] 
                self.version_num = data[self.propname_version]
                self._set_state(data[self.propname_state], from_cold=from_cold)
                self.is_and_sweep = data.get(self.propname_is_and_sweep,True)
                params = data.get(self.propname_parameters,[])
                self.parameters.clear()
                for p in params:
                    self.parameters.append(ParameterContainer().from_json(p))
                
        return

    def write_properties(self):
        data = {}
        data[self.propname_maxjobs] = self.maxjobs      
        data[self.propname_version] = self.version
        data[self.propname_state] = self.state
        params = []
        for p in self.parameters:
            params.append(p.to_json())
        data[self.propname_parameters] = params
        data[self.propname_is_and_sweep] = self.is_and_sweep
        
        with open(self.full_properties_path, 'w') as outfile:  
            json.dump(data, outfile)
            
        return
    
class ParameterContainer():
    def __init__(self):
        self.init("","","","",[])
        return
    
    def init(self, fn, fh, ls, le, p,id_=None):
        if id_:
            st = id_
        else:
            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%H%M%S')
        self.id = st
        self.filename = fn
        self.filehash = fh
        self.location_start = ls
        self.location_end = le
        self.parameters = p
        return self
    
    def get_line_numbers(self):
        rng = range(int(self.location_start.split(".")[0])-1,int(self.location_end.split(".")[0]))
        lines = []
        for r in rng:
            lines.append(r)
            
        
        pos = [int(self.location_start.split(".")[1]),int(self.location_end.split(".")[1])]
            
        return (lines,pos)
    
    def get_line_text(self, directory,mark_select=False):
        ret = ""
        if directory:
            file_ = os.path.join(directory, self.filename)
            if os.path.isfile(file_):
                fp = open(file_)
                ln = self.get_line_numbers()
                line_nums = ln[0]
                start_line = ln[0][0]
                end_line = ln[0][len(ln[0])-1]
                start = ln[1][0]
                end = ln[1][1]
                
                for i, line in enumerate(fp):
                    if i in line_nums:
                        if len(line_nums):
                            if len(line_nums) == 1: #Single row
                                if len(line) > end:
                                    line = line[:start] + "[[]]" + line[end:]
                                    
                            else:
                                if i == start_line and i < end_line: #start
                                    line = line[:start] + "[[\n"
                                elif i > start_line and i < end_line: #middle
                                    line = "\n"
                                elif i == end_line:#end
                                    line = "]]" + line[end:]
                            
                        if ret == "":
                            ret = line
                        else:
                            ret = ret + line
                fp.close()
        return ret
    
    def apply_change(self, directory, parameter_index):
        ret_text = ""
        if directory:
            file_ = os.path.join(directory, self.filename)
            if os.path.isfile(file_):
                
                fh, abs_path = mkstemp()
                with fdopen(fh,'w') as new_file:
                    with open(file_) as old_file:
                        ln = self.get_line_numbers()
                        line_nums = ln[0]
                        start_line = ln[0][0]
                        end_line = ln[0][len(ln[0])-1]
                        start = ln[1][0]
                        end = ln[1][1]
                        s = ""
                        dash = ""
                        end_ = ""
                        if start_line != end_line:
                            s = "s"
                            dash = "-"
                            end_ = end_line+1
                        ret_text = "P{}. Changed file \"{}\" - line{}:{}{}{}\n".format(self.id, self.filename, s, start_line+1,dash,end_)
                        
                        
                        for i, line in enumerate(old_file):
                            if i in line_nums:
                                if len(line_nums):
                                    ret_text = ret_text + "[Original]\n"
                                    ret_text = ret_text + line
                                    ret_text = ret_text + "[Changed to]\n"
                                    if len(line_nums) == 1: #Single row
                                        if len(line) > end:
                                            line = line[:start] + self.parameters[parameter_index] + line[end:]
                                            
                                    else:
                                        if i == start_line and i < end_line: #start
                                            line = line[:start] + self.parameters[parameter_index] +"\n"
                                        elif i > start_line and i < end_line: #middle
                                            line = "\n"
                                        elif i == end_line:#end
                                            line = line[end:]
                                    
                                    ret_text = ret_text + line
                                    
                            new_file.write(line)
                        
                #Remove original file
                remove(file_)
                #Move new file
                move(abs_path, file_)
                
        return ret_text
        
    def to_json(self):
        data = {}
        data["id"] = self.id
        data["filename"] = self.filename
        data["filehash"] = self.filehash
        data["location_start"] = self.location_start
        data["location_end"] = self.location_end
        data["parameters"] = self.parameters
        return data
    
    def from_json(self,data):
        self.id = data.get("id","")
        self.filename = data.get("filename","")
        self.filehash = data.get("filehash","")
        self.location_start = data.get("location_start", "")
        self.location_end = data.get("location_end","")
        self.parameters = data.get("parameters",[])
        return self
        