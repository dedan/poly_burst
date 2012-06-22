"""

    bbciApplyParser.py: 
    
        This file contains a script to parse the results from the file bbci_apply_log.txt. The script 
parses the data from the lines that are not empty and that do not begin with a '#', which seem to be 
comments to the file. 
		The parsed data are stored in a list with dictionaries. Each dictionary comprises the following 
information: 
			>> time1: The first number seems to be a time index, as it is followed by an 's', maybe 
		indicating seconds. 
			>> stim: The second number (we find it between brackets like M(###), where ### is the number 
		that we parse out of the file) identifies the stimulus that was presented to the subject. Unluckily, 
		in this number it is encoded the number of the picture from which the stimulus was extracted, but 
		not the actual polygon that was presented. This information must be parsed out from the file 
		bbci_apply_log.txt. 
			>> time2: The third number seems to be a time index as well. I don't know the difference 
		between the two of them. 
			>> square-bracked number (sB in the script): a number between square brackets is presented. 
		My guess is that this number is the classifier response to the presented stimulus. We can find 
		a strong correlation between a stimulus been selected by the classifier and this number being 
		negative. 
			>> response: None by default, it is the number identifying the selected stimulus whenever 
		there is a response from the classifier. 


"""

import numpy as np;
import pylab as plt;

fIn = open('./VPAne_12_06_15/bbci_apply_log.txt', 'r'); ## ANE
#fIn = open('./VPJorge_12_06_14/bbci_apply_log.txt', 'r'); ## JORGE
#fIn = open('./VPmai_12_06_12/bbci_apply_log.txt', 'r'); ## MAI
#fIn = open('./VP_piratenbraut_12_06_12/bbci_apply_log.txt', 'r'); ## PIRATEN
#fIn = open('./VP_nancy_12_06_13/bbci_apply_log.txt', 'r'); ## NANCY
#fIn = open('./VPjam_12_06_14/bbci_apply_log.txt', 'r'); ## RAFA

dR = fIn.read();
fIn.close();

dL = dR.split('\n');
dL = [line for line in dL if (len(line)>0) and (line[0] != '#')];

dP = [];
for line in dL:
	sL = line.split(' | ');
	time1 = float(sL[0][0:len(sL[0])-1]);
	stim = int(sL[1][2:len(sL[1])-1])
	time2 = float(sL[2][0:len(sL[2])-1]);
	sB = float(sL[3][1:len(sL[3])-1]);
	response = None;
	if (len(sL[4].split('='))>1):
		response = int(sL[4].split('=')[-1][0:len(sL[4].split('=')[-1])-1]);
	newDic = {'time1':time1, 'stim':stim, 'time2':time2, 'sB':sB, 'resp':response};
	dP += [newDic];

for dic in dP:
	print dic['time1'], dic['stim'], dic['time2'], dic['sB'], dic['resp'];
    











