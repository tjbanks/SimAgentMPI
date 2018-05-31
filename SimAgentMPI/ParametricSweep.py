# -*- coding: utf-8 -*-
"""
Created on Wed May 30 21:01:24 2018

@author: Tyler
"""
import json
import os

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
    
    def __init__(self, project_dir, name, external_state_var=None):
                        
        self.name = name
        self.project_dir = project_dir
        self.sweep_dir = None
        self.maxjobs = 1
        self.server = None
        
        self.parameters = []#objects of some sort
        
        self.current_running_jobs = 0
        self.cancel_initiated = False #If we're in a submitting state
        
        self.is_in_working_state = False #will write this to file everytime state changes so we restart state if app closes
        
        self.state = ""
        self.external_state_var = None
        if external_state_var:
            self.external_state_var = external_state_var
            self.external_state_var.set(self.state)
            
        self._set_state(ParametricSweep.state[0])
        
        return
    
    def _set_state(self, state):
        print("Parametric sweep {} changing to state: {}".format(self.name, state))
        self.state = state
        if self.external_state_var:
            self.external_state_var.set(self.state)
        return
    
    def get_state(self):
        return self.state
    
    """
    Create snapshot of project_dir
    Create all simjobs in the sweep_dir
    """
    def build(self, callback=None):
        if self.state == ParametricSweep.state[0]: #If we're done creating
            self.is_in_working_state = True
            self._set_state(ParametricSweep.state[1])  #We're now building
            #Threaded stuff here
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
    
    