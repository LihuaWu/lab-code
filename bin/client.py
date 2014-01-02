#!/usr/bin/python
#coding:utf-8

import urllib
import popen2
import re
import logging, logging.handlers
import time
import datetime
import socket
import sys

if "." not in sys.path:
	sys.path.append(".")

import tool
	
class Task:
	def __init__(self):
		self.setup()
		try:
			self.handle()
		finally:
			self.finish()

	def setup(self):
		pass

	def handle(self):
		pass

	def finish(self):
		pass

class Extractor(Task):
	def __init__(self, cmd):
		self.cmd = cmd
		self.log_list = list()
		Task.__init__(self)

	def setup(self):
		r = popen2.Popen4(self.cmd)
		# r.wait() returns the status code of wait()
		s = r.fromchild.readlines()
		self.lines = [i.strip() for i in s]

	def handle_line(self, line):
		#line example
		# s="NOTICE: 12-11 15:45:15:  newsdiproxy. * 2007337312 [work_thread_func]: send newsdi of url[http://www.chinanews.com/gn/2013/11-12/5489300.shtml?f=baidu] ok,error no[0] all time use[1] 			       	process time use[1] queue wait time [0] queue len is[0] re_crawl_page_times [0]"

		# and the list will be:
		#funcname, url, error_no, all_time_use, process_time, queue_wait_time, queue_len, re_crawl_times(this will always be 0)
		# and the result will be like:
		#['[work_thread_func]', '[http://www.chinanews.com/gn/2013/11-12/5489300.shtml?f=baidu]', '[0]', '[1]', '[1]', '[0]', '[0]', '[0]']
		regex = "(\[\S+\])+"	
		l = re.findall(regex, line)
		#strip the square braces
		l = [i.lstrip('[').rstrip(']') for i in l]

		keys = ['func', 'url', 'error_no', 'all_time', 'process_time',
			'queue_wait_time', 'queue_len', 're_crawl_times']
		return dict(zip(keys, l))
		
	def handle(self):
		for line in self.lines:
			client_log.debug("Process line:[%s]" %line)
			r = self.handle_line(line)
			self.log_list.append(r)

class Sender(Task):
	def __init__(self, logs, logger):
		self.log_list = logs
		self.logger = logger
		Task.__init__(self)
	
	def handle(self):
		cnt = 0
		for i in self.log_list:
			cnt += 1 
			if(cnt%10 == 0):
				time.sleep(1)
			if 'url' in i:
				print i['url']	
			else:
				print i	
			try:
				client_log.info("transmitting record to server:[%s]" %i)
				self.logger.info(i)
			except socket.error, e:
				if isinstance(e.args, tuple):
					client_log.error("Socket error occured! errno is [%d]" %e[0])
					if e[0] == errno.EPIPE:
						client_log.error("Detect remote disconnect! errorno errno.EPIPE")
					else:
						client_log.error("Other error, error info [%s]" %e)
				else:
					client_log.error("Socket error [%s]" %e)
			except Exception, e:
				print e
				client_log.error("Exception occured in class Sender while transmiting [%s].exception msg:[%s]" %(i, e))

class SocketLogger:
	def __init__(self, log_name, host, port = logging.handlers.DEFAULT_TCP_LOGGING_PORT):
		self.name = log_name
		self.host = host
		self.port = port
		self.setup()

	def setup(self):
		client_log.debug("Preparing socket logger [%s][%s:%s]" %(self.name, self.host, self.port) )
		self.logger = logging.getLogger(self.name)
		sh = logging.handlers.SocketHandler(self.host, self.port)
		self.logger.setLevel(logging.INFO)
		self.logger.addHandler(sh)

def socket_logger(log_name, host, 
				port = logging.handlers.DEFAULT_TCP_LOGGING_PORT): 
	return SocketLogger(log_name, host, port).logger

def get_last_hour():
	l = time.time() - 60 * 60
	l = int(l)
	return datetime.datetime.fromtimestamp(l).strftime("%Y%m%d%H")

def sender():
	ip = '10.81.12.156'
	port = 50007
	client_log.debug("Ready to connect to [%s:%s]" %(ip, port))

	prefix = "/home/work/newsdi-proxy/log/newsdiproxy.log."
	suffix = get_last_hour()
	filename = prefix + suffix
	#print filename
	client_log.debug("transmit file:[%s]" %filename)

	cmd = "cat %s |grep 'time use'" %filename	
	print cmd
	client_log.debug("using cmd:[%s]" %cmd)
	b = Extractor(cmd)
	#using host_name for server side to identify client
	host_name = socket.gethostname()
	l = socket_logger(host_name, ip, port)
	s = Sender(b.log_list, l)

#global log object for client side
client_log = tool.get_logger("client", "client.log")

def main():
	while True:
		sender()
		for i in range(60, 0, -1):
			client_log.info("%d minutes left to wait " %i)
			time.sleep(60)
	pass
if __name__ == '__main__':
	pass
