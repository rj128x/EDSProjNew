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
tagVal='04VT_AC31A-01.MCR@GRARM' 


def getData(tag,tagVal,tagP,tagF):
	print (tag)
	web.out.info("{0};{1};{2};{3}".format(tag,tagVal,tagP,tagF))
	dt=ds
	data=[]
	while dt<de:	
		dt1=web.getDateChange(dt,de,tag,'F_INTOOVER_DT',[0.9])	
		if dt1<de:				
			dt2=web.getDateChange(dt1,de,tag,'F_INTOUNDER_DT',[0.1])
			val=web.getVal(dt1+datetime.timedelta(seconds=10),tagVal)
			valP=web.getVal(dt1+datetime.timedelta(seconds=-10),tagP)
			valF=web.getVal(dt1+datetime.timedelta(seconds=-10),tagF)
			len=dt2.timestamp()-dt1.timestamp()
			record={'start':dt1,'end':dt2,'len':len, 'val':val, 'valP':valP,'valF':valF}
			data.append(record)
			#web.out.info ('{start} - {end}: {len}'.format(**record))
			web.out.info ('{start};{val};{valP};{valF}'.format(**record))
			dt=dt2
		else:
			break

getData('04VT_AC31D-22.MCR@GRARM','04VT_AC31A-01.MCR@GRARM','04VT_LP01AO-03.MCR@GRARM','04VT_GC01A-16.MCR@GRARM')
getData('04VT_AC30D-22.MCR@GRARM','04VT_AC30A-01.MCR@GRARM','04VT_LP01AO-03.MCR@GRARM','04VT_GC01A-16.MCR@GRARM')

getData('07VT_AC31D-22.MCR@GRARM','07VT_AC31A-01.MCR@GRARM','07VT_LP01AO-03.MCR@GRARM','07VT_GC01A-16.MCR@GRARM')
getData('07VT_AC30D-22.MCR@GRARM','07VT_AC30A-01.MCR@GRARM','07VT_LP01AO-03.MCR@GRARM','07VT_GC01A-16.MCR@GRARM')

