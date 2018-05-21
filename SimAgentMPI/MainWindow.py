# -*- coding: utf-8 -*-
"""
Created on Sun May 20 16:46:40 2018

@author: Tyler
"""
from Utils import CreateToolTip, Autoresized_Notebook

import tkinter as tk
from tkinter import messagebox,ttk,filedialog

import threading

class MainWindow():
    def __init__(self):
        self.root = tk.Tk()
        self.window_title = "Sim Agent MPI (University of Missouri - Nair Neural Engineering Laboratory - Banks)"
        self.about_text = "Written for:\nProfessor Satish Nair's Neural Engineering Laboratory\nat The University of Missouri\n\nWritten by: Tyler Banks\n\nContributors:\nFeng Feng\nBen Latimer\nZiao Chen\n\nInitial Neuron Code:  Feng et al. (2016)\n\nEmail tbg28@mail.missouri.edu with questions"
        
        self.window_size = '1220x600'
        self.default_status = "Status: Ready"
        self.status_timer = 4.0
        
        self.root.columnconfigure(0,weight=1)
        self.root.rowconfigure(0,weight=1)
        self.root.title(self.window_title)
        self.root.geometry(self.window_size)
        
        #self.root.resizable(0,0)
        self.root.config(menu=self.menu_bar(self.root))
        
        self.app_status = tk.StringVar(self.root,'')
        self.reset_app_status()
        
        print('Starting. Please wait...')
        self.style = ttk.Style()
        try:
            self.style.theme_create( "colored", parent="alt", settings={
                    "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0] } },
                    "TNotebook.Tab": {
                        "configure": {"padding": [5, 2], "background": "#D9D9D9" },
                        "map":       {"background": [("selected", "#C0C0E0")],
                                      "expand": [("selected", [1, 1, 1, 0])] } } } )
        
            self.style.theme_create( "largertheme", parent="alt", settings={
                    "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0] } },
                    "TNotebook.Tab": {
                        "configure": {"padding": [5, 2] },
                        "map":       {
                                      "expand": [("selected", [1, 1, 1, 0])] } } } )
            self.style.theme_use("colored")
        except Exception:
            print('Style loaded previously. Continuing.')
        
        frame1 = tk.Frame(self.root)
        frame1.grid(row=0,column=0,sticky='news')
        frame1.columnconfigure(0,weight=1)
        frame1.columnconfigure(0,weight=1)
        frame2 = tk.Frame(self.root)
        frame2.grid(row=1,column=0,sticky='news')
        
        nb = Autoresized_Notebook(frame1)
        nb.pack(padx=5,pady=5,side="left",fill="both",expand=True)
        
        bottom_status_bar = tk.Frame(frame2)
        bottom_status_bar.grid(row=0,column=0,padx=5,pady=2)#,fill=tk.X,expand=True)
        
        label = tk.Label(bottom_status_bar,textvariable=self.app_status)
        label.pack(expand=True)
    
        page1 = ttk.Frame(nb)
        
        nb.add(page1, text='Manage Jobs')
        
        #Alternatively you could do parameters_page(page1), but wouldn't get scrolling
        self.bind_page(page1, self.jobs_page)
        
        self.display_app_status("Ready")
                
        return
    
    def show(self):
        try:
            print('Load complete. Running...')
            self.root.mainloop()
        except Exception:
            print('Error, closing display loop')
        print('Closing.\n')
        
    def bind_page(self, page, gen_frame):
        #### Scrollable Frame Window ####
        #https://stackoverflow.com/questions/42237310/tkinter-canvas-scrollbar
        frame = tk.Frame(page, bd=2)
        frame.pack(side="left",fill="both",expand=True)
        
        yscrollbar = tk.Scrollbar(frame)
        yscrollbar.pack(side=tk.RIGHT,fill=tk.Y)
        xscrollbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
        xscrollbar.pack(side=tk.BOTTOM,fill=tk.X)
        
        canvas = tk.Canvas(frame, bd=0,
                        xscrollcommand=xscrollbar.set,
                        yscrollcommand=yscrollbar.set,)
        
        xscrollbar.config(command=canvas.xview)
        yscrollbar.config(command=canvas.yview)
        
        f=tk.Frame(canvas)
        canvas.pack(side="left",fill="both",expand=True)
        canvas.create_window(0,0,window=f,anchor='nw')
        ###############################
        gen_frame(f)
        frame.update()
        canvas.config(scrollregion=canvas.bbox("all"))
    
    def reset_app_status(self):
        self.app_status.set(self.default_status)

    def display_app_status(self,str):
        self.app_status.set("Status: "+str)
        threading.Timer(4.0, self.reset_app_status).start()
        
    def menu_bar(self, root):
        def hello():
            messagebox.showinfo("Create New Server", "To be implemented")
            
        def about():
            messagebox.showinfo("About", self.about_text, icon='info')
    
        menubar = tk.Menu(root)
        
        # create a pulldown menu, and add it to the menu bar
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Add Server", command=hello)
        #filemenu.add_command(label="Save", command=hello)
        #filemenu.add_separator()
        #filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        return menubar
    
    
    def jobs_page(self, root):
        
        #open project dir
        print(filedialog.askdirectory())
        return
