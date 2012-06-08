"""

	parseData.py: 

		This file contains a routine to parse the data from files with .vmrk extension. 

"""

import numpy as np;
import pylab as plt;

fileName = './calibration_ImageCreatorVPmag03.vmrk';
fIn = open(fileName, 'r');
dataR = fIn.read();
fIn.close();
dataL = dataR.split('\n');
while (dataL[0][0] != 'M'):
	dataL.pop(0);
dataL.pop(0);
dataL.pop();

dataDict = [];
for line in dataL:
	aa = line.split(',');

	# Detect Response or Stimulus:
	kind = aa[1][0];

	# Detect stimulus or response ID: 
	ID_ = aa[1].split(' ');
	if (len(ID_)!=1): 
		ID = int(aa[1][-1]);
	else: 
		ID = int(aa[1][1:len(aa)-1]);

	# Target? 
	target = False;
	if ((ID>=100) and (ID<200)): 
		target=True;

	# Right Response? 
	rightResponse = False;
	if ((kind=='R') and (ID==4 or ID==6)):
		rightResponse = True;

	# Time: 
	time = int(aa[2]);

	# Add to dataDict: 
	dataDict += [{'kind':kind, 'ID':ID, 'time':time, 'target':target, 'rightResponse':rightResponse}];


# Inter-stimulus interval: 
stim = [dic for dic in dataDict if dic['kind']=='S'];
ISI = [stim[ii+1]['time']-stim[ii]['time'] for ii in range(len(stim)-1)];
plt.figure();
plt.title('Inter-stimulus Interval');
plt.xlabel('Time [ms]');
plt.ylabel('Number of events [#]');
plt.hist(ISI, 500);#


# Inter-target interval: 
actualTarget = [dataDict[ii-1] for ii in range(len(dataDict)) if dataDict[ii]['target']];
targets = [dic for dic in dataDict if dic['target']];
ITI = [targets[ii+1]['time']-targets[ii]['time'] for ii in range(len(targets)-1)];
aITI = [actualTarget[ii+1]['time']-actualTarget[ii]['time'] for ii in range(len(actualTarget)-1)];
plt.figure();
plt.title('Inter-target Interval');
plt.xlabel('Time [ms]');
plt.ylabel('Number of events [#]');
plt.hist(ITI, 500);
plt.hist(aITI, 500);


# Inter-response interval:
responses = [dic for dic in dataDict if dic['rightResponse']];
IRI = [responses[ii+1]['time']-responses[ii]['time'] for ii in range(len(targets)-1)];
plt.figure();
plt.title('Inter-response interval');
plt.xlabel('Time [ms]');
plt.ylabel('Number of events [#]');
plt.hist(IRI, 500);

# Inter-response interval corrected:
responses_ = [responses[ii-1] for ii in range(1,len(responses)) if (responses[ii]['time']-responses[ii-1]['time']>200)];
# if (dataDict[-1]['time']-dataDict[-2]['time']>200):
# 	targets_ += [dataDict[-1]['time']];
IRI_ = [responses_[ii+1]['time']-responses_[ii]['time'] for ii in range(len(responses_)-1)];
plt.figure();
plt.title('Inter-response Interval corrected');
plt.xlabel('Time [ms]');
plt.ylabel('Number of events [#]');
plt.hist(IRI_, 500);


##

# Target to response interval:
dT = [];
jj = 0;
for ii, t in enumerate(actualTarget):
	if (ii<len(targets)-1):
		while ((jj<len(responses_)) and (responses_[jj]['time']<=targets[ii+1]['time'])) :
			dT += [responses_[jj]['time']-t['time']];
			jj += 1;

	if ii==len(actualTarget)-1:
		while (jj<len(responses_)): 
			dT += [responses_[jj]['time']-t['time']];
			jj += 1;

plt.figure();
plt.title('Target-to-response interval');
plt.xlabel('Time [ms]');
plt.ylabel('Number of events [#]');
plt.hist(dT, 1000);

# Prob. OK:
s = 0;
s_ = 0;
s__ = 0;
for tt in dT: 
	if (tt>300 and tt<550):
		s += 1;
	if (tt<650):
		s_ += 1;
	if (tt<750):
		s__ += 1;
pOK = float(s)/len(dT);
pOK_ = float(s_)/len(dT);
pOK__ = float(s__)/len(dT);
print "Probability of right reactions, short interval: ", pOK;
print "Probability of right reactions, medium interval: ", pOK_;
print "Probability of right reactions, long interval: ", pOK__;
print;




# Inter-response interval corrected:
responses_ = [responses[ii-1] for ii in range(1,len(responses)) if (responses[ii]['time']-responses[ii-1]['time']>200)];
# if (dataDict[-1]['time']-dataDict[-2]['time']>200):
# 	targets_ += [dataDict[-1]['time']];
IRI_ = [responses_[ii+1]['time']-responses_[ii]['time'] for ii in range(len(responses_)-1)];
plt.figure();
plt.title('Inter-response Interval corrected');
plt.xlabel('Time [ms]');
plt.ylabel('Number of events [#]');
plt.hist(IRI_, 500);
# Prob hit vs. prob miss: 
dT = [];
jj = 0;
countHit = 0.;
countHit_ = 0.;
countHit__ = 0.;
for ii,t in enumerate(actualTarget):
	# nearRespones = [resp for resp in responses_ if ((resp['time']-t['time']>300) and (resp['time']-t['time']<550))];
	# nearRespones_ = [resp for resp in responses_ if (resp['time']-t['time']>300 and resp['time']-t['time']<650)];
	# nearRespones__ = [resp for resp in responses_ if (resp['time']-t['time']>300 and resp['time']-t['time']<750)];
	# print ii, ": ", t['time'];
	for resp in responses_:
		if (resp['time']-t['time']>300 and resp['time']-t['time']<550):
			countHit += 1.;
			break;
	for resp in responses_:
		if (resp['time']-t['time']>300 and resp['time']-t['time']<650):
			countHit_ += 1.;
			break;
	for resp in responses_:
		if (resp['time']-t['time']>300 and resp['time']-t['time']<750):
			countHit__ += 1.;
			break;


pHit = countHit/len(actualTarget);
pHit_ = countHit_/len(actualTarget);
pHit__ = countHit__/len(actualTarget);
print "Probability of hit, short interval: ", pHit;
print "Probability of hit, medium intrval: ", pHit_;
print "Probability of hit, long interval: ", pHit__;
	

plt.show();


