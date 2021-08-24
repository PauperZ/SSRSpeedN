#coding:utf-8

import time
import sys
import os
import json
import threading
import urllib.parse
import logging

from config import config

from flask import Flask,request,redirect#,render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename

from ssrspeed.utils import RequirementsCheck, check_platform
from ssrspeed.utils.web import getPostData

from ssrspeed.core.ssrspeed_core import SSRSpeedCore
from ssrspeed.shell import web_cli as console_cfg

from ssrspeed.result import ExportResult
from ssrspeed.result import importResult

from ssrspeed.types.errors.webapi.error_file_not_allowed import FileNotAllowed
from ssrspeed.types.errors.webapi.error_file_common import WebFileCommonError

WEB_API_VERSION = config["WEB_API_VERSION"]

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

TEMPLATE_FOLDER = "./resources/webui/templates"
STATIC_FOLDER = "./resources/webui/statics"
UPLOAD_FOLDER = "./tmp/uploads"
ALLOWED_EXTENSIONS = set(["json", "yml"])

app = Flask(__name__,
	template_folder=TEMPLATE_FOLDER,
	static_folder=STATIC_FOLDER,
	static_url_path=""
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
CORS(app)
sc = None

@app.route("/",methods=["GET"])
def index():
	return redirect("https://web1.ospf.in/", 301)
	#return render_template(
	#	"index.html"
	#	)

'''
	{
		"proxyType":"SSR", //[SSR,SSR-C#,SS,V2RAY]
		"testMethod":"SOCKET", //[SOCKET,SPEED_TEST_NET,FAST]
		"testMode":"",//[ALL,TCP_PING,WEB_PAGE_SIMULATION]
		"subscriptionUrl":"",
		"colors":"origin",
		"sortMethod":"",//[SPEED,REVERSE_SPEED,PING,REVERSE_PING]
		"include":[],
		"includeGroup":[],
		"includeRemark":[],
		"exclude":[],
		"excludeGroup":[],
		"excludeRemark":[]
	}
'''

@app.route("/getversion",methods=["GET"])
def getVersion():
	return json.dumps(
		{
			"main":config["VERSION"],
			"webapi":config["WEB_API_VERSION"]
		}
	)

@app.route("/status",methods=["GET"])
def status():
	return sc.web_get_status()

@app.route("/readsubscriptions",methods=["POST"])
def readSubscriptions():
	if (request.method == "POST"):
		data = getPostData()
		if (sc.web_get_status() == "running"):
			return 'running'
		subscriptionUrl = data.get("url","")
		#proxyType = data.get("proxyType","SSR")
		if (not subscriptionUrl):
			return "invalid url."
		return json.dumps(sc.web_read_subscription(subscriptionUrl))

def check_file_allowed(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/readfileconfig", methods=["POST"])
def readFileConfig():
	if request.method == "POST":
		if (sc.web_get_status() == "running"):
			return 'running'
		ufile = request.files["file"]
		#data = getPostData()
		if ufile:
			if check_file_allowed(ufile.filename):
				filename = secure_filename(ufile.filename)
				tmpFilename = os.path.join(app.config["UPLOAD_FOLDER"], filename)
				ufile.save(tmpFilename)
				logger.info("Tmp config file saved as {}".format(tmpFilename))
				return json.dumps(sc.web_read_config_file(tmpFilename))
			else:
				logger.error("Disallowed file {}".format(ufile.filename))
				return FileNotAllowed.errMsg
		else:
			logger.error("File upload failed or unknown error.")
			return WebFileCommonError.errMsg

@app.route("/getcolors",methods=["GET"])
def getColors():
	return json.dumps(sc.web_get_colors())

@app.route('/start',methods=["POST"])
def startTest():
	if (request.method == "POST"):
		data = getPostData()
	#	return "SUCCESS"
		if (sc.web_get_status() == "running"):
			return 'running'
		configs = data.get("configs",[])
		if (not configs):
			return "No configs"
		#proxyType =data.get("proxyType","SSR")
		testMethod =data.get("testMethod", "ST_ASYNC")
		colors =data.get("colors", "origin")
		sortMethod =data.get("sortMethod", "")
		testMode = data.get("testMode", "")
		use_ssr_cs = data.get("useSsrCSharp", False)
		group = data.get("group", "")
		sc.web_setup(
			testMode = testMode,
			testMethod = testMethod,
			colors = colors,
			sortMethod = sortMethod
		)
		sc.clean_result()
		sc.web_set_configs(configs)
		if group:
			sc.set_group(group)
		sc.start_test(use_ssr_cs)
		return 'done'
	return 'invalid method'

@app.route('/getresults')
def getResults():
	return json.dumps(sc.web_get_results())

if (__name__ == "__main__"):
	pfInfo = check_platform()
	if (pfInfo == "Unknown"):
		logger.critical("Your system does not supported.Please contact developer.")
		sys.exit(1)

	DEBUG = False
	
	options,args = console_cfg.init(WEB_API_VERSION)

	if (options.paolu):
		for root, dirs, files in os.walk(".", topdown=False):
			for name in files:
				try:
					os.remove(os.path.join(root, name))
				except:
					pass
			for name in dirs:
				try:
					os.remove(os.path.join(root, name))
				except:
					pass
		sys.exit(0)
	
	if (options.debug):
		DEBUG = options.debug
		for item in loggerList:
			item.setLevel(logging.DEBUG)
			item.addHandler(fileHandler)
			item.addHandler(consoleHandler)
	else:
		for item in loggerList:
			item.setLevel(logging.INFO)
			item.addHandler(fileHandler)
			item.addHandler(consoleHandler)

	logger.info("SSRSpeed {}, Web Api Version {}".format(config["VERSION"], config["WEB_API_VERSION"]))

	if (logger.level == logging.DEBUG):
		logger.debug("Program running in debug mode")

	if not options.skip_requirements_check:
		rc = RequirementsCheck()
		rc.check()
	else:
		logger.warn("Requirements check skipped.")

	sc = SSRSpeedCore()
	sc.webMode = True
	if not os.path.exists(UPLOAD_FOLDER):
		logger.warn("Upload folder {} not found, creating.".format(UPLOAD_FOLDER))
		os.makedirs(UPLOAD_FOLDER)
	app.run(host=options.listen,port=int(options.port),debug=DEBUG,threaded=True)

