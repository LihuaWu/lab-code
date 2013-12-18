import pickle
import sys
import logging
import logging.handlers
import SocketServer
import struct
import collections
import urlparse
import heapq


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
	

def main():
	tcpserver = LogRecordSocketReceiver()
	print('About to start TCP server...')
	tcpserver.serve_until_stopped()


if __name__ == '__main__':
	main()
	pass
