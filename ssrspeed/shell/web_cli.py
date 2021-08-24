#coding:utf-8

import logging
import sys
from optparse import OptionParser

from config import config

logger = logging.getLogger("Sub")

def setArgsListCallback(option,opt_str,value,parser):
	assert value is None
	value = []
	def floatable(arg):
		try:
			float(arg)
			return True
		except ValueError:
			return False
	for arg in parser.rargs:
		if (arg[:2] == "--" and len(arg) > 2):
			break
		if (arg[:1] == "-" and len(arg) > 1 and not floatable(arg)):
			break
		if (arg.replace(" ","") == ""):
			continue
		value.append(arg)
	del parser.rargs[:len(value)]
	setattr(parser.values,option.dest,value)

def setOpts(parser):
	parser.add_option(
		"-l","--listen",
		action="store",
		dest="listen",
		default=config["web"]["listen"],
		help="Set listen address for web server."
		)
	parser.add_option(
		"-p","--port",
		action="store",
		dest="port",
		default=config["web"]["port"],
		help="Set listen port for web server."
		)
	parser.add_option(
		"--skip-requirements-check",
		action="store_true",
		dest="skip_requirements_check",
		default=False,
		help="Skip requirements check."
		)
	parser.add_option(
		"--debug",
		action="store_true",
		dest="debug",
		default=False,
		help="Run program in debug mode."
		)
	parser.add_option(
		"--paolu",
		action="store_true",
		dest="paolu",
		default=False,
		help="如题"
		)

def init(VERSION):
	parser = OptionParser(usage="Usage: %prog [options] arg1 arg2...",version="SSR Speed Web Api " + VERSION)
	setOpts(parser)
	(options,args) = parser.parse_args()
	return (options,args)
