from suds import client
import logging
import time
import datetime
import config
import logging
from logging import handlers
import os

class EdsWebApi():	
	def __init__(self):
		self.auth_str = ''
		self.soap_cln = None
		self.connected = False		
		self.logger = self.initLogging()
		self.outs=dict()
		self.out=self.initMainOut()

	def initLogging(self):
		logger = logging.getLogger('eds')
		logger.setLevel("DEBUG")
		if not os.path.exists('logs'):
			os.makedirs('logs')
		log_file = handlers.RotatingFileHandler(filename='logs\eds.log',
			maxBytes=10000000,
			backupCount=10)
		log_formater = logging.Formatter('%(asctime)s %(message)s')
		log_file.setFormatter(log_formater)
		logger.addHandler(log_file)	
		logger.debug('init')	
		return logger

	def initMainOut(self):				
		s='outEDS_{0}.txt'.format(time.time())
		logger = logging.getLogger(s)
		logger.setLevel("INFO")
		if not os.path.exists('out'):
			os.makedirs('out')
		log_file = handlers.WatchedFileHandler("out/{0}".format(s))
		log_formater = logging.Formatter('%(message)s')
		log_file.setFormatter(log_formater)
		logger.addHandler(log_file)	
		logger.debug('init')			
		return logger


	def initOut(self,name):				
		s='outEDS_{1}_{0}.txt'.format(time.time(),name)
		logger = logging.getLogger(s)
		logger.setLevel("INFO")
		if not os.path.exists('out'):
			os.makedirs('out')
		log_file = handlers.WatchedFileHandler("out/{0}".format(s))
		log_formater = logging.Formatter('%(message)s')
		log_file.setFormatter(log_formater)
		logger.addHandler(log_file)	
		logger.debug('init')	
		self.outs[name]=logger
		return logger
	
	def outString(self,name,s):
		out=self.outs[name]
		out.info(s)

	def connect(self):		
		eds_wsdl = '%s://%s:%i/eds.wsdl' % (config.EDS_WEB_PROTOCOL,config.EDS_HOST,config.EDS_WEB_PORT)
		connected = False
		authorized = False
		try:
			self.soap_cln = client.Client(eds_wsdl)
			self.logger.debug('[EDS_connector] Successfully connected to EDS')
			connected = True
		except Exception as conn_error:
			self.logger.debug('[EDS_connector] WSDL connection error to %s, %s' % (eds_wsdl, conn_error))
		if connected:
			try:
				self.auth_str = self.soap_cln.service.login(config.EDS_USER, config.EDS_PWD)
				self.logger.debug('[EDS_connector] Successfully authorized in EDS')
				authorized = True
			except Exception as auth_error:
				self.logger.debug('[EDS_connector] WebApi authorisation error with user %s and pass %s, %s' % (config.EDS_USER, config.EDS_PWD, auth_error))
		if connected and authorized:
				self.connected = True

	def eds_logout(self):
		try:
			self.soap_cln.service.logout(self.auth_str)
		except Exception as logour_error:
			self.logger.debug('[EDS_connector] Problem during EDS logout %s' % str(logour_error))
		finally:
			self.connected = False

	def runRequest(self,reqId):
		if reqId is not None:
			for i in range(1000 * config.TIMEOUT):
				try:
					eds_request_status = self.soap_cln.service.getRequestStatus(self.auth_str, reqId)
				except Exception as request_error:
					self.logger.debug(u'[EDS_WebAPI_read]  EDS API problem: %s' % (str(request_error).encode('utf8')))						
					break
				self.logger.debug('[EDS_WebAPI_read] status: %s' % (str(eds_request_status.message)))
				if eds_request_status.status == 'REQUEST-SUCCESS':
					return True						
				if eds_request_status.status == 'REQUEST-FAILURE':
					return False					
				time.sleep(0.1)

	def createRequest(self,dateStart,dateEnd,period,items):				
		request = {
			'period':{
				'from':{
					'second':dateStart.timestamp()
					},
				'till':{
					'second':dateEnd.timestamp()
					}
				},
			'step':{
				'seconds':period
				},
			'items':items
		}
		return request

	def getDateChange(self,dateStart,dateEnd,tag,func,params):			
		items=[]
		item={
			'function':func,
			'pointId':{
				'iess':tag 
				},
			'params':params
			}
		items.append(item)
		step=dateEnd.timestamp()-dateStart.timestamp()
		request = {
			'period':{
				'from':{
					'second':dateStart.timestamp()
					},
				'till':{
					'second':dateEnd.timestamp()
					}
				},
			'step':{
				'seconds':step
				},
			'items':items
		}
		reqId=self.soap_cln.service.requestTabular(self.auth_str,request)
		self.runRequest(reqId)
		response=self.soap_cln.service.getTabular(self.auth_str,reqId)
		rows=[]
		rows=response['rows']
		if len(rows)>0:	
			row=rows[0]			
			vals=row['values']
			if len(vals)>0:				
				try:
					val=vals[0]['value'][0]
					dt1=datetime.datetime.fromtimestamp(val)		
					if dt1==dateStart:
						return dateEnd						
					return dt1
				except Exception:
					return dateEnd
			else:
				return dateEnd
		else:
			return dateEnd

	def getVal(self,dt,tag):
		#print('{0}'.format(dt))
		items=[]
		item={
			'function':'VALUE',
			'pointId':{
				'iess':tag 
				}
			}
		items.append(item)
		request = {
			'period':{
				'from':{
					'second':dt.timestamp()
					},
				'till':{
					'second':dt.timestamp()+10
					}
				},
			'step':{
				'seconds':1
				},
			'items':items
		}
		reqId=self.soap_cln.service.requestTabular(self.auth_str,request)
		self.runRequest(reqId)
		response=self.soap_cln.service.getTabular(self.auth_str,reqId)
		rows=[]
		rows=response['rows']

		if len(rows)>0:	
			row=rows[0]
			ts=row['ts']['second']
			dt=datetime.datetime.fromtimestamp(ts)
			values=row['values']
			value=values[0]
			v=value['value'][0]
			return v
		return None


	def getDateChangeFull(self,dateStart,dateEnd,tag,valInit):			
		#print('{0}-{1} {2}'.format(dateStart,dateEnd,valInit))
		dt1=self.getDateChange(dateStart,dateEnd,tag,"F_INTOOVER_DT",[valInit+0.1])
		#print(dt1)
		dt2=self.getDateChange(dateStart,dateEnd,tag,"F_INTOUNDER_DT",[valInit-0.1])
		#print(dt2)
		dt=dt1
		if dt2<dt1:
			dt=dt2
		return dt

	def eds_qualityToLetter(self, eds_quality):
		return_quality = ''
		if eds_quality == 'QUALITY-BAD':
			return_quality = 'B'
		elif eds_quality == 'QUALITY-GOOD':
			return_quality = 'G'
		elif eds_quality == 'QUALITY-FAIR':
			return_quality = 'F'
		elif eds_quality == 'QUALITY-POOR':
			return_quality = 'P'
		return return_quality

	def getBitVal(self,val,bit):
		s=bin(val)
		if (len(s)-2)>bit:
			b=int(s[-bit-1])	
			return b==1
		return False

