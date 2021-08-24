# -*- coding: utf-8 -*-

class WebErrorBase(object):
	errMsg = ""
	errTag = ""
	def __init__(self):
		raise TypeError("Web Errors should not be instantiated.")
		
