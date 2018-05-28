# -*- coding: utf-8 -*-
"""
Created on Sun May 20 16:46:40 2018

@author: Tyler
"""
import os
import paramiko
import zipfile,tarfile
import time

from SimAgentMPI.nsg.nsgclient import Client,CipresError
from SimAgentMPI.SimServer import ServersFile
import SimAgentMPI

class ServerInterface(object):
    ssh_status = ["SSH_sbatch_RUNNING","SSH_sbatch_COMPLETED","SSH_sbatch_DOWNLOADED","SSH_batch_CANCELLED"]
    nsg_status = ["NSG_RUNNING","NSG_COMPLETED","NSG_DOWNLOADED","NSG_CANCELLED"]
    
    def __init__(self):
        self.remote_dir = "simagent_remote"#THIS IS THE DIRECTORY WHERE ALL CODE WILL BE EXECUTED FROM
        
        return
    
    def get_server(self, simjob):
        simjob.append_log("Loading server " + simjob.server_connector)
        servers = ServersFile()
        server = servers.get_server_byname(simjob.server_connector) #will return Mone if not found
        if not server:
            simjob.append_log("Server connection not found")        
        return server
    
    
    def start_simjob(self, simjob, validate_nsg_only=False):
        server = self.get_server(simjob)
        ts = time.time()
        #st = datetime.datetime.fromtimestamp(ts).strftime('%y%m%d-%H%M%S')
        simjob.sim_start_time = ts
        simjob.write_properties()
        
        if server:#check to make sure we have a valid server
            if(server.type == "nsg"):
                self.submit_nsg(simjob, validate_nsg_only, server)
            elif(server.type == "ssh"):
                self.submit_ssh(simjob, validate_nsg_only, server)
                
        else:
            simjob.append_log("ERROR: Can't start job... not a valid server connector")
            
        return 
    
    def update_for_completion(self, simjob, nsg_job_list=None): 
        server = self.get_server(simjob)
        if server:#check to make sure we have a valid server
            if(server.type == "nsg"):
                self.update_nsg(simjob, server, nsg_job_list=nsg_job_list)
            elif(server.type == "ssh"):
                self.update_ssh(simjob, server)
        else:
            simjob.append_log("ERROR: Can't update... not a valid server connector")
            
        return 
    
    def stop_simjob(self, simjob):
        server = self.get_server(simjob)
        if server:#check to make sure we have a valid server
            if(server.type == "nsg"):
                self.stop_nsg(simjob, server)
            elif(server.type == "ssh"):
                self.stop_ssh(simjob, server)
        else:
            simjob.append_log("ERROR: Can't stop... not a valid server connector")
            
        return
    
    def download_results_simjob(self, simjob):
        server = self.get_server(simjob)
        if server:#check to make sure we have a valid server
            if(server.type == "nsg"):
                self.download_nsg(simjob, server)
            elif(server.type == "ssh"):
                self.download_ssh(simjob, server)
        else:
            simjob.append_log("ERROR: Can't download... not a valid server connector")
        
        return
        
    def download_status_simjob(self, simjob):
        server = self.get_server(simjob)
        if server:#check to make sure we have a valid server
            if(server.type == "nsg"):
                self.download_status_nsg(simjob, server)
            elif(server.type == "ssh"):
                self.download_status_ssh(simjob, server)
        else:
            simjob.append_log("ERROR: Can't update status files... not a valid server connector")
        
        return
        
    def delete_remote_results(self, simjob):
        server = self.get_server(simjob)
        if server:#check to make sure we have a valid server
            if(server.type == "nsg"):
                self.delete_nsg(simjob, server)
            elif(server.type == "ssh"):
                self.delete_ssh(simjob, server)
        else:
            simjob.append_log("ERROR: Can't delete results... not a valid server connector")
            
        return 
    
    def delete_all_remote_results(self, server):
        if server:#check to make sure we have a valid server
            if(server.type == "nsg"):
                self.delete_all_nsg(server)
            elif(server.type == "ssh"):
                self.delete_all_ssh(server)
        else:
            print("ERROR: Can't delete jobs... not a valid server connector")
            
        return 
    
    
    def submit_nsg(self, simjob, validate_only, server):
        nsg_template_param_file = "param.properties"
        nsg_template_input_file = "input.properties"
        return_filename = simjob.sim_name+'-nsg-return'
        
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
            the_file.write('{}={}\n'.format("outputfilename_",return_filename))
            the_file.write('{}={}\n'.format("runtime_",simjob.server_max_runtime))
            the_file.write('{}={}\n'.format("singlelayer_","0")) 
            
        #validate
        simjob.file_resultszip = return_filename + ".tar.gz"
        simjob.dir_results = return_filename
        simjob.write_properties()
        
        nsg = Client(server.nsg_api_appname, server.nsg_api_appid, server.user, server.password, server.nsg_api_url)
        
        simjob.append_log("Validating job build with NSG...")
        
        try:
            status = nsg.validateJobTemplate(simjob.job_directory_absolute)
            if status.isError():
                simjob.append_log("NSG template validation failed. See debug.")
            else:
                simjob.append_log("NSG template validation success")
        except CipresError as e:
            simjob.append_log("Error validating NSG template: " + e.message)
            simjob.append_log("Job stopped")
            simjob.status = ServerInterface.nsg_status[3]
            simjob.write_properties()
            return
            
        if(validate_only):
            return
        try:
            status = nsg.submitJobTemplate(simjob.job_directory_absolute,metadata={"statusEmail" : simjob.server_status_email})
        
            simjob.server_remote_identifier = status.jobUrl
            simjob.write_properties()
            
            if status.isError():
                simjob.append_log("NSG template submit failed. See debug.")
                
            else:
                simjob.append_log("NSG template submit success")
                simjob.status = ServerInterface.nsg_status[0]
                simjob.write_properties()
        except CipresError as e:
            simjob.append_log("Error submitting NSG template: " + e.message)
            simjob.append_log("Job stopped")
            
        return
    
    def zipdir(self, path, ziph, foldername, zipfold):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                dir_ = root.split(zipfold, 1)[-1]
                if(len(dir_) and dir_[0] == "\\"):
                    dir_ = dir_[1:]
                #print(os.path.join(dir_,file))
                ziph.write(os.path.join(root, file), arcname=os.path.join(dir_,file))
        return
    
    def take_snapshotzip(self, save_to_file, dir_path,zipfold):
        #Zip up everything except results foldername
        zipf = zipfile.ZipFile(save_to_file+".zip", 'w', zipfile.ZIP_DEFLATED)
        self.zipdir(dir_path, zipf, foldername=os.path.basename(save_to_file), zipfold=zipfold) #must be in format file.zip -> file (folder) -> sim stuff
        zipf.close()
        return
    
    def submit_ssh(self, simjob, validate_only, server):
        
        ## YOU HAVE TO EXTRACT THE FILE FIRST THEN MAKE THE CHANGES, DELETE OLD ZIP THEN REZIP
        snapzip = os.path.join(simjob.job_directory_absolute,simjob.file_snapshotzip)
        snapdir = os.path.join(simjob.job_directory_absolute,simjob.file_snapshotzip.split(".")[0])
        #unzip
        zip_ref = zipfile.ZipFile(snapzip, 'r')
        zip_ref.extractall(snapdir)
        zip_ref.close()
        
        ##Edit batch file
        batch_file = os.path.join(simjob.job_directory_absolute,simjob.sim_name,simjob.sim_name,simjob.batch_file)
        SimAgentMPI.Utils.replace(batch_file, "#SBATCH -p " + "(.*)", "{}{}".format("#SBATCH -p ", simjob.server_mpi_partition),unix_end=True)
        SimAgentMPI.Utils.replace(batch_file, "#SBATCH -N " + "(.*)", "{}{}".format("#SBATCH -N ", simjob.server_nodes),unix_end=True)
        SimAgentMPI.Utils.replace(batch_file, "#SBATCH -n " + "(.*)", "{}{}".format("#SBATCH -n ", simjob.server_cores),unix_end=True)
        #SBATCH --time 0-23:00
        SimAgentMPI.Utils.replace(batch_file, "#SBATCH --time " + "(.*)", "{}0-{}:00".format("#SBATCH --time ", simjob.server_max_runtime),unix_end=True)
        ##
        os.remove(snapzip)
        self.take_snapshotzip(snapdir,snapdir, zipfold=snapdir)
        
        try:
            client = self.connect_ssh(server,simjob)
            
            simjob.append_log("Verifying/creating folder /home/{}/{} on {}".format(server.user,self.remote_dir,server.host))
            command= 'mkdir '+ self.remote_dir
            self.exec_ssh_command(client, command, simjob, server)
                    
            rem_loc = "./"+self.remote_dir+"/"+simjob.file_snapshotzip
            zip_file = os.path.join(simjob.job_directory_absolute,simjob.file_snapshotzip)
            zip_dir = simjob.file_snapshotzip.split(".zip")[0]
            
            simjob.append_log("Uploading code ({}) to /home/{}/{} on {}".format(simjob.file_snapshotzip,server.user,self.remote_dir,server.host))
            sftp_client=client.open_sftp()
            sftp_client.put(zip_file,rem_loc)
            sftp_client.close()
            simjob.append_log("Code uploaded successfully.")
                   
            
            simjob.append_log("{}> Unzipping and running code".format(server.host))
            command = 'unzip -o -d '+self.remote_dir+'/'+zip_dir +' '+self.remote_dir+'/'+simjob.file_snapshotzip
            self.exec_ssh_command(client, command, simjob, server)
            
            simjob.append_log("{}> Deleting zip".format(server.host))
            command = 'rm -rf '+self.remote_dir+'/'+simjob.file_snapshotzip
            self.exec_ssh_command(client, command, simjob, server)
                
            if simjob.server_ssh_tool == self.get_ssh_tools()[0]: #SBATCH
                sbatch_command = "sbatch"
                simjob.append_log("{}> Running sbatch".format(server.host))
                command = 'cd ' + self.remote_dir+'/'+ zip_dir+'/'+zip_dir+' && ' + sbatch_command + ' ' + simjob.batch_file+ ' && cd ~' #We want to execute from that dir
                batch_id = self.exec_ssh_command(client, command, simjob, server)
                batch_id = batch_id[0]
                batch_id = batch_id.replace("Submitted batch job ", "")
                batch_id = batch_id.replace("\n", "")
                simjob.append_log("Logging remote id {}".format(batch_id))
                simjob.server_remote_identifier = batch_id
                simjob.status = ServerInterface.ssh_status[0]
                simjob.server_stdout_file = simjob.server_stdout_file.replace("%j",simjob.server_remote_identifier)
                simjob.server_stderr_file = simjob.server_stderr_file.replace("%j",simjob.server_remote_identifier)
                simjob.write_properties()
                #Submitted batch job 18214
                
            client.close()
        except Exception as e:
                simjob.append_log('*** Caught exception: %s: %s' % (e.__class__, e))
                #traceback.print_exc()
                simjob.status = ServerInterface.ssh_status[3]
                simjob.write_properties()
                try:
                    client.close()
                except:
                    pass
                
        return
    
    def update_nsg(self, simjob, server, nsg_job_list=None):
        simjob.append_log("Updating NSG information on job...")
        nsg = Client(server.nsg_api_appname, server.nsg_api_appid, server.user, server.password, server.nsg_api_url)
        
        if not nsg_job_list: #Just save a couple calls to their server
            nsg_job_list = nsg.listJobs()
            
        for job in nsg.listJobs():
            if job.jobUrl == simjob.server_remote_identifier:
                job.update()
                for m in job.messages:
                    simjob.append_log(m)
                if(job.isError()):
                    simjob.append_log("NSG Job found in error state")
                    simjob.status = ServerInterface.nsg_status[3]
                    simjob.write_properties()
                if(job.isDone()):
                    simjob.append_log("NSG Job found in finished state")
                    simjob.status = ServerInterface.nsg_status[1]
                    simjob.write_properties()
            
        return
    
    def update_ssh(self, simjob, server):
        
        try:
            client = self.connect_ssh(server,simjob)
            
            if simjob.server_ssh_tool == self.get_ssh_tools()[0]: #SBATCH
                command = 'squeue -u ' + server.user
                lines = self.exec_ssh_command(client, command, simjob, server)
                done = True
                for line in lines:
                    if(simjob.server_remote_identifier in line):
                        done = False
                if done:
                    simjob.append_log("SSH Job Completed")
                    simjob.status = ServerInterface.ssh_status[1]
                    simjob.write_properties()
            client.close()
        except Exception as e:
                simjob.append_log('*** Caught exception: %s: %s' % (e.__class__, e))
                #traceback.print_exc()
                try:
                    client.close()
                except:
                    pass
    
    def stop_nsg(self, simjob, server):
        nsg = Client(server.nsg_api_appname, server.nsg_api_appid, server.user, server.password, server.nsg_api_url)
        for job in nsg.listJobs():
            if job.jobUrl == simjob.server_remote_identifier:
                job.update()
                for m in job.messages:
                        simjob.append_log(m)
                        
                if not job.isDone():
                    job.delete()
                    simjob.append_log("NSG Job Canceled")
                    simjob.status = ServerInterface.nsg_status[3]
                    simjob.write_properties()
        
        return
    
    def stop_ssh(self, simjob, server):
        
        try:
            client = self.connect_ssh(server,simjob)
            
            if simjob.server_ssh_tool == self.get_ssh_tools()[0]: #SBATCH
                command = 'scancel ' + simjob.server_remote_identifier
                lines = self.exec_ssh_command(client, command, simjob, server)
                #command = 'squeue -u ' + server.user
                done = True
                for line in lines:
                    if(simjob.server_remote_identifier in line):
                        done = False
                if done:
                    simjob.append_log("SSH Job Canceled")
                    simjob.status = ServerInterface.ssh_status[3]
                    simjob.write_properties()
                else:
                    simjob.append_log("Trouble finding job to cancel")
            client.close()
        except Exception as e:
                simjob.append_log('*** Caught exception: %s: %s' % (e.__class__, e))
                #traceback.print_exc()
                try:
                    client.close()
                except:
                    pass
                
        return
    
    
    def download_nsg(self, simjob, server):
        nsg = Client(server.nsg_api_appname, server.nsg_api_appid, server.user, server.password, server.nsg_api_url)
        
        for job in nsg.listJobs():
            if job.jobUrl == simjob.server_remote_identifier:
                job.update()
                if not job.isError():
                    if job.isDone():
                        results = job.listResults()
                        for m in job.messages:
                            simjob.append_log(m)
                        for r in results:
                            simjob.append_log("Downloading: " + r)                        
                        job.downloadResults(simjob.job_directory_absolute)
                        
                        try:
                            simjob.append_log("Extracting results")
                            nsg_tar_returned = os.path.join(simjob.job_directory_absolute,simjob.file_resultszip)
                            zip_dir_nsg_return = os.path.join(simjob.job_directory_absolute,simjob.dir_results)
                            tar = tarfile.open(nsg_tar_returned,"r:gz")
                            tar.extractall(zip_dir_nsg_return)
                            tar.close()
                            simjob.append_log("Extracted results to " + zip_dir_nsg_return)
                        
                            simjob.status = ServerInterface.nsg_status[2]
                            
                        except Exception as e:
                            simjob.append_log("Error extracting tar file, the job may not have completed.")
                            simjob.status = ServerInterface.nsg_status[3]
                        
                        simjob.write_properties()
                    else:
                        simjob.append_log("The job is not done can't download yet.")
                else:
                    simjob.append_log("There was an error running or downloading. See console output")
       
        return
    
    def download_ssh(self, simjob, server):
        try:
            client = self.connect_ssh(server,simjob)
            
            if simjob.server_ssh_tool == self.get_ssh_tools()[0]: #SBATCH
                zip_dir = simjob.file_snapshotzip.split(".zip")[0]
                simjob.file_resultsdir = zip_dir + "-results"
                simjob.file_resultszip = simjob.file_resultsdir + ".zip"
                results_dir_absolute = os.path.join(simjob.job_directory_absolute,simjob.file_resultsdir)
                results_zip_absolute = os.path.join(simjob.job_directory_absolute,simjob.file_resultszip)
                
                command = "cd " + self.remote_dir + '/' + zip_dir + " && zip -r ../" + simjob.file_snapshotzip +" "+ zip_dir + " && cd ~"
                simjob.append_log("{}> Zipping remote results...".format(server.host))
                self.exec_ssh_command(client,command,simjob,server)
                        
                simjob.append_log("Downloading results")
                rem_loc = "./"+self.remote_dir+"/"+simjob.file_snapshotzip
                ftp_client=client.open_sftp()
                ftp_client.get(rem_loc,results_zip_absolute)
                ftp_client.close()
                
                zip_ref = zipfile.ZipFile(results_zip_absolute, 'r')
                zip_ref.extractall(results_dir_absolute)
                zip_ref.close()
                simjob.append_log("Results saved to: {}".format(results_dir_absolute))
                simjob.status = ServerInterface.ssh_status[2]
                simjob.write_properties()
            
            client.close()
        except Exception as e:
                simjob.append_log('*** Caught exception: %s: %s' % (e.__class__, e))
                #traceback.print_exc()
                try:
                    client.close()
                except:
                    pass
        return
    
    def download_status_nsg(self, simjob, server):
        nsg = Client(server.nsg_api_appname, server.nsg_api_appid, server.user, server.password, server.nsg_api_url)
        outfile = "stdout.txt"
        errfile = "stderr.txt"
        
        for job in nsg.listJobs():
            if job.jobUrl == simjob.server_remote_identifier:
                job.update()
                resultFiles = job.listResults(final=False)
                
                for filename in resultFiles: 
                    if filename == outfile:
                        resultFiles[filename].download(simjob.job_directory_absolute)
                        out_dl = os.path.join(simjob.job_directory_absolute,outfile)
                        std_out = os.path.join(simjob.job_directory_absolute,simjob.stdout_file)
                        if os.path.exists(std_out):
                            os.remove(std_out)
                        os.rename(out_dl, std_out)
                        os.remove(out_dl)
                    if filename == errfile:
                        resultFiles[filename].download(simjob.job_directory_absolute)
                        err_dl = os.path.join(simjob.job_directory_absolute,errfile)
                        std_err = os.path.join(simjob.job_directory_absolute,simjob.stderr_file)
                        if os.path.exists(std_err):
                            os.remove(std_err)
                        os.rename(err_dl, std_err)
                        os.remove(err_dl)
        return
    
    def download_status_ssh(self, simjob, server):
        #the outfiles are in the simjob now
        try:
            client = self.connect_ssh(server,simjob)
            
            if simjob.server_ssh_tool == self.get_ssh_tools()[0]: #SBATCH
                local_out = os.path.join(simjob.job_directory_absolute,simjob.stdout_file)
                local_err = os.path.join(simjob.job_directory_absolute,simjob.stderr_file)
                rem_out = "./"+self.remote_dir+"/"+simjob.sim_name+"/"+simjob.sim_name+"/"+simjob.server_stdout_file
                rem_err = "./"+self.remote_dir+"/"+simjob.sim_name+"/"+simjob.sim_name+"/"+simjob.server_stderr_file
                ftp_client=client.open_sftp()
                ftp_client.get(rem_out,local_out)
                ftp_client.get(rem_err,local_err)
                ftp_client.close()
                
            client.close()
        except Exception as e:
                simjob.append_log('*** Caught exception: %s: %s' % (e.__class__, e))
                #traceback.print_exc()
                try:
                    client.close()
                except:
                    pass
        return
        return
        
    def delete_all_nsg(self, server):
        nsg = Client(server.nsg_api_appname, server.nsg_api_appid, server.user, server.password, server.nsg_api_url)
        print("Deleting ALL NSG Jobs...")
        for job in nsg.listJobs():
            job.delete()
            
    def delete_all_ssh(self, server):
        try:
            client = self.connect_ssh(server,None)
            #STOP ALL JOBS!
            command = 'rm -rf '+self.remote_dir
            self.exec_ssh_command(client,command,None,server)
                
            client.close()
        except Exception as e:
                try:
                    client.close()
                except:
                    pass
        return
            
    def delete_nsg(self, simjob, server):
        nsg = Client(server.nsg_api_appname, server.nsg_api_appid, server.user, server.password, server.nsg_api_url)
        for job in nsg.listJobs():
            if job.jobUrl == simjob.server_remote_identifier:
                #job.update()
                job.delete()
                simjob.append_log("NSG Job Deleted on remote server")
                if simjob.status == ServerInterface.nsg_status[0] or simjob.status == ServerInterface.nsg_status[2]:
                    simjob.status = ServerInterface.nsg_status[3]
                    simjob.write_properties()
        return
    
    def delete_ssh(self, simjob, server):
        
        try:
            client = self.connect_ssh(server,simjob)
            
            if simjob.server_ssh_tool == self.get_ssh_tools()[0]: #SBATCH
                simjob.append_log("Deleting remote ssh files files")
                zip_dir = simjob.file_snapshotzip.split(".zip")[0]
                command = 'rm -rf '+self.remote_dir+'/'+zip_dir+'*'
                self.exec_ssh_command(client,command,simjob,server)
                if simjob.status == ServerInterface.ssh_status[0] or simjob.status == ServerInterface.ssh_status[2]:
                    simjob.status = ServerInterface.ssh_status[3]
                    simjob.write_properties()
                    
            client.close()
        except Exception as e:
                simjob.append_log('*** Caught exception: %s: %s' % (e.__class__, e))
                #traceback.print_exc()
                try:
                    client.close()
                except:
                    pass
        return
    
    
    def get_nsg_tools(self):
        #implement in api sometime... see http://www.nsgportal.org/guide.html#ToolAPI --> /tool
        tools = ["NEURON75_TG","NEURON74_TG","NEURON73_TG"]
        return tools
    
    def get_ssh_tools(self):
        tools = ["sbatch"]
        return tools
    
    def connect_ssh(self,server,simjob):
        #simjob.append_log("Starting SSH connection process")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if simjob:
            simjob.append_log("Connecting to {}:{} over SSH".format(server.host,server.port))
                
        if(server.priv_key_location == ""):
            #simjob.append_log("No private keyfile used")
            client.connect(server.host, port=server.port, username=server.user, password=server.password)
        else:
            #simjob.append_log("Using private key authentication. Private key location: " + server.priv_key_location)
            k = paramiko.RSAKey.from_private_key_file(server.priv_key_location, server.password)
            client.connect(server.host, port=server.port, username=server.user, pkey=k)
        return client
    
    def exec_ssh_command(self,client, command, simjob, server):
        if simjob:
            simjob.append_log("{}> {}".format(server.host, command))
        else:
            print("{}> {}".format(server.host, command))
        stdin , stdout, stderr = client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        lines = [""]
        if exit_status == 0:
            lines = stdout.readlines()
            if simjob:
                simjob.append_log(lines) 
            else:
                print(lines)
        else:
            lines = stderr.readlines()
            if simjob:
                simjob.append_log(lines)
            else:
                print(lines)
        return lines
    