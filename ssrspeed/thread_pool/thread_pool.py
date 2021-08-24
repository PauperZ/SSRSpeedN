#coding:utf-8

import threading
import queue

from .work_thread import WorkThread

class ThreadPool:

	def __init__(self, maxsize, tasklist):
		if maxsize < 0:
			raise ValueError("Thread must be more than 0.")
		
		self.tasklist = tasklist		
		self.workthreads = []
		
		for i in range(maxsize):
			workthread = WorkThread(self.tasklist)
			self.workthreads.append(workthread)
			workthread.start()
		
	def join(self):
		self.tasklist.join()
		for workthread in self.workthreads:
			workthread.dismiss()
		
	def isOver(self):
		return self.tasklist.empty()
