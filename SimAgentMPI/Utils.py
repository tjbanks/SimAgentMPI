# -*- coding: utf-8 -*-
"""
Created on Sun May 20 16:48:45 2018

@author: Tyler
"""

import tkinter as tk
from tkinter import ttk,Entry,StringVar,Listbox

import re
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove

def replace(file_path, pattern, subst,unix_end=False):
    #Create temp file
    #print("searching for: {}".format(pattern))
    fh, abs_path = mkstemp()
    with fdopen(fh,'w',newline="\n") as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                line = re.sub(r"{}".format(pattern), subst, line)
                line.replace("\n", "")
                new_file.write(line)
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)
    
def get_line_with(file_path, text):
    with open(file_path) as file:
        for line in file:
            if (text in line)==True:
                return line

class Autoresized_Notebook(ttk.Notebook):
    def __init__(self, master=None, **kw):
        ttk.Notebook.__init__(self, master, **kw)
        self.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self,event):
        event.widget.update_idletasks()
        tab = event.widget.nametowidget(event.widget.select())
        event.widget.configure(height=tab.winfo_reqheight())
        

class CreateToolTip(object):
    """
    create a tooltip for a given widget
    https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()
            
class AutocompleteEntry(Entry):
    def __init__(self, parent, autocompleteList, *args, **kwargs):
        self.parent=parent
        # Listbox length
        if 'listboxLength' in kwargs:
            self.listboxLength = kwargs['listboxLength']
            del kwargs['listboxLength']
        else:
            self.listboxLength = 8

        # Custom matches function
        if 'matchesFunction' in kwargs:
            self.matchesFunction = kwargs['matchesFunction']
            del kwargs['matchesFunction']
        else:
            def matches(fieldValue, acListEntry):
                pattern = re.compile('.*' + re.escape(fieldValue) + '.*', re.IGNORECASE)
                return re.match(pattern, acListEntry)
                
            self.matchesFunction = matches

        
        Entry.__init__(self,master=parent, *args, **kwargs)
        self.focus()

        self.autocompleteList = autocompleteList
        
        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = StringVar()

        self.var.trace('w', self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Up>", self.moveUp)
        self.bind("<Down>", self.moveDown)
        
        self.listboxUp = False

    def changed(self, name, index, mode):
        if self.var.get() == '':
            if self.listboxUp:
                self.listbox.destroy()
                self.listboxUp = False
        else:
            words = self.comparison()
            if words:
                if not self.listboxUp:
                    self.listbox = Listbox(master=self.parent,width=self["width"], height=self.listboxLength)
                    self.listbox.bind("<Button-1>", self.selection)
                    self.listbox.bind("<Right>", self.selection)
                    self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                    self.listboxUp = True
                
                self.listbox.delete(0, tk.END)
                for w in words:
                    self.listbox.insert(tk.END,w)
            else:
                if self.listboxUp:
                    self.listbox.destroy()
                    self.listboxUp = False
        
    def selection(self, event):
        if self.listboxUp:
            self.var.set(self.listbox.get(tk.ACTIVE))
            self.listbox.destroy()
            self.listboxUp = False
            self.icursor(tk.END)

    def moveUp(self, event):
        if self.listboxUp:
            if self.listbox.curselection() == ():
                index = '0'
            else:
                index = self.listbox.curselection()[0]
                
            if index != '0':                
                self.listbox.selection_clear(first=index)
                index = str(int(index) - 1)
                
                self.listbox.see(index) # Scroll!
                self.listbox.selection_set(first=index)
                self.listbox.activate(index)

    def moveDown(self, event):
        if self.listboxUp:
            if self.listbox.curselection() == ():
                index = '0'
            else:
                index = self.listbox.curselection()[0]
                
            if index != tk.END:                        
                self.listbox.selection_clear(first=index)
                index = str(int(index) + 1)
                
                self.listbox.see(index) # Scroll!
                self.listbox.selection_set(first=index)
                self.listbox.activate(index) 

    def comparison(self):
        return [ w for w in self.autocompleteList if self.matchesFunction(self.var.get(), w) ]
    
    
class Batch_File(object):
    parallel_cmd = "srun"
    
    def __init__(self, filename):
        self.filename = filename
        
        self.partition = "General"
        self.cust_name = ""
        self.out_file = ""
        self.err_file = ""
        self.hours_limit = 2
        self.nodes = 1
        self.cores = 1
        self.modules = []
        self.singlecoreruns = []
        self.sruns = []
        
        
        self.read_file()
        
    def read_file(self):
        return
        
    def write_replacements(self):
        return
    
    def write_new_file(self):
        
        
        
        
        return    
        
    def get_file_lines(self):
        arr = []
        
        header = [
                "#! /bin/bash",
                "",
                "{}#SBATCH -p {} # Uses the {} partition".format(("" if self.partition else "#"),self.partition,self.partition),
                "{}#SBATCH -J {} # job's custom name".format(("" if self.cust_name else "#"),self.cust_name),
                "{}#SBATCH -o {} # job output custom name".format(("" if self.out_file else "#"),self.out_file),
                "{}#SBATCH -e {} # job error custom name".format(("" if self.err_file else "#"),self.err_file),
                "{}#SBATCH -t 0-{}:00".format(("" if self.hours_limit else "#"),self.hours_limit),
                "",
                "{}#SBATCH -N {} # number of nodes".format(("" if self.nodes else "#"),self.nodes),
                "{}#SBATCH -n {} # number of codes (tasks)".format(("" if self.cores else "#"),self.cores),
                ""
                ]
        
        module_load = []
        
        single_header = [
                "# Commands here run only on the first core",
                ]
        
        single = []

        parallel_header = [
                "# Commands with {} will run on all cores in the allocation".format(Batch_File.parallel_cmd)
                ]        
        
        parallel = []
        
        module_unload = []
        
        for m in self.modules:
            module_load.append("module load ".format(m))
        
        
        arr = header + module_load + single_header + single + parallel_header + parallel + module_unload
        
        return arr