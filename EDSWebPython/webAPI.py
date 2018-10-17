from suds import client
import logging
import time
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
			for i in range(10 * config.TIMEOUT):
				try:
					eds_request_status = self.soap_cln.service.getRequestStatus(self.auth_str, reqId)
				except Exception as request_error:
					self.logger.debug(u'[EDS_WebAPI_read]  EDS API problem: %s' % (str(request_error).encode('utf8')))						
					break
				self.logger.debug('[EDS_WebAPI_read] status: %s' % (str(eds_request_status.message)))
				if eds_request_status.status == 'REQUEST-SUCCESS':
					return False						
				if eds_request_status.status == 'REQUEST-FAILURE':
					return True					
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

