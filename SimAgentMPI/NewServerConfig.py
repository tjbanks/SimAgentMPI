# -*- coding: utf-8 -*-
"""
Created on Sun May 20 16:46:40 2018

@author: Tyler
"""

"""
        self.id = "-1"
        self.name = ""
        self.type = "nsg"
        self.host = ""
        self.port = "22"
        self.user = "user"
        self.password = "pass"
        self.priv_key_location = "."
        self.nsg_api_url = "https://nsgr.sdsc.edu:8443/cipresrest/v1"
        self.nsg_api_appname = "nsgappname"
        self.nsg_api_appid = "nsgappname-id"
"""
import tkinter as tk
from tkinter import IntVar,filedialog
import time, datetime

from SimServer import SimServer,ServersFile

class ServerEntryBox:
        
        def __init__(self, parent, server_id=None, display=True):
            self.parent = parent
                        
            if display:
                self.display(server_id=server_id)
            return
        
        def display(self, server_id=None):            
            top = self.top = tk.Toplevel(self.parent)
            top.geometry('315x385')
            top.resizable(0,0)
            
            
            self.name = tk.StringVar(top)
            self.hostname = tk.StringVar(top)
            self.port = tk.StringVar(top)
            self.user = tk.StringVar(top)
            self.password = tk.StringVar(top)
            self.keyfile = tk.StringVar(top)
            
            self.nsg_url = tk.StringVar(top)
            self.nsg_user = tk.StringVar(top)
            self.nsg_password = tk.StringVar(top)
            self.nsg_app_name = tk.StringVar(top)
            self.nsg_app_id = tk.StringVar(top)
            self.use_ssh = tk.StringVar(top)
            self.confirm = False
            
            self.servers_file = ServersFile()
            self.server = None
            
            if server_id:
                self.is_loaded_server = True
                self.server = self.servers_file.get_server(server_id)
            else:
                self.is_loaded_server = False
            
            if not self.server:
                self.server = SimServer()         
                
                
            #Inputs            
            #tc.rnet.missouri.edu tbg28 INPUT NONE General 2 40
            self.server_type = IntVar()
            self.name.set(self.server.name)
            self.hostname.set(self.server.host)
            self.port.set(self.server.port)
            self.user.set(self.server.user)
            self.password.set(self.server.password)
            self.keyfile.set(self.server.priv_key_location)
            
            self.nsg_url.set(self.server.nsg_api_url)
            self.nsg_user.set(self.server.user)
            self.nsg_password.set(self.server.password)
            self.nsg_app_name.set(self.server.nsg_api_appname)
            self.nsg_app_id.set(self.server.nsg_api_appid)
            self.use_ssh.set("0")
            
            
            """###############################################"""
            
            if self.server.type == "nsg":
                self.server_type.set(0) #0 for nsg 1 for ssh
            else:
                self.server_type.set(1) #0 for nsg 1 for ssh
                                  
            
            def on_server_type_change():
                if(self.server_type.get()==0):
                    conn_option_frame.grid_forget()
                    nsgconn_option_frame.grid(column=0,row=14,sticky='news',padx=10,pady=5,columnspan=2)
                    self.use_ssh.set(str(0))
                else:
                    nsgconn_option_frame.grid_forget()
                    conn_option_frame.grid(column=0,row=15,sticky='news',padx=10,pady=5,columnspan=2)
                    self.use_ssh.set(str(1))
                return
            tk.Label(top, text='Add/Edit Server Connection').grid(row=0,column=0,sticky="WE",columnspan=2,pady=15)
            
            l = tk.Label(top, text='Display Name',width=15, background='light gray')
            l.grid(row=1,column=0,pady=5,padx=5)
            l.config(relief=tk.GROOVE)
            
            self.name_e = tk.Entry(top,width=25,textvariable=self.name)
            self.name_e.grid(row=1,column=1,padx=5)
            
            tk.Label(top, text='Server Connection Type').grid(row=2,column=0,sticky="WE",columnspan=2)
            tk.Radiobutton(top, text="NSG", variable=self.server_type, command=on_server_type_change, value=0).grid(column=0,row=3)
            tk.Radiobutton(top, text="Other (SSH)", variable=self.server_type, command=on_server_type_change, value=1).grid(column=1,row=3)
            
            
            
            
            conn_option_frame = tk.LabelFrame(top, text="SSH Connection Parameters")
            nsgconn_option_frame = tk.LabelFrame(top, text="NSG Connection Parameters")
            if(self.use_ssh.get() is "0"):
                nsgconn_option_frame.grid(column=0,row=14,sticky='news',padx=10,pady=5,columnspan=2)
            else:
                conn_option_frame.grid(column=0,row=15,sticky='news',padx=10,pady=5,columnspan=2)
            
            #run_option_frame = tk.LabelFrame(top, text="Runtime Parameters")
            #run_option_frame.grid(column=0,row=4,sticky='news',padx=10,pady=5,columnspan=2)
            
            ###GENERAL###
                    
            
            l = tk.Label(conn_option_frame, text='Hostname',width=15, background='light gray')
            l.grid(row=2,column=0,pady=5,padx=5)
            l.config(relief=tk.GROOVE)
            
            self.host_e = tk.Entry(conn_option_frame,width=25,textvariable=self.hostname)
            self.host_e.grid(row=2,column=1,padx=5)
            
            l = tk.Label(conn_option_frame, text='Port',width=15, background='light gray')
            l.grid(row=3,column=0,pady=5,padx=5)
            l.config(relief=tk.GROOVE)
            
            self.host_e = tk.Entry(conn_option_frame,width=25,textvariable=self.port)
            self.host_e.grid(row=3,column=1,padx=5)
            
            l = tk.Label(conn_option_frame, text='Username',width=15, background='light gray')
            l.grid(row=4,column=0,pady=5,padx=5)
            l.config(relief=tk.GROOVE)
            
            self.user_e = tk.Entry(conn_option_frame,width=25,textvariable=self.user)
            self.user_e.grid(row=4,column=1,padx=5)
            
            l = tk.Label(conn_option_frame, text='Password',width=15, background='light gray')
            l.grid(row=5,column=0,pady=5,padx=5)
            l.config(relief=tk.GROOVE)
            
            self.pass_e = tk.Entry(conn_option_frame,width=25,show="*",textvariable=self.password)
            self.pass_e.grid(row=5,column=1,padx=5)
            
            l = tk.Label(conn_option_frame, text='Private Key',width=15, background='light gray')
            l.grid(row=6,column=0,pady=5,padx=5)
            l.config(relief=tk.GROOVE)
            
            self.key_e = tk.Entry(conn_option_frame,width=25,textvariable=self.keyfile)
            self.key_e.grid(row=6,column=1,padx=5)
            self.key_e.config(state=tk.DISABLED)
            
            def open_key():
                self.keyfile.set(filedialog.askopenfilename())
                self.top.lift()
                
            b = tk.Button(conn_option_frame, text="Select", command=open_key)
            b.grid(pady=5, padx=5, column=1, row=7, sticky="WE")
            
            
            
            ####NSG###
            
            l = tk.Label(nsgconn_option_frame, text='Base API URL',width=15, background='light gray')
            l.grid(row=2,column=0,pady=5,padx=5)
            l.config(relief=tk.GROOVE)
            
            self.nsg_url_e = tk.Entry(nsgconn_option_frame,width=25,textvariable=self.nsg_url)
            self.nsg_url_e.grid(row=2,column=1,padx=5)
            
            l = tk.Label(nsgconn_option_frame, text='Username',width=15, background='light gray')
            l.grid(row=3,column=0,pady=5,padx=5)
            l.config(relief=tk.GROOVE)
            
            self.nsg_user_e = tk.Entry(nsgconn_option_frame,width=25,textvariable=self.nsg_user)
            self.nsg_user_e.grid(row=3,column=1,padx=5)
            
            l = tk.Label(nsgconn_option_frame, text='Password',width=15, background='light gray')
            l.grid(row=4,column=0,pady=5,padx=5)
            l.config(relief=tk.GROOVE)
            
            self.nsg_pass_e = tk.Entry(nsgconn_option_frame,width=25,show="*",textvariable=self.nsg_password)
            self.nsg_pass_e.grid(row=4,column=1,padx=5)
                                    
            l = tk.Label(nsgconn_option_frame, text='Application Name',width=15, background='light gray')
            l.grid(row=5,column=0,pady=5,padx=5)
            l.config(relief=tk.GROOVE)
            
            self.nsg_app_name_e = tk.Entry(nsgconn_option_frame,width=25,textvariable=self.nsg_app_name)
            self.nsg_app_name_e.grid(row=5,column=1,padx=5)
            
            l = tk.Label(nsgconn_option_frame, text='Application ID',width=15, background='light gray')
            l.grid(row=6,column=0,pady=5,padx=5)
            l.config(relief=tk.GROOVE)
            
            self.nsg_app_id_e = tk.Entry(nsgconn_option_frame,width=25,textvariable=self.nsg_app_id)
            self.nsg_app_id_e.grid(row=6,column=1,padx=5)
            
            #Return
            
            button_frame = tk.Frame(top)
            button_frame.grid(row=20,column=0,columnspan=2)
            
            b = tk.Button(button_frame, text="Ok", command=self.ok)
            b.grid(pady=5, padx=5, column=0, row=0, sticky="WE")
            
            b = tk.Button(button_frame, text="Cancel", command=self.cancel)
            b.grid(pady=5, padx=5, column=1, row=0, sticky="WE")
            
            
        def verify_good(self):
            return True
        
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
                self.server.port = self.port.get()
                self.server.user = self.user.get()
                self.server.password = self.password.get()
                self.server.priv_key_location = self.keyfile.get()
                                
            self.servers_file.update_server_details(self.server)
            return
            
        def ok(self):
            self.confirm = True
            self.save_file()
            self.top.destroy()
            
        def cancel(self):
            self.top.destroy()