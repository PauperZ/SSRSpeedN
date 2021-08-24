#coding:utf-8

import urllib.parse
import logging
import json
logger = logging.getLogger("Sub")

from ...utils import b64plus

class ParserV2RayQuantumult(object):
	def __init__(self):
		pass

	def parseSubsConfig(self,rawLink):
		link = rawLink[8:]
		linkDecoded = b64plus.decode(link).decode("utf-8")
		try:
			linkSplited = linkDecoded.split(",")
			
			new_list = []
			while True:
				try:
					item = linkSplited.pop(0)
				except IndexError:
					break
				text = item
				while text.count("\"") % 2 != 0:
					try:
						text += ", {}".format(linkSplited.pop(0))
					except IndexError:
						raise ValueError("Invalid Quantumult URL.")
				new_list.append(text)
			linkSplited = new_list

			remarks = linkSplited[0].split(" = ")[0]
			server = linkSplited[1]
			remarks = remarks if remarks else server
			port = int(linkSplited[2])
			security = linkSplited[3]
			uuid = linkSplited[4].replace("\"","")
			group = linkSplited[5].split("=")[1]
			tls = ""
			tlsHost = ""
			host = "" # http host,web socket host,h2 host,quic encrypt method
			net = "tcp"
			path = "" #Websocket path, http path, quic encrypt key
			headers = []

			if (linkSplited[6].split("=")[1] == "true"):
				tls = "tls"
				tlsHost = linkSplited[7].split("=")[1]
				allowInsecure = False if (linkSplited[8].split("=")[1] == "1") else True
			else:
				allowInsecure = True
			i = 7
			if (tls):
				i = 8
			if len(linkSplited) == 11 or len(linkSplited) == 12:
				net = linkSplited[i+1].split("=")[1]
				path = linkSplited[i+2].split("=")[1].replace("\"","")
				header = linkSplited[i+3].split("=")[1].replace("\"","").split("[Rr][Nn]")
				if (len(header) > 0):
					host = header[0].split(":")[1].strip()
					for h in range(1,len(header)):
						headers.append(
							{
								"header":header[h].split(":")[0].strip(),
								"value":header[h].split(":")[1].strip()
							}
						)

			_type = "none" #Obfs type under tcp mode
			aid = 0
			logger.debug("Server : {},Port : {}, tls-host : {}, Path : {},Type : {},UUID : {},AlterId : {},Network : {},Host : {}, Headers : {},TLS : {},Remarks : {},group={}".format(
				server,
				port,
				tlsHost,
				path,
				_type,
				uuid,
				aid,
				net,
				host,
				headers,
				tls,
				remarks,
				group
			))
			_config = {
				"remarks":remarks,
				"group":group,
				"server":server,
				"server_port":port,
				"id":uuid,
				"alterId":aid,
				"security":security,
				"allowInsecure":allowInsecure,
				"type":_type,
				"path":path,
				"network":net,
				"host":host,
				"headers":headers,
				"tls":tls,
				"tls-host":tlsHost
			}
			return _config
		except:
			logger.exception("Parse {} failed.(Quantumult Method)".format(rawLink))
			return None

	
