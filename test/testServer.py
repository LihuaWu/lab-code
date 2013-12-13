#! /usr/bin/env python
#coding:utf-8

import sys

if not "../bin/" in sys.path:
	sys.path.append("../bin/")

import server

def test_server():
	tcp_server = server.LogRecordSocketReceiver()
	print("About to start tcp server...") 
	tcp_server.serve_until_stopped()


if __name__ == "__main__":
	test_server()
