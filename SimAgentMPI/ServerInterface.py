# -*- coding: utf-8 -*-
"""
Created on Sun May 20 16:46:40 2018

@author: Tyler
"""
import os
from nsg.nsgclient import Client
from SimServer import ServersFile

class ServerInterface(object):
    
    def __init__(self):
        return
    
    def get_server(self, simjob):
        servers = ServersFile()
        server = servers.get_server_byname(simjob.server_connector) #will return Mone if not found
        
        return server
    
    def validate_simjob(self, simjob):
        self.start_simjob(simjob, validate_only=True)
        return
    
    
    def start_simjob(self, simjob, validate_only=False):
        
        nsg_template_param_file = "param.properties"
        nsg_template_input_file = "input.properties"
        
        server = self.get_server(simjob)
        if server:#check to make sure we have a valid server
            if(server.type == "nsg"):
                simjob.append_log("Creating NSG parameter files: " + nsg_template_param_file + "," + nsg_template_input_file)
                #generate new properties
                with open(os.path.join(simjob.sim_directory_object.sim_results_dir,simjob.job_directory,nsg_template_input_file), 'w') as the_file:
                    the_file.write('{}={}\n'.format("infile_",os.path.join(simjob.job_directory, simjob.file_snapshotzip)))
                with open(os.path.join(simjob.sim_directory_object.sim_results_dir, simjob.job_directory,nsg_template_param_file), 'w') as the_file:
                    the_file.write('{}={}\n'.format("toolId",simjob.server_nsg_tool))
                    the_file.write('{}={}\n'.format("filename_",simjob.batch_file))
                    the_file.write('{}={}\n'.format("number_nodes_",simjob.server_nodes))
                    the_file.write('{}={}\n'.format("number_cores_",simjob.server_cores))
                    the_file.write('{}={}\n'.format("pythonoption_",simjob.server_nsg_python))
                    the_file.write('{}={}\n'.format("outputfilename_",simjob.sim_name+'-nsg-return'))
                    the_file.write('{}={}\n'.format("runtime_",simjob.server_max_runtime))
                    the_file.write('{}={}\n'.format("singlelayer_","0")) 
                    
                #validate
                
                nsg = Client(server.nsg_api_appname, server.nsg_api_appid, server.user, server.password, server.nsg_api_url)
                
                simjob.append_log("Validating job build with NSG...")
                status = nsg.validateJobTemplate(simjob.job_directory_absolute)
                if status == "true":
                    simjob.append_log("NSG Template validation failed. See debug.")
                else:
                    simjob.append_log("NSG Template validation success")
                    
                if(validate_only):
                    return
                
                #status = nsg.submitJobTemplate(simjob.job_directory,metadata={"statusEmail" : simjob.server_status_email})
                
                
            
            
            elif(server.type == "ssh"):
                simjob.append_log("Starting SSH connection process")
                simjob.append_log("ssh to be implemented")
        else:
            simjob.append_log("ERROR: not a valid server connector")
            
        return 
    
    
    def stop_simjob(self, simjob):
        
        return
    
    def get_nsg_tools(self):
        #implement in api sometime... see http://www.nsgportal.org/guide.html#ToolAPI --> /tool
        
        tools = ["NEURON75_TG","NEURON74_TG","NEURON73_TG"]
        return tools
    
    def get_ssh_tools(self):
        
        tools = ["sbatch"]
        return tools
    
    """THREAD THIS TASK"""
    def wait_for_completion(self, simjob): 
        server = self.get_server(simjob)
        
        if(server.type == "nsg"):
            nsg = Client(server.nsg_api_appname, server.nsg_api_appid, server.user, server.password, server.nsg_api_url)
                
            #must get all tasks and lookup the task id from the job, make sure it's submitted
                
        return
    
    def download_results_simjob(self, simjob):
        
        return
    
    
    def update_status(self, simjob):
        
        return
    
    
    def delete_remote_results(self, simjob):
        
        return
    
    