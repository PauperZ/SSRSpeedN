#coding:utf-8

class AbstractTask(object):
	def __init__(self, *args, **kwargs):
		self.__args = args
		self.__kwargs = kwargs

	def execute(self):
		raise NotImplementedError
		
