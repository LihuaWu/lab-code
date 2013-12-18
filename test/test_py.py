#!/usr/bin/env python
#encoding: utf-8

class A:
	def __init__(self):
		print "A"

class B(A):
	def __init__(self):
		print "B"
class C(A):
	pass

def test_inherit():
	b = B()
	c = C()
	pass

if __name__ == "__main__":
	test_inherit()
	pass
