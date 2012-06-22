"""

    matrixParser.py: 
    
        This script parses data from the file paint_##_##.logresponse_matrix.txt (## are numbers, different 
for every subject). This script computes straight away the rate with which the classifier yielded the 
target stimulus. 

"""



import numpy as np;
import pylab as plt;
# Add stuff not to 

fIn = open('./VPAne_12_06_15/paint_18_24.logresponse_matrix.txt', 'r'); ## ANE
#fIn = open('./VPJorge_12_06_14/paint_20_55.logresponse_matrix.txt', 'r'); ## JORGE
#fIn = open('./VPmai_12_06_12/paint_14_41.logresponse_matrix.txt', 'r'); ## MAI
#fIn = open('./VP_piratenbraut_12_06_12/paint_17_3.logresponse_matrix.txt', 'r'); ## PIRATEN
#fIn = open('./VP_nancy_12_06_13/paint_18_28.logresponse_matrix.txt', 'r'); ## GUY
#fIn = open('./VPjam_12_06_14/paint_12_47.logresponse_matrix.txt', 'r'); ## RAFA

dR = fIn.read();
fIn.close();

dSB = dR.split('], [');
dSB[0] = dSB[0][2:len(dSB[0])];
dSB[-1] = dSB[-1][0:len(dSB[-1])-2];

dMatrix = [];
for dd in dSB:
    newLine = [];
    dL = dd.split(',');
    for ii, ddd in enumerate(dL):
        if (ii==0):
            newLine += [int(ddd[-1])];
        elif (ii==len(ddd)-1): 
            newLine += [int(ddd[1])];
        else:
            newLine += [int(ddd)];
    dMatrix += [newLine];
    
nGo = 0;
nOK = 0;
for ii in range(len(dMatrix)): 
    nOK += dMatrix[ii][ii];
    for jj in range(len(dMatrix)):
         nGo += dMatrix[ii][jj];
    
print nGo, nOK;
print "pOK = ", float(nOK)/nGo;


GSMatrix = [];
for line in dMatrix:
    newLine = [];
    for dd in line:
        newLine += [float(dd)/nGo];
    GSMatrix += [newLine];
    

# Plotting the matrix. 
plt.figure();
plt.imshow(GSMatrix, interpolation='nearest');
plt.show();


    
    
    
    
    
    
    
    
    
    
