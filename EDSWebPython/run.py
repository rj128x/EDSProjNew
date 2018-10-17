import config
import datetime
import time
from webAPI import EdsWebApi



web=EdsWebApi()
web.connect()
web.logger.debug('lalalala')

ds=datetime.datetime(2018,10,17)
de=datetime.datetime(2018,10,18)
tags={'07VT_LP01AO-03.MCR@GRARM','07VT_TW00AI-05.MCR@GRARM' }

reqId=None
items=[]

for tag in tags:
	item={
		'function':'VALUE',
		'pointId':{
			'iess':tag
			}
		}
	items.append(item)


request=web.createRequest(ds,de,3600,items)


reqId=web.soap_cln.service.requestTabular(web.auth_str,request)
web.runRequest(reqId)

response=web.soap_cln.service.getTabular(web.auth_str,reqId)

points=response['pointsIds']
for point in points:
	print(point)

rows=response['rows']
for row in rows:
	ts=row['ts']['second']
	dt=datetime.datetime.fromtimestamp(ts)
	print(dt)
	values=row['values']
	vs=[]
	for value in values:
		v=value['value'][0]
		vs.append(v)
	print(vs)
	