import config
import datetime
import time
from webAPI import EdsWebApi



web=EdsWebApi()
web.connect()
web.logger.debug('lalalala')

ds=datetime.datetime(2017,9,1)
de=datetime.datetime(2018,11,27)
tag='04VT_AC31D-22.MCR@GRARM' 




dt=ds
data=[]
while dt<de:	
	dt1=web.getDateChange(dt,de,tag,'F_INTOOVER_DT',[0.9])	
	if dt1<de:				
		dt2=web.getDateChange(dt1,de,tag,'F_INTOUNDER_DT',[0.1])
		len=dt2.timestamp()-dt1.timestamp()
		record={'start':dt1,'end':dt2,'len':len}
		data.append(record)
		web.out.info ('{start} - {end}: {len}'.format(**record))
		dt=dt2
	else:
		break

