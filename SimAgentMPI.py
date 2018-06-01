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
        main_window.stop_threads()
        raise
    except Exception as e:
        try:
            main_window.exitapp = True
            main_window.stop_threads()
        except Exception:
            print("main_window.exitapp not defined yet, other problem too, passing")
            pass
        print(e)  
        raise e

    
main()