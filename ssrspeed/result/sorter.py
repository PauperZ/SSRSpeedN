#coding:utf-8

class Sorter(object):
	def __init__(self):
		pass

	def __sortBySpeed(self,result):
		return result["dspeed"]

	def __sortByPing(self,result):
		return result["ping"]

	def sortResult(self,result,sortMethod):
		if (sortMethod != ""):
			if (sortMethod == "SPEED"):
				result.sort(key=self.__sortBySpeed,reverse=True)
			elif(sortMethod == "REVERSE_SPEED"):
				result.sort(key=self.__sortBySpeed)
			elif(sortMethod == "PING"):
				result.sort(key=self.__sortByPing)
			elif(sortMethod == "REVERSE_PING"):
				result.sort(key=self.__sortByPing,reverse=True)
		return result
