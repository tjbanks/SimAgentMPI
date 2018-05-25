    # -*- coding: utf-8 -*-
"""
Created on Sun May 20 16:46:40 2018

@author: Tyler
"""

from SimAgentMPI.MainWindow import MainWindow

def main():
    
    try:
        main_window = MainWindow()
        main_window.show()
    except KeyboardInterrupt:
        main_window.exitapp = True
        raise
    except Exception:
        main_window.exitapp = True
        raise
        
    
    
main()