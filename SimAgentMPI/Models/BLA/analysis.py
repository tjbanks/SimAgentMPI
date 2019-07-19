# Python
#import matplotlib.pyplot as plt
#import pandas as pd
#import sys

#df = pd.read_csv('data',sep='\t',header=None)
#spiketimes = df[0].tolist()

#bins = 500
#if len(sys.argv) == 2:
#    bins = int(sys.argv[1])
	
#plt.hist(spiketimes,normed=False,bins=bins)
#plt.show()

# Python
import matplotlib.pyplot as plt
import pandas as pd
import sys

df = pd.read_csv('data',sep='\t',header=None)
df = df.loc[(df[1] >= 900)]
print(df)
spiketimes = df[0].tolist()
cells = df[1].tolist()

bins = 500
if len(sys.argv) == 2:
    bins = int(sys.argv[1])
	
#plt.hist(spiketimes,normed=False,bins=bins)
plt.scatter(spiketimes,cells,s=1)
plt.xlim(45000,45500)
plt.show()
