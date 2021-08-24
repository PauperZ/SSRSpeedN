# coding:utf-8

import copy
	
V2RayBaseConfig = {
	"remarks": "",
	"group": "N/A",
	"server": "",
	"server_port": "",
	"log": {"access": "", "error": "", "loglevel": "warning"},
	"inbounds": [
		{
			"port": 1087,
			"listen": "127.0.0.1",
			"protocol": "socks",
			"sniffing": {"enabled": True, "destOverride": ["http", "tls"]},
			"settings": {"auth": "noauth", "udp": True, "ip": None, "clients": None},
			"streamSettings": None,
		}
	],
	"outbounds": [
		{
			"tag": "proxy",
			"protocol": "vmess",
			"settings": {
				"vnext": [
					{
						"address": "",
						"port": 1,
						"users": [
							{"id": "", "alterId": 0, "email": "", "security": "auto"}
						],
					}
				],
				"servers": None,
				"response": None,
			},
			"streamSettings": {
				"network": "",
				"security": "",
				"tlsSettings": {},
				"tcpSettings": {},
				"kcpSettings": {},
				"wsSettings": {},
				"httpSettings": {},
				"quicSettings": {},
			},
			"mux": {"enabled": True},
		},
		{
			"tag": "direct",
			"protocol": "freedom",
			"settings": {"vnext": None, "servers": None, "response": None},
			"streamSettings": {},
			"mux": {},
		},
		{
			"tag": "block",
			"protocol": "blackhole",
			"settings": {"vnext": None, "servers": None, "response": {"type": "http"}},
			"streamSettings": {},
			"mux": {},
		},
	],
	"dns": {},
	"routing": {"domainStrategy": "IPIfNonMatch", "rules": []},
}

tcpSettingsObject = {
	"connectionReuse": True,
	"header": {
		"type": "http",
		"request": {
			"version": "1.1",
			"method": "GET",
			"path": ["/pathpath"],
			"headers": {
				"Host": ["hosthost.com", "test.com"],
				"User-Agent": [
					"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
					"Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_2 like Mac OS X) AppleWebKit/601.1 (KHTML, like Gecko) CriOS/53.0.2785.109 Mobile/14A456 Safari/601.1.46",
				],
				"Accept-Encoding": ["gzip, deflate"],
				"Connection": ["keep-alive"],
				"Pragma": "no-cache",
			},
		},
		"response": None,
	},
}

quicSettingsObject = {
	"security": "none",
	"key": "",
	"header": {
		"type": "none",
		"request": None,
		"response": None
	}
}
httpSettingsObject = {
	"path": "",
	"host": [
		"aes-128-gcm"
	]
}
webSocketSettingsObject = {
	"connectionReuse": True,
	"path": "",
	"headers": {
		"Host": ""
	}
}

tlsSettingsObject = {
	"allowInsecure": True,
	"serverName": ""
}

class V2RayBaseConfigs:

	@staticmethod
	def get_tls_object():
		return copy.deepcopy(tlsSettingsObject)

	@staticmethod
	def get_ws_object():
		return copy.deepcopy(webSocketSettingsObject)

	@staticmethod
	def get_http_object():
		return copy.deepcopy(httpSettingsObject)

	@staticmethod
	def get_tcp_object():
		return copy.deepcopy(tcpSettingsObject)

	@staticmethod
	def get_quic_object():
		return copy.deepcopy(quicSettingsObject)

	@staticmethod
	def get_config():
		return copy.deepcopy(V2RayBaseConfig)
	
	@staticmethod
	def generate_config(config: dict, listen: str = "127.0.0.1", port: int = 1087) -> dict:
		_config = V2RayBaseConfigs.get_config()

		_config["inbounds"][0]["listen"] = listen
		_config["inbounds"][0]["port"] = port

		#Common
		_config["remarks"] = config["remarks"]
		_config["group"] = config.get("group","N/A")
		_config["server"] = config["server"]
		_config["server_port"] = config["server_port"]

		#stream settings
		streamSettings = _config["outbounds"][0]["streamSettings"]
		streamSettings["network"] = config["network"]
		if (config["network"] == "tcp"):
			if (config["type"] == "http"):
				tcpSettings = V2RayBaseConfigs.get_tcp_object()
				tcpSettings["header"]["request"]["path"] = config["path"].split(",")
				tcpSettings["header"]["request"]["headers"]["Host"] = config["host"].split(",")
				streamSettings["tcpSettings"] = tcpSettings
		elif (config["network"] == "ws"):
			webSocketSettings = V2RayBaseConfigs.get_ws_object()
			webSocketSettings["path"] = config["path"]
			webSocketSettings["headers"]["Host"] = config["host"]
			for h in config.get("headers",[]):
				webSocketSettings["headers"][h["header"]] = h["value"]
			streamSettings["wsSettings"] = webSocketSettings
		elif(config["network"] == "h2"):
			httpSettings = V2RayBaseConfigs.get_http_object()
			httpSettings["path"] = config["path"]
			httpSettings["host"] = config["host"].split(",")
			streamSettings["httpSettings"] = httpSettings
		elif(config["network"] == "quic"):
			quicSettings = V2RayBaseConfigs.get_quic_object()
			quicSettings["security"] = config["host"]
			quicSettings["key"] = config["path"]
			quicSettings["header"]["type"] = config["type"]
			streamSettings["quicSettings"] = quicSettings

		streamSettings["security"] = config["tls"]
		if (config["tls"] == "tls"):
			tlsSettings = V2RayBaseConfigs.get_tls_object()
			tlsSettings["allowInsecure"] = True if (config.get("allowInsecure","false") == "true") else False
			tlsSettings["serverName"] = config.get("tls-host", "")
			streamSettings["tlsSettings"] = tlsSettings

		_config["outbounds"][0]["streamSettings"] = streamSettings

		outbound = _config["outbounds"][0]["settings"]["vnext"][0]
		outbound["address"] = config["server"]
		outbound["port"] = config["server_port"]
		outbound["users"][0]["id"] = config["id"]
		outbound["users"][0]["alterId"] = config["alterId"]
		outbound["users"][0]["security"] = config["security"]
		_config["outbounds"][0]["settings"]["vnext"][0] = outbound
		return _config

