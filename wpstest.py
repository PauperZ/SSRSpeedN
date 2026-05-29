#coding:utf-8

import time
import sys
import os
import logging

from config import config

if (not os.path.exists("./logs/")):
	os.mkdir("./logs/")
if (not os.path.exists("./results/")):
	os.mkdir("./results/")

loggerList = []
loggerSub = logging.getLogger("Sub")
logger = logging.getLogger(__name__)
loggerList.append(loggerSub)
loggerList.append(logger)

formatter = logging.Formatter("[%(asctime)s][%(levelname)s][%(thread)d][%(filename)s:%(lineno)d]%(message)s")
fileHandler = logging.FileHandler("./logs/" + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".log",encoding="utf-8")
fileHandler.setFormatter(formatter)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)

import SSRSpeed.SpeedTest.Methods.webpage_simulation as webPageSimulation

for item in loggerList:
	item.setLevel(logging.DEBUG)
	item.addHandler(fileHandler)
	item.addHandler(consoleHandler)

webPageSimulation.startWebPageSimulationTest("127.0.0.1", 1080)
