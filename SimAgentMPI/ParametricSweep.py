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
    sweeps_folder_name = "SimAgentSweeps"
    properties_file = "sweep.properties"
    original_extension = "-original"
    working_extension = "-working"
    version = 1
    
    """
    project_dir : SimDirectory
    name : String
    """
    def __init__(self, project_dir, name, initialize=True, external_state_var=None):
        self.version = ParametricSweep.version
        
        self.name = name
        self.project_dir = project_dir
        self.initialize = initialize
        
        self.parent_sweep_dir = os.path.join(self.project_dir.sim_directory, ParametricSweep.sweeps_folder_name)
        self.sweep_dir = os.path.join(self.parent_sweep_dir, self.name)
        self.sweep_dir_original = os.path.join(self.parent_sweep_dir, self.name, self.project_dir.sim_directory_relative + ParametricSweep.original_extension)
        self.sweep_dir_working = os.path.join(self.parent_sweep_dir, self.name, self.project_dir.sim_directory_relative + ParametricSweep.working_extension)
        self.full_properties_path = os.path.join(self.sweep_dir, ParametricSweep.properties_file)
        
        self.propname_maxjobs = "maxjobs"
        self.propname_version = "version"
        self.propname_state = "state"
        
        self.maxjobs = 1
        self.server = None
        
        self.parameters = []#objects of some sort
        
        self.current_running_jobs = 0
        self.completed_jobs = 0
        self.cancel_initiated = False #If we're in a submitting state
        
        self.is_in_working_state = False #will write this to file everytime state changes so we restart state if app closes
        
        self.state = ""
        self.external_state_var = None
        if external_state_var:
            self.external_state_var = external_state_var
            self.external_state_var.set(self.state)
            
        self.init()
         
        return
    
    def init(self):
        
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
                self.read_properties(from_cold=True)
            else:
                self.write_properties()
                self._set_state(ParametricSweep.state[0])
        else:
            if(os.path.isfile(self.full_properties_path)):
                self.read_properties(from_cold=True)
            
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
                    
        print("Parametric sweep {} now in state {}".format(self.name, state))
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
        
        snapzip = self.sweep_dir_original + ".zip"
        #unzip
        zip_ref = zipfile.ZipFile(snapzip, 'r')
        #zip_ref.extractall(self.sweep_dir_original)
        zip_ref.extractall(self.sweep_dir_working)
        zip_ref.close()
        #move everything in the directory up a level
        """
        source = '/path/to/source_folder'
        dest1 = '/path/to/dest_folder'
        
        
        files = os.listdir(source)
        
        for f in files:
        shutil.move(source+f, dest1)
        """
        
        return
    
    """
    Create snapshot of project_dir
    Create all simjobs in the sweep_dir
    """
    def build(self, callback=None):
        if self.state == ParametricSweep.state[0]: #If we're done creating
            self.is_in_working_state = True
            self._set_state(ParametricSweep.state[1])  #We're now building
            #Threaded stuff here
            self.take_project_snapshot()
            
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
            self._set_state(ParametricSweep.state[0])  #Deconstructing complete
            if callback:
                callback()
        return
    
    """
    Loop through all simjobs and submit
    """
    def submit(self, callback=None):
        if self.state == ParametricSweep.state[2] or self.state==ParametricSweep.state[5]: #If we're in a ready state or running
            if not self.is_in_working_state and not self.cancel_initiated:
                if self.current_running_jobs < self.maxjobs:
                    self.is_in_working_state = True
                    self._set_state(ParametricSweep.state[4]) # We're going to be submitting new jobs now
                    #Threaded stuff here
                    self._set_state(ParametricSweep.state[5]) # We're done sumbitting for now
                    self.is_in_working_state = False
                elif self.completed_jobs == self.maxjobs:
                    self._set_state(ParametricSweep.state[8])
                    
                if callback:
                        callback()
        return
    
    """
    Loop through all simjobs and cancel
    """
    def cancel(self, callback=None):
        if self.state == ParametricSweep.state[4] or self.state == ParametricSweep.state[5]:
            if not self.is_in_working_state:
                self.is_in_working_state = True
                self._set_state(ParametricSweep.state[6])
                #Threaded stuff here
                self._set_state(ParametricSweep.state[7])
                self.is_in_working_state = False
                if callback:
                    callback()
            else:
                self.cancel_initiated = True
                #Run a thread to keep trying to cancel, since we're probably in the mid of submitting
        return
    
    def read_properties(self, from_cold=False):
        if(os.path.isfile(self.full_properties_path)):
            with open(self.full_properties_path) as json_file:  
                data = json.load(json_file)
                self.maxjobs = data[self.propname_maxjobs] 
                self.version_num = data[self.propname_version]
                self._set_state(data[self.propname_state], from_cold=from_cold)
        return

    def write_properties(self):
        data = {}
        data[self.propname_maxjobs] = self.maxjobs      
        data[self.propname_version] = self.version
        data[self.propname_state] = self.state
        
        with open(self.full_properties_path, 'w') as outfile:  
            json.dump(data, outfile)
            
        return
    
    