import pickle
import sys
import logging
import logging.handlers
import SocketServer
import struct
import time

if "." not in sys.path:
	sys.path.append(".")

import tool

class LogRecordStreamHandler(SocketServer.StreamRequestHandler):

	log = tool.get_logger('log_record_handler')

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

	def last_hour(self):
		l = time.time() - 60 * 60
		l = int(l)
		return datetime.datetime.fromtimestamp(l).strftime("%Y%m%d%H")

	def printRecord(self,record):

		suffix = self.last_hour()
		filename = "../data/url.%s" %suffix
		with open(filename, 'a') as f:
			if "msg" in record and "url" in record["msg"]:
				name = "Unknown"
				if "name" in  record:
					name = record["name"]
				url = record["msg"]["url"]

				self.log.info("[%s]-[%s]" %(name, url))

				url = url +"\n"
				#print url,
				f.write(url)

	def handleLogRecord(self, record):
		self.printRecord(record)
		#d = self.server.db
		#if "msg" in record and "url" in record["msg"]:
		#	url = record["msg"]["url"]
		#	d.execute(url)
		#d.commit()
		#d.show()

class LogRecordSocketReceiver(SocketServer.ForkingTCPServer):

	allow_reuse_address = 1

	def __init__(self, host='',
			 port=50007,
			 handler=LogRecordStreamHandler):
		SocketServer.ForkingTCPServer.__init__(self, (host, port), handler)
		self.abort = 0
		self.timeout = 1
		self.logname = None
		#self.db.create()

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

def main():
	tcpserver = LogRecordSocketReceiver()
	print('About to start TCP server...')
	tcpserver.serve_until_stopped()

if __name__ == '__main__':
	main()
	pass
