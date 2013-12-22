#! /usr/bin/env python
#coding:utf-8

import sys
import urllib2
import urlparse
import logging
import thread
import time
import json

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

def test_request():
	cnt = 0
	r = server.Request()
	for line in sys.stdin:
		cnt += 1
		line = line.strip()
		try:
			thread.start_new_thread(r.get, (line,))
			if (cnt %100 == 1):
				time.sleep(1)
		except Exception, e:
			print "exception: %s\t%s" %(type(e), line)

def test_multitask():	
	r = server.Request()
	l = [i.strip() for i in sys.stdin]
	t = server.MultiTask(l, r.get)
	t.start_threads(5)
	t.join()
	print "done"

def test_json():
	r = server.Request()
	url ="http://cq01-testing-news30.vm.baidu.com:8080/sn/api/instantfulltext?url=http://news.xinhuanet.com/politics/2013-12/19/c_118631071.htm"
	s = r.get(url)
	print s 
	d = json.loads(s)
	print type(d)

def test_parser(suffix):
	r = server.Request()
	prefix = "http://cq01-testing-news30.vm.baidu.com:8080/sn/api/instantfulltext?url="
	url = prefix+suffix
	try :
		s = r.get(url)
		p = server.SmartNewsValidator(suffix, s)
	except Exception, e:
		print e, suffix

def test_parser_mul():
	l = [i.strip() for i in sys.stdin]
	t = server.MultiTask(l, test_parser)
	t.start_threads(5)
	t.join()
	print "done"

def test_parser_2():
	l = formulate_dict2()
	for i in l:
		s = json.dumps(i)	
		try:
			#p = server.SmartNewsParser("", s)
			p = server.PcNewsValidator("",s)
		except Exception, e:
			print e
			#raise e
	l = formulate_dict()
	for i in l:
		s = json.dumps(i)	
		try:
			p = server.SmartNewsValidator("", s)
			#p = server.PcNewsParser("",s)
		except Exception, e:
			print e
			#raise e

def formulate_dict():
	s = list()
	s.append(dict())
	s[0]["errno"] = 1
	s.append(dict())
	s[1] = dict()
	s[1]["errno"] = 0
	s[1]["data"] = dict()
	s[1]["data"]["news"] = list()
	news = dict()
	news["ts"] = "1"
	news["title"] = "s"
	news["url"] = "d"
	news["site"] = "s"
	l = [{"types": "text", "data":""}]
	news["content"] = l
	
	s[1]["data"]["news"].append(news)
	return [k  for k in s]

def formulate_dict2():
	s = list()
	s.append(dict())
	a = dict()
	a["title"] = "sd"
	a["time"] = "ss"
	a["author"] = "d"
	a["url"] = "s"
	a["isvideo"] = "f"
	l = [{"type" : "text", "data" : "1"}]

	a["content"] = l

	s.append(a)
	return [k for k in s]
		

if __name__ == "__main__":
	logging.basicConfig(format = "%(message)s", level = logging.INFO)
	test_parser_2()
	#test_parser_mul()
	#test_parser()
	#test_json()
	#test_multitask()
	#test_request()
	#test_sort_dict()
	#test_list()
	#test_host()
	#test_urlparse()
	#test_urlparse_fromfile()
	#test_httpget()
	#test_func()

	#test_task()
	#test_server()
	pass
