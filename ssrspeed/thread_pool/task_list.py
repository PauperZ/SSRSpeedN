#coding:utf-8

import queue
_pool_size = 15
TASK_LIST = queue.Queue(maxsize=_pool_size)

