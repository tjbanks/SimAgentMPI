# -*- coding: utf-8 -*-
"""
Created on Sun May 20 16:46:40 2018

@author: Tyler
"""
import json
import os.path

class ServersFile(object):
    servers_file = "SimAgentMPI/.servers"
    
    def __init__(self, filename = None):
        if not filename:
            self.filename = ServersFile.servers_file
            
        if not os.path.isfile(self.filename):
            self.create_file()
            
        self.reload_servers()
        
        
    def create_file(self):
        open(self.filename, 'a').close()
        return
    
    def reload_servers(self):
        self.json_data = None
        self.servers = []
        
        try:
            with open(self.filename) as json_file:  
                self.json_data = json.load(json_file)
            
            for s in self.json_data:
                self.servers.append(SimServer().from_dict(s))#joson load array of dicts
        except Exception as e:
            print(e)
        return self.servers
    
    def get_server(self, server_id):
        for s in self.servers:
            if s.id == server_id:
                return s
        return None
    
    def get_server_byname(self, server_name):
        for s in self.servers:
            if s.name == server_name:
                return s
        return None
    
    def update_server_details(self, sim_server):
        
        self.update = False
        for s in self.servers:
            if s.id == sim_server.id:
                self.update = True
                s.from_dict(sim_server.to_dict())
        if not self.update:
            self.servers.append(sim_server)
            
            
        json_data = []
        for s in self.servers:
            json_data.append(s.to_dict())
            
        with open(self.filename, 'w') as outfile:  
            json.dump(json_data, outfile)
        return

class SimServer(object):
    propname_id = "id"
    propname_name = "name"
    propname_type = "type"
    propname_host = "host"
    propname_port = "port"
    propname_user = "user"
    propname_password = "password"
    propname_priv_key_location = "private_key_location"
    propname_nsg_api_url = "nsg_api_url"
    propname_nsg_api_appname = "nsg_api_appname"
    propname_nsg_api_appid = "nsg_api_appid"
    
    
    def __init__(self):
        self.set_to_defaults()
        return
    
    def set_to_defaults(self):
        self.id = "-1"
        self.name = ""
        self.type = "nsg"
        self.host = ""
        self.port = "22"
        self.user = "user"
        self.password = "pass"
        self.priv_key_location = ""
        self.nsg_api_url = "https://nsgr.sdsc.edu:8443/cipresrest/v1"
        self.nsg_api_appname = "nsgappname"
        self.nsg_api_appid = "nsgappname-id"
        return self

    def to_dict(self):
        data = {}
        data[self.propname_id] = self.id
        data[self.propname_name] = self.name
        data[self.propname_type] = self.type
        data[self.propname_host] = self.host
        data[self.propname_port] = self.port
        data[self.propname_user] = self.user
        data[self.propname_password] = self.password
        data[self.propname_priv_key_location] = self.priv_key_location
        data[self.propname_nsg_api_url] = self.nsg_api_url
        data[self.propname_nsg_api_appname] = self.nsg_api_appname
        data[self.propname_nsg_api_appid] = self.nsg_api_appid
        return data
    
    def from_dict(self, data):
        self.id = data[self.propname_id]
        self.name = data[self.propname_name]
        self.type = data[self.propname_type]
        self.host = data[self.propname_host]
        self.port = data[self.propname_port]
        self.user = data[self.propname_user]
        self.password = data[self.propname_password]
        self.priv_key_location = data[self.propname_priv_key_location]
        self.nsg_api_url = data[self.propname_nsg_api_url]
        self.nsg_api_appname = data[self.propname_nsg_api_appname]
        self.nsg_api_appid = data[self.propname_nsg_api_appid]
        return self