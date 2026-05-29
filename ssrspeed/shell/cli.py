#coding:utf-8

import logging
import sys
from optparse import OptionParser

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
#	print(parser.values)
#	print(option.dest)
#	print(opt_str)
	del parser.rargs[:len(value)]
	setattr(parser.values,option.dest,value)
#	print(value)

def setOpts(parser):
	parser.add_option(
		"-c","--config",
		action="store",
		dest="guiConfig",
		default="",
		help="Load configurations from file."
		)
	parser.add_option(
		"-u","--url",
		action="store",
		dest="url",
		default="",
		help="Load ssr config from subscription url."
		)
	parser.add_option(
		"-m","--method",
		action="store",
		dest="test_method",
		default="socket",
		help="Select test method in [speedtestnet, fast, socket, stasync]."
		)
	parser.add_option(
		"-M","--mode",
		action="store",
		dest="test_mode",
		default="all",
		help="Select test mode in [all,wps,pingonly]."
		)
	parser.add_option(
		"--include",
		action="callback",
		callback = setArgsListCallback,
		dest="filter",
		default = [],
		help="Filter nodes by group and remarks using keyword."
		)
	parser.add_option(
		"--include-remark",
		action="callback",
		callback = setArgsListCallback,
		dest="remarks",
		default=[],
		help="Filter nodes by remarks using keyword."
		)
	parser.add_option(
		"--include-group",
		action="callback",
		callback = setArgsListCallback,
		dest="group",
		default=[],
		help="Filter nodes by group name using keyword."
		)
	parser.add_option(
		"--exclude",
		action="callback",
		callback = setArgsListCallback,
		dest="efliter",
		default = [],
		help="Exclude nodes by group and remarks using keyword."
		)
	parser.add_option(
		"--exclude-group",
		action="callback",
		callback = setArgsListCallback,
		dest="egfilter",
		default=[],
		help="Exclude nodes by group using keyword."
		)
	parser.add_option(
		"--exclude-remark",
		action="callback",
		callback = setArgsListCallback,
		dest="erfilter",
		default = [],
		help="Exclude nodes by remarks using keyword."
	)
	parser.add_option(
		"--use-ssr-cs",
		action="store_true",
		dest="use_ssr_cs",
		default = False,
		help="Replace the ShadowsocksR-libev with the ShadowsocksR-C# (Only Windows)."
	)
	parser.add_option(
		"-g",
		action="store",
		dest="group_override",
		default="",
		help="Manually set group."
	)
	'''
	parser.add_option(
		"-t","--type",
		action="store",
		dest="proxy_type",
		default = "ssr",
		help="Select proxy type in [ssr,ssr-cs,ss,v2ray],default ssr."
		)
	'''
	parser.add_option(
		"-y","--yes",
		action="store_true",
		dest="confirmation",
		default=False,
		help="Skip node list confirmation before test."
		)
	parser.add_option(
		"-C","--color",
		action="store",
		dest="result_color",
		default="",
		help="Set the colors when exporting images.."
		)
	'''
	parser.add_option(
		"-s","--split",
		action="store",
		dest="split_count",
		default="-1",
		help="Set the number of nodes displayed in a single image when exporting images."
	'''
	parser.add_option(
		"-s","--sort",
		action="store",
		dest="sort_method",
		default="",
		help="Select sort method in [speed,rspeed,ping,rping],default not sorted."
		)
	parser.add_option(
		"-i","--import",
		action="store",
		dest="import_file",
		default="",
		help="Import test result from json file and export it."
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
	parser = OptionParser(usage="Usage: %prog [options] arg1 arg2...",version="SSR Speed Tool " + VERSION)
	setOpts(parser)
	if (len(sys.argv) == 1):
		parser.print_help()
		sys.exit(0)
	(options,args) = parser.parse_args()
	return (options,args)

