import config
import datetime
import time
from webAPI import EdsWebApi


def getBitVal(val,bit):
	s=bin(val)
	if (len(s)-2)>bit:
		b=int(s[-bit-1])	
		return b==1
	return False

web=EdsWebApi()
web.connect()
web.logger.debug('lalalala')

ds=datetime.datetime(2018,10,1)
de=datetime.datetime(2018,10,18)
tag='07VT_AM01P-47.MCR@GRARM' 
tag='07VT_AM03P-01.MCR@GRARM' 
bit=14




dt=ds
data=[]
val=web.getVal(ds,tag)
bitVal=getBitVal(val,bit)
#val=0.1
#bitVal=False
onDT=None
offDT=None
if bitVal:
	onDT=ds
while dt<de:	
	d1=web.getDateChangeFull(dt,de,tag,val)
	valNew=web.getVal(d1,tag)
	bitValNew=getBitVal(valNew,bit)
	if val!=valNew:
		val=valNew
		dt=d1
		if bitVal != bitValNew:
			bitVal=bitValNew
			if bitVal:
				onDT=d1
			else:
				offDT=d1
				print('{0} - {1} [{2}]'.format(onDT,offDT,offDT.timestamp()-onDT.timestamp()))
	else:
		dt=d1
print('finish')
input()