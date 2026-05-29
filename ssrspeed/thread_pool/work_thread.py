#coding:utf-8

import threading
import queue

class WorkThread(threading.Thread):

	def __init__(self, tasklist):
		threading.Thread.__init__(self)
		self.tasklist = tasklist
		self.over = threading.Event()
	
	def run(self):
		while not self.over.is_set():
			try:
				task = self.tasklist.get(True, 3)
			except queue.Empty:
				continue
			task.execute()
			self.tasklist.task_done()
			
	def dismiss(self):
		self.over.set()

