#!/usr/bin/env python
#coding: utf-8

import sys

if not "../bin/" in sys.path:
	sys.path.append("../bin/")

import grepText

def test_grepText():
	b = grepText.GrepText()
	l = b.grepFile("cat data |grep 'time use'")
	for i in l:
		print i

def test_grepLine():
	s ="NOTICE: 12-11 15:45:15:  newsdiproxy. * 2007337312 [work_thread_func]: send newsdi of url[http://www.chinanews.com/gn/2013/11-12/5489300.shtml?f=baidu] ok,error no[0] all time use[1] 			       	process time use[1] queue wait time [0] queue len is[0] re_crawl_page_times [0]"
	b = grepText.GrepText()
	print b.grepLine(s)

def test_extractor():
	b = grepText.Extractor("cat data.1000 |grep 'time use'")	
	for i in  b.log_list:
		print i

def test_sender():	
	b = grepText.Extractor("cat data |grep 'time use'")	
	logger = grepText.getLogger('will-laptop', 'localhost')
	s = grepText.Sender(b.log_list, logger)
	

if __name__ == '__main__':
	#test_grepText()
	#test_grepLine()
	#test_extractor()
	test_sender()
	pass

