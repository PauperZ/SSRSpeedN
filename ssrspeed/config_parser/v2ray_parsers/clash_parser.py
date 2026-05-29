#coding:utf-8

import logging
import yaml
import json

logger = logging.getLogger("Sub")

class ParserV2RayClash(object):
	def __init__(self):
		self.__clashVmessConfigs = []
		self.__decodedConfigs = []

	def __clashConfigConvert(self,clashCfg):
		server = clashCfg["server"]
		remarks = clashCfg.get("name",server)
		remarks = remarks if remarks else server
		group = "N/A"
		port = int(clashCfg["port"])
		uuid = clashCfg["uuid"]
		aid = int(clashCfg["alterId"])
		security = clashCfg.get("cipher","auto")
		tls = "tls" if (clashCfg.get("tls",False)) else "" #TLS
		allowInsecure = True if (clashCfg.get("skip-cert-verify",False)) else False
		net = clashCfg.get("network","tcp") #ws,tcp
		_type = clashCfg.get("type","none") #Obfs type
		wsHeader = clashCfg.get("ws-headers",{})
		host = wsHeader.get("Host","") # http host,web socket host,h2 host,quic encrypt method
		headers = {}
		for header in wsHeader.keys():
			if (header != "Host"):
				headers[header] = wsHeader[header]
		tlsHost = host
		path = clashCfg.get("ws-path","") #Websocket path, http path, quic encrypt key
		logger.debug("Server : {},Port : {}, tls-host : {}, Path : {},Type : {},UUID : {},AlterId : {},Network : {},Host : {},TLS : {},Remarks : {},group={}".format(
				server,
				port,
				tlsHost,
				path,
				_type,
				uuid,
				aid,
				net,
				host,
				tls,
				remarks,
				group
			)
		)
		return {
			"remarks":remarks,
			"group":group,
			"server":server,
			"server_port":port,
			"id":uuid,
			"alterId":aid,
			"security":security,
			"type":_type,
			"path":path,
			"allowInsecure":allowInsecure,
			"network":net,
			"headers":headers,
			"tls-host":tlsHost,
			"host":host,
			"tls":tls
		}
	
	def __parseConfig(self,clashCfg):
		for cfg in clashCfg["Proxy"]:
			if (cfg.get("type","N/A").lower() == "vmess"):
				self.__clashVmessConfigs.append(cfg)
			else:
				pass
			#	logger.info("Config {}, type {} not support.".format(
			#		cfg["name"],
			#		cfg["type"]
			#		)
			#	)
	#	logger.debug("Read {} configs.".format(
	#		len(self.__clashVmessConfigs)
	#		)
	#	)
		for cfg in self.__clashVmessConfigs:
			self.__decodedConfigs.append(self.__clashConfigConvert(cfg))
		
	def parseSubsConfig(self,config):
		try:
			clashCfg = yaml.load(config,Loader=yaml.FullLoader)
		except:
			logger.exception("Not Clash config.")
			return False
		self.__parseConfig(clashCfg)
		return self.__decodedConfigs

	def parseGuiConfig(self,filename):
		with open(filename,"r+",encoding="utf-8") as f:
			try:
				clashCfg = yaml.load(f,Loader=yaml.FullLoader)
			except:
				logger.exception("Not Clash config.")
				return False
		self.__parseConfig(clashCfg)
		return self.__decodedConfigs

if (__name__ == "__main__"):
	cvp = ParserV2RayClash()
	cvp.parseGuiConfig("./config.example.yml")


