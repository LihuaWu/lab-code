import pickle
import sys
import logging
import logging.handlers
import SocketServer
import struct
import collections
import urlparse
import heapq
import urllib2
import Queue
import threading
import time
import json


class LogRecordStreamHandler(SocketServer.StreamRequestHandler):

	def handle(self):
		while True:
			chunk = self.connection.recv(4)
			if len(chunk) < 4:
				break
			slen = struct.unpack('>L', chunk)[0]
			chunk = self.connection.recv(slen)
			while len(chunk) < slen:
				chunk = chunk + self.connection.recv(slen - len(chunk))
			record = self.unPickle(chunk)
			self.handleLogRecord(record)

	def unPickle(self, data):
		return pickle.loads(data)

	def printRecord(self,record):
		for i in record:
			print i, record[i]

	def handleLogRecord(self, record):
		for i in self.server.tasks:
			i(record)


class LogRecordSocketReceiver(SocketServer.ThreadingTCPServer):

	allow_reuse_address = 1

	def __init__(self, host='localhost',
			 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
			 handler=LogRecordStreamHandler):
		SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
		self.abort = 0
		self.timeout = 1
		self.logname = None
		self.tasks = list()

	def addTask(self,task):
		print dir(task)
		self.tasks.append(task)

	def serve_until_stopped(self):
		import select
		abort = 0
		while not abort:
			rd, wr, ex = select.select([self.socket.fileno()],
								   [], [],
								   self.timeout)
			if rd:
				self.handle_request()
				abort = self.abort

class HostParser: 

	def __init__(self):
		self.url = dict()
		self.top_lvl_domain = ["com", "cn", "net", "gov", "edu", "org"]
		self.www = "www"

	def parse_host(self, url):	
		p = url.split(":")
		if len(p) == 2:
			self.url["host"], self.url["port"] = p 
		elif len(p) == 1:
			self.url["host"] = url
			self.url["port"] = 80
		else:
			raise Exception("parse host url error")
		pass

	def parse_site(self, host):
		l = host.split('.')
		for i in range(len(l)):
			if l[i] == self.www:
				self.url['main'] = l[i+1]
				break
			elif l[i] in self.top_lvl_domain:
				self.url["main"] = l[i-1]
				self.url["slave"] = l[i-2]
				break
			# deal with cases that use http://ip:port/..., without a domain name
			else:
				continue
		if "main" not in self.url:
			self.url["main"] = host
			logging.info("%s\t%s" %(host, self.url["url"]))

	def parse(self, url):	
		self.url.clear()
		url = url.strip()
		if len(url) <  19 or url[:7] != "http://":
			return 
		self.url["url"] = url
		p_r = urlparse.urlparse(url)
		self.url["parse_result"] = p_r
		self.url["scheme"] = p_r.scheme
		self.url["domain"] = p_r.netloc

		self.parse_host(self.url["domain"])
		self.parse_site(self.url["host"])


class Counter:
	def __init__(self):
		self._cnt = dict()

	def count(self, l = list(),n = 0):

		for i in l:
			if "main" in i:
				main = i["main"]

				if main not in self._cnt:
					self._cnt[main] = dict()
					self._cnt[main]["total"] = 0

				self._cnt[main]["total"] += 1

				if "slave" in i:
					slave = i["slave"]
					if slave not in self._cnt[main]:
						self._cnt[main][slave] = 0
					self._cnt[main][slave] += 1
			else:
				raise Exception("counter exception, host parse error!", i)
		#return sorted(
		#		[(main, slave, cnt)
		#			for main, main_v in self._cnt.items()
		#				for slave, cnt in main_v.items() 
		#					if slave == "total"
		#		],
		#		key = lambda tup: tup[2]
		#		)	
		return heapq.nlargest(
				n  if n  else len(l),
				[(main, slave, cnt)
					for main, main_v in self._cnt.items()
						for slave, cnt in main_v.items() 
							#if slave == "total"
				], key = lambda tup: tup[2]
				)

class Request:	
	def get(self, url):
		#print "%s :download %s" %(ident, url)
		s = urllib2.urlopen(url, timeout = 10)
		l = s.read()
		s.close()
		return l
		#logging.info("%s\t%s" %(e.message, url))

class Validator:
	def __init__(self, url, html):
		self.d = json.loads(html)
		self.u = url
		self.validate()

	def validate(self):
		raise Exception("should use inherited class type !")


class PcNewsValidator(Validator):

	def validate_content(self, content):
		if not isinstance(content, list):
			raise Exception("content type wrong")
		for i in content:
			if "type" not in i or "data" not in i:
				raise Exception("content field absent")
			else:
				i_type = i["type"]
				if i_type not in ["image", "text"]:
					raise Exception("content type unknown")
				
				i_data = i["data"]
				if len(i_data) == 0:
					raise Exception("content data empty")

	def validate(self):

		news = self.d
		for i in ["title", "time", "author", "url", "isvideo", "content"]:
			if i not in news:
				raise Exception("news field absent")
			elif len(news[i]) == 0:
				raise Exception("news field empty!")
			else:
				pass

		content = news["content"]
		self.validate_content(content)

		print "return data correct" 	


class SmartNewsValidator(PcNewsValidator):
	def validate(self):
		if "errno" not in self.d:
			raise Exception("parse data eror")
		else:
			error_no = self.d["errno"]
		if error_no != 0 or "data" not in self.d or "news" not in self.d["data"]:
			#raise Exception("data return false")
			raise Exception("errno false or data and news not exist")
		else:
			news = self.d["data"]["news"][0]

			for i in ["ts", "title", "url", "site", "content"]:
				if len(news[i]) == 0:
					raise Exception("news field empty")
			else:
				content = news["content"]
				self.validate_content(content)

		print "return data correct" 	


class MultiTask:
	def __init__(self, record, func):
		if record == None:
			raise Exception("record should not be none!")
		if func == None:
			raise Exception("a handle function should be provided")

		self.q = Queue.Queue()

		for i in record:
			self.q.put(i)

		self.f = func

	def start_threads(self, thread_num = 1):

		if (thread_num <= 0):
			raise Exception("thread number must be a positive number!")

		for i in range(thread_num):
			w = threading.Thread(target = self.handle)
			w.start()

	def handle(self):
		while not self.q.empty():
			i = self.q.get()
			self.f(i)
			self.q.task_done()

		#print "%s exit" %ident

	def join(self):
		self.q.join()
	

def main():
	tcpserver = LogRecordSocketReceiver()
	print('About to start TCP server...')
	tcpserver.serve_until_stopped()


if __name__ == '__main__':
	main()
	pass
