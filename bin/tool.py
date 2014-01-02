#!/usr/bin/env python
#coding:utf-8

import collections
import urlparse
import heapq
import urllib2
import Queue
import threading
import time
import json
import datetime
import logging
import logging.handlers

def last_hour():
	l = time.time() - 60 * 60
	l = int(l)
	return datetime.datetime.fromtimestamp(l).strftime("%Y%m%d%H")

def read_file(filename):
	l = list()
	try:
		with open(filename, 'r') as f:
			l = f.readlines()
	except Exception, e:
		raise e
	return [i.strip() for i in l]

def get_logger(name, log_name = "../logs/%s.log" %name):
	logger = logging.getLogger(name)
	logger.setLevel(logging.DEBUG)
	fh = logging.FileHandler(log_name)
	fh.setLevel(logging.DEBUG)
	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)
	fmt = logging.Formatter("[%(asctime)s]-[%(name)s]-[%(levelname)s]-[%(message)s]")
	fh.setFormatter(fmt)
	ch.setFormatter(fmt)
	logger.addHandler(fh)
	logger.addHandler(ch)
	return logger

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
		return self.url


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
	log = get_logger("validator")
	def __init__(self, url, html):
		self.d = json.loads(html)
		self.u = url

	def validate(self):
		raise Exception("should use inherited class type !")


class PcNewsValidator(Validator):

	def validate_content(self, content):

		if not isinstance(content, list):
			self.log.error("in class [%s] url [%s] content type wrong" %(self.name, self.u))	
			return False

		for i in content:
			if "type" not in i or "data" not in i:
				self.log.error("in class [%s] url[%s] content field absent" %(self.name, self.u))
				return False
			else:
				i_type = i["type"]
				if i_type not in ["image", "text"]:
					self.log.error("in class [%s] url[%s] content type unknown" %(self.name, self.u))
					return False
				
				i_data = i["data"]
				if len(i_data) == 0:
					self.log.error("in class [%s] url[%s] content data empty" %(self.name, self.u))
					return False

		return True


	def validate(self):
		self.name = "PCNewsValidator"

		news = self.d
		for i in ["title", "time", "author", "url", "isvideo", "content"]:
			if i not in news:
				self.log.error("in class [%s] url[%s]: news field absent" %(self.name, self.u))
				return False
			elif len(news[i]) == 0:
				self.log.error("in class [%s] url[%s] news field empty!" %(self.name, self.u))
				return False
			else:
				pass

		content = news["content"]
		flag = self.validate_content(content)
		if flag:
			self.log.info("in class [%s] url [%s] return data correct" %(self.name, self.u))
		else: 
			self.log.error("in class [%s] url [%s] return data wrong" %(self.name, self.u))
		return flag


class SmartNewsValidator(PcNewsValidator):

	def validate(self):
		self.name = "SmartNewsValidator"

		flag = False

		if "errno" not in self.d:
			self.log.error("in class [%s] url[%s] parse data error" %(self.name, self.u))
			return False;
		else:
			error_no = self.d["errno"]
		if error_no != 0 or "data" not in self.d or "news" not in self.d["data"]:
			#raise Exception("data return false")
			self.log.error("in class [%s] url[%s] errno false or data and news not exist" %(self.name, self.u))
			return False
		else:
			news = self.d["data"]["news"][0]

			for i in ["ts", "title", "url", "site", "content"]:
				if len(news[i]) == 0:
					self.log.error("in class [%s] url[%s] news field empty" %(self.name, self.u))
					return False
			else:
				content = news["content"]
				flag = self.validate_content(content)

		if flag:
			self.log.info("in class [%s] url [%s] return data correct" %(self.name, self.u)) 
		else:
			self.log.error("in class [%s] url [%s] return data wrong" %(self.name, self.u))
		return flag


class MultiTask:

	log = get_logger("multi-task")

	def __init__(self, record, func):
		if record == None:
			self.log.error("record should not be none!")
			raise Exception("record should not be none!")
		if func == None:
			self.log.error("a handle function should be provided")
			raise Exception("a handle function should be provided")

		self.q = Queue.Queue()
		for i in record:
			self.q.put(i)

		self.f = func


	def start_threads(self, thread_num = 1):

		if (thread_num <= 0):
			self.log.error("thread number must be a positive number!")
			raise Exception("thread number must be a positive number!")

		for i in range(thread_num):
			w = threading.Thread(target = self.handle)
			w.start()

	def handle(self):
		while not self.q.empty():
			i = self.q.get()
			self.log.info("url [%s]" %i)
			self.f(i)
			self.q.task_done()

	def join(self):
		self.q.join()

def get_url_freq(record):
	pass
