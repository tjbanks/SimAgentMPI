#Load the synaptic.txt file and plot the trace
import matplotlib.pyplot as plt

x = []
with open('synaptic.txt') as f:
    lines = f.readlines()
    x = [float(line.strip()) for line in lines]
    
plt.plot(x)
plt.show()