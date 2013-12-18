#! /usr/bin/env python
#coding:utf-8

import sys
import urllib2
import urlparse
import logging

if not "../bin/" in sys.path:
	sys.path.append("../bin/")

import server

def printLog(record):
	print record['msg']['url']

def test_server():
	tcp_server = server.LogRecordSocketReceiver()
	print("About to start tcp server...") 
	tcp_server.addTask(printLog)
	tcp_server.serve_until_stopped()

def test_task():
	a = server.Task()
	pass

def test_func():
	print dir(test_func)
	print printLog.__call__
	print printLog.func_name
	print printLog.func_dict
	print printLog.func_code

def test_httpget():
	url = "http://cp01-testing-news25.cp01.baidu.com:8091/nc_n?m=app&v=detail&tnp=json&from=news_webapp_fulltext&url=http://china.haiwainet.cn/n/2013/1211/c345646-20022475.html"
	print urllib2.urlopen(url2).read()
	pass

def test_urlparse():
	u = server.HostParser()
	url = "http://china.haiwainet.cn/n/2013/1211/c345646-20022475.html"
	u.parse(url)
	#for line in sys.stdin:
	#	u.parse(line)

def test_urlparse_fromfile():
	logging.info("test url parse from file")
	u = server.HostParser()
	l = list()
	for line in sys.stdin:
		u.parse(line)
		r = dict(u.url)
		if len(r) > 0:
			l.append(r)
		else:	
			continue

	cnt = server.Counter()
	print cnt.count(l, 10)

def test_host():
	s = server.Host()
	s.main="test"
	s.slave = "1"
	print s.main
	print s
	s.main="ddt"
	print s.main

def test_list():
	s = "s"
	lis = ["r","ss", "t"]
	if s in lis:
		print "Yes"
	else:
		print "No"

def test_sort_dict():
	d = {1:{2:0.3, 3:0.4}, 2:{8:0.2}}
	s = [(value, id1, id2) for id1, d1 in d.items() for id2, value in d1.items()]
	print sorted(s)

def test_log():
	logging.basicConfig(format = "%(message)s", level = logging.DEBUG)
	logging.info("test log")

if __name__ == "__main__":
	logging.basicConfig(format = "%(message)s", level = logging.INFO)
	#test_sort_dict()
	#test_list()
	#test_host()
	#test_urlparse()
	test_urlparse_fromfile()
	#test_httpget()
	#test_func()

	#test_task()
	#test_server()
	pass
