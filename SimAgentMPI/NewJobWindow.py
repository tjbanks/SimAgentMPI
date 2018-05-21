# -*- coding: utf-8 -*-
"""
Created on Sun May 20 16:46:40 2018

@author: Tyler
"""

import tkinter as tk
from tkinter import IntVar,filedialog,OptionMenu
import time, datetime

from SimServer import SimServer,ServersFile
from NewServerConfig import ServerEntryBox


"""
self.version = SimJob.version
        self.log = SimJob.log_file
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
        
"""

class JobEntryBox:
        
        def __init__(self, parent, sim_directory, job_name=None):
            self.window_title = "New Job"
            self.parent = parent
            self.sim_directory = sim_directory
            self.job_name = job_name
            self.simjob = None
            self.display()
            return
        
        def display(self):            
            top = self.top = tk.Toplevel(self.parent)
            top.geometry('375x375')
            top.resizable(0,0)
            top.title(self.window_title)
            
            self.name = tk.StringVar(top)
            self.notes = tk.StringVar(top)
            self.status = tk.StringVar(top)
            self.batch_file = tk.StringVar(top)
            #self.update_interval = tk.StringVar(top)
            self.server_connector = tk.StringVar(top)
            self.server_nodes = tk.StringVar(top)
            self.server_cores = tk.StringVar(top)
            self.server_nsg_tool = tk.StringVar(top)
            self.server_nsg_python = tk.StringVar(top)
            self.server_mpi_partition = tk.StringVar(top)
            self.server_max_runtime = tk.StringVar(top)
            #self.server_email = tk.StringVar(top)
            self.server_status_email = tk.StringVar(top)
            self.confirm = False
            
            """
            self.servers_file = ServersFile()
            self.server = None
            
            if server_id:
                self.is_loaded_server = True
                self.server = self.servers_file.get_server(server_id)
            else:
                self.is_loaded_server = False
            
            if not self.server:
                self.server = SimServer()  
            """
                
            
            #if not self.simjob:#create a new one
                
            #else:
            
            
            
            """###############################################"""
            
            def on_server_type_change(type_):
                if(type_ == "nsg"):
                    conn_option_frame.grid_forget()
                    nsgconn_option_frame.grid(column=0,row=14,sticky='news',padx=10,pady=5,columnspan=2)
                elif(type_ == "ssh"):
                    nsgconn_option_frame.grid_forget()
                    conn_option_frame.grid(column=0,row=15,sticky='news',padx=10,pady=5,columnspan=2)
                else:
                    conn_option_frame.grid_forget()
                    nsgconn_option_frame.grid_forget()
                    
                return
            
            def select_batch():
                self.batch_file.set(filedialog.askopenfilename())
                self.top.lift()
                return
                
            def new_server():
                s = ServerEntryBox(self.top)
                #Refresh options
                
                # on change dropdown value
            def change_dropdown(*args):
                server_name = self.server_connector.get()
                
                if(server_name==""):
                    on_server_type_change("")
                    return
                servers = ServersFile()
                s = servers.get_server_byname(server_name)
                #get the connection and check if it's a ssh / nsg
                on_server_type_change(s.type)
            
            
            tk.Label(top, text='New Remote Job').grid(row=0,column=0,sticky="WE",pady=15, columnspan=3)
            
            l = tk.Label(top, text='Sim Job Name',width=15, background='light gray')
            l.grid(row=1,column=0,pady=5,padx=5,columnspan=1)
            l.config(relief=tk.GROOVE)
            
            self.name_e = tk.Entry(top,width=25,textvariable=self.name)
            self.name_e.grid(row=1,column=1,padx=5,columnspan=1)
            
            
            
            l = tk.Label(top, text='Batch File',width=15, background='light gray')
            l.grid(row=2,column=0,pady=5,padx=5,columnspan=1)
            l.config(relief=tk.GROOVE)
            
            self.name_e = tk.Entry(top,width=25,textvariable=self.batch_file)
            self.name_e.grid(row=2,column=1,padx=5,columnspan=1)
            self.name_e.config(state=tk.DISABLED)
            
            b = tk.Button(top, text="Select", command=select_batch)
            b.grid(pady=5, padx=5, column=2, row=2, sticky="WE",columnspan=1)
            
            
            
            l = tk.Label(top, text='Nodes',width=15, background='light gray')
            l.grid(row=3,column=0,pady=5,padx=5,columnspan=1)
            l.config(relief=tk.GROOVE)
            
            self.name_e = tk.Entry(top,width=25,textvariable=self.server_nodes)
            self.name_e.grid(row=3,column=1,padx=5,columnspan=1)
            
            
            l = tk.Label(top, text='Cores',width=15, background='light gray')
            l.grid(row=4,column=0,pady=5,padx=5,columnspan=1)
            l.config(relief=tk.GROOVE)
            
            self.name_e = tk.Entry(top,width=25,textvariable=self.server_cores)
            self.name_e.grid(row=4,column=1,padx=5,columnspan=1)
            
            
            l = tk.Label(top, text='Server Connection',width=15, background='light gray')
            l.grid(row=5,column=0,pady=5,padx=5,columnspan=1)
            l.config(relief=tk.GROOVE)
            
 
            # Dictionary with options
            choices = self.get_connections()
 
            popupMenu = OptionMenu(top, self.server_connector, *choices)
            popupMenu.grid(row = 5, column =1)
            self.server_connector.trace('w', change_dropdown)
            
            b = tk.Button(top, text="New", command=new_server)
            b.grid(pady=5, padx=5, column=2, row=5, sticky="WE",columnspan=1)
            
            
            conn_option_frame = tk.LabelFrame(top, text="SSH Connection Parameters")
            nsgconn_option_frame = tk.LabelFrame(top, text="NSG Connection Parameters")
            
        
            """
            if(self.use_ssh.get() is "0"):
                nsgconn_option_frame.grid(column=0,row=14,sticky='news',padx=10,pady=5,columnspan=2)
            else:
                conn_option_frame.grid(column=0,row=15,sticky='news',padx=10,pady=5,columnspan=2)
            
            #run_option_frame = tk.LabelFrame(top, text="Runtime Parameters")
            #run_option_frame.grid(column=0,row=4,sticky='news',padx=10,pady=5,columnspan=2)
            """
            ###GENERAL###
                    
            
            l = tk.Label(conn_option_frame, text='Partition',width=15, background='light gray')
            l.grid(row=2,column=0,pady=5,padx=5)
            l.config(relief=tk.GROOVE)
            
            self.host_e = tk.Entry(conn_option_frame,width=25,textvariable=self.server_mpi_partition)
            self.host_e.grid(row=2,column=1,padx=5)
            
            
            ####NSG###
            
            l = tk.Label(nsgconn_option_frame, text='Tool',width=15, background='light gray')
            l.grid(row=2,column=0,pady=5,padx=5)
            l.config(relief=tk.GROOVE)
            
            self.nsg_url_e = tk.Entry(nsgconn_option_frame,width=25,textvariable=self.server_nsg_tool)
            self.nsg_url_e.grid(row=2,column=1,padx=5)
            
            l = tk.Label(nsgconn_option_frame, text='Uses Python',width=15, background='light gray')
            l.grid(row=3,column=0,pady=5,padx=5)
            l.config(relief=tk.GROOVE)
            
            self.nsg_user_e = tk.Entry(nsgconn_option_frame,width=25,textvariable=self.server_nsg_python)
            self.nsg_user_e.grid(row=3,column=1,padx=5)
            
            l = tk.Label(nsgconn_option_frame, text='Send Status Email on Complete',width=15, background='light gray')
            l.grid(row=4,column=0,pady=5,padx=5)
            l.config(relief=tk.GROOVE)
            
            self.nsg_pass_e = tk.Entry(nsgconn_option_frame,width=25,show="*",textvariable=self.server_status_email)
            self.nsg_pass_e.grid(row=4,column=1,padx=5)
             
            
            
            
            #Return
                        
            button_frame = tk.Frame(top)
            button_frame.grid(row=20,column=0,columnspan=2)
            
            b = tk.Button(button_frame, text="Ok", command=self.ok)
            b.grid(pady=5, padx=5, column=0, row=0, sticky="WE")
            
            b = tk.Button(button_frame, text="Cancel", command=self.cancel)
            b.grid(pady=5, padx=5, column=1, row=0, sticky="WE")
            
            
        def verify_good(self):
            return True
        """
        def save_file(self):
            
            if(not self.is_loaded_server):
                ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%y%m%d%H%M%S')
                self.server.id = st
            
            self.server.name = self.name.get()
            if(self.use_ssh.get()=="0"):#NSG
                self.server.type = "nsg"
                self.server.user = self.nsg_user.get()
                self.server.password = self.nsg_password.get()
                self.server.nsg_api_url = self.nsg_url.get()
                self.server.nsg_api_appname = self.nsg_app_name.get()
                self.server.nsg_api_appid = self.nsg_app_id.get()
                
            else:#SSH
                self.server.type = "ssh"
                self.server.host = self.hostname.get()
                self.server.user = self.user.get()
                self.server.password = self.password.get()
                self.server.priv_key_location = self.keyfile.get()
                                
            self.servers_file.update_server_details(self.server)
            return
        """    
        
        def get_connections(self):            
            servers = ServersFile().servers
            names = [""]
            for s in servers:
                names.append(s.name)
            return names
        
        def is_valid():
            return True
        
        def to_simjob():
            return 
        
        def ok(self):
            self.confirm = True
            self.top.destroy()
        def cancel(self):
            self.top.destroy()