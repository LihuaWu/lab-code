#!/usr/bin/env python
#coding:utf-8

import sys
import time
import datetime

if not "." in sys.path:
    sys.path.append(".")

import tool 

def serial_validate():
	l = read_file("log.bak")
	for line in l:
		line = line.strip()
		print line 
		cnt += 1
		_validate(line)

def parallel_validate():
	suffix = last_hour()
	filename = "../data/url.%s" %suffix
	l = read_file(filename)
	t = tool.MultiTask(l, _validate)
	t.start_threads(10)
	t.join()

def _validate(suffix):
	prefix = ["http://cq01-testing-news30.vm.baidu.com:8080/sn/api/instantfulltext?url=", "http://cq01-testing-news30.vm.baidu.com:8092/nc_n?m=app&v=detail&tnp=json&from=news_webapp_fulltext&url="] 
	func = [tool.SmartNewsValidator, tool.PcNewsValidator]
	r = tool.Request()
	prefix_len = len(prefix)
	for i in range(prefix_len):
		url = prefix[i] + suffix
		try:
			s = r.get(url)
			p = func[i](suffix, s)
			v = p.validate()
		except Exception, e:
			print e.message, suffix

def main():
	while True:
		parallel_validate()
		for i in range(10, 0, -1):
			print "%d minutes left to wait " %i
			time.sleep(60)
	pass

if __name__ == "__main__":
	main()
