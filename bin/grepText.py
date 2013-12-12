#!/usr/bin/python
#coding:utf-8

import urllib
import popen2
import re
	
def test_popen():
	r = popen2.Popen4("cat grepText.py |grep test")
	print r.poll()
	s = r.wait()
	print s
	
	s = r.fromchild.readlines()
	for i in s:
		print i.strip()

class GrepText:
	def grepFile(self, cmd):
		r = popen2.Popen4(cmd)
		# r.wait() returns the status code of wait()
		s = r.fromchild.readlines()
		return [i.strip() for i in s]

	def grepLine(self, line):
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

class Handler:
	def handle(self):
		pass
		

	

if __name__ == '__main__':
	pass

