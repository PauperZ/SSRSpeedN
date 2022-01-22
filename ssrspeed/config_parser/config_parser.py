# -*- coding: utf-8 -*-

import binascii
from copy import deepcopy
import json
import logging
import requests

from ..utils import b64plus
from ..types.nodes import NodeShadowsocks, NodeShadowsocksR, NodeV2Ray
from .base_configs import shadowsocks_get_config, V2RayBaseConfigs
from .shadowsocks_parsers import ParserShadowsocksBasic, ParserShadowsocksSIP002, ParserShadowsocksD
from .shadowsocksr_parsers import ParserShadowsocksR
from .v2ray_parsers import ParserV2RayN, ParserV2RayQuantumult
from .clash_parser import ParserClash
from .node_filters import NodeFilter

from config import config
PROXY_SETTINGS = config["proxy"]
LOCAL_ADDRESS = config["localAddress"]
LOCAL_PORT = config["localPort"]
TIMEOUT = 10

logger = logging.getLogger("Sub")

class UniversalParser:
	def __init__(self):
		self.__nodes = []
		self.__ss_base_cfg = shadowsocks_get_config(LOCAL_ADDRESS, LOCAL_PORT, TIMEOUT)

	@staticmethod
	def web_config_to_node(configs: list) -> list:
		result = []
		for config in configs:
			_type = config.get("type", "N/A")
			if _type == "Shadowsocks":
				result.append(NodeShadowsocks(config["config"]))
			elif _type == "ShadowsocksR":
				result.append(NodeShadowsocksR(config["config"]))
			elif _type == "V2Ray":
				result.append(NodeV2Ray(config["config"]))
			else:
				logger.warn(f"Unknown node type: {_type}")
		return result

	@property
	def nodes(self):
		return deepcopy(self.__nodes)

	def __get_ss_base_config(self):
		return deepcopy(self.__ss_base_cfg)

	def __clean_nodes(self):
		self.__nodes.clear()

	def set_nodes(self, nodes: list):
		self.__clean_nodes()
		self.__nodes = nodes
	
	def set_group(self, group: str):
		tmp_nodes = deepcopy(self.__nodes)
		self.__clean_nodes()
		for node in tmp_nodes:
			if group:
				node.update_config({"group": group})
			self.__nodes.append(node)
		

	def parse_links(self, links: list):
		#Single link parse
		result = []
		for link in links:
			link = link.replace("\r", "")
			node = None
			if link[:5] == "ss://":
				#Shadowsocks
				cfg = None
				try:
					pssb = ParserShadowsocksBasic(self.__get_ss_base_config())
					cfg = pssb.parse_single_link(link)
				except ValueError:
					pssip002 = ParserShadowsocksSIP002(self.__get_ss_base_config())
					cfg = pssip002.parse_single_link(link)
				if cfg:
					node = NodeShadowsocks(cfg)
				else:
					logger.warn(f"Invalid shadowsocks link {link}")

			elif link[:6] == "ssr://":
				#ShadowsocksR
				pssr = ParserShadowsocksR(self.__get_ss_base_config())
				cfg = pssr.parse_single_link(link)
				if cfg:
					node = NodeShadowsocksR(cfg)
				else:
					logger.warn(f"Invalid shadowsocksR link {link}")

			elif link[:8] == "vmess://":
				#Vmess link (V2RayN and Quan)
				#V2RayN Parser
				cfg = None
				logger.info("Try V2RayN Parser.")
				pv2rn = ParserV2RayN()
				try:
					cfg = pv2rn.parseSubsConfig(link)
				except ValueError:
					pass
				if not cfg:
					#Quantumult Parser
					logger.info("Try Quantumult Parser.")
					pq = ParserV2RayQuantumult()
					try:
						cfg = pq.parseSubsConfig(link)
					except ValueError:
						pass
				if not cfg:
					logger.error(f"Invalid vmess link: {link}")
				else:
					gen_cfg = V2RayBaseConfigs.generate_config(cfg, LOCAL_ADDRESS, LOCAL_PORT)
					node = NodeV2Ray(gen_cfg)

			else:
				logger.warn(f"Unsupport link: {link}")

			if node:
				result.append(node)

		return result

	def __parse_clash(self, clash_cfg: str) -> list:
		result = []
		pc = ParserClash(shadowsocks_get_config(LOCAL_ADDRESS, LOCAL_PORT, TIMEOUT))
		pc.parse_config(clash_cfg)
		cfgs = pc.config_list
		for cfg in cfgs:
			if cfg["type"] == "ss":
				result.append(NodeShadowsocks(cfg["config"]))
			elif cfg["type"] == "vmess":
				result.append(
					NodeV2Ray(
						V2RayBaseConfigs.generate_config(cfg["config"], LOCAL_ADDRESS, LOCAL_PORT)
					)
				)

		return result
	
	def filter_nodes(self, fk=[], fgk=[], frk=[], ek=[], egk=[], erk=[]):
		nf = NodeFilter()
		self.__nodes = nf.filter_node(self.__nodes, fk, fgk, frk, ek, egk, erk)

	def print_nodes(self):
		for item in self.nodes:
			logger.info(
				"{} - {}".format(
					item.config["group"],
					item.config["remarks"]
				)
			)
		#logger.info(f"{len(self.__nodes)} node(s) in list.")

	def read_subscription(self, urls: list):
		for url in urls:
			if not url:
				continue

			if (
				url.startswith("ss://") or
				url.startswith("ssr://") or
				url.startswith("vmess://")
			):
				self.__nodes.extend(self.parse_links([url]))
				continue

			header = {
				"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
			}
			logger.info("Reading {}".format(url))

			ClashUA = {
        		"User-Agent": "Clash"
    		}

			try:
				r = requests.get(url, headers=ClashUA, timeout=15)
				t = r.headers["subscription-userinfo"]
				dl = int(t[t.find("download") + 9:t.find("total") - 2])
				sum = dl
			except:
				sum = 0

			with open(r'test.txt', 'a+', encoding='utf-8') as test:
				test.write('{}\n'.format(url))
				test.write('{}\n'.format(sum))

			if PROXY_SETTINGS["enabled"]:
				auth = ""
				if PROXY_SETTINGS["username"]:
					auth = "{}:{}@".format(
						PROXY_SETTINGS["username"],
						PROXY_SETTINGS["password"]
					)
				proxy = "socks5://{}{}:{}".format(
					auth,
					PROXY_SETTINGS["address"],
					PROXY_SETTINGS["port"]
				)
				proxies = {
					"http": proxy,
					"https": proxy
				}
				logger.info("Reading subscription via {}".format(proxy))
				rep = requests.get(url,headers = header, timeout=15, proxies=proxies)
			else:
				rep = requests.get(url,headers = header, timeout=15)
			rep.encoding = "utf-8"
		#	rep = rep.content.decode("utf-8")
			rep = rep.text

			parsed = False
			#Try ShadowsocksD Parser
			if rep[:6] == "ssd://":
				parsed = True
				logger.info("Try ShadowsocksD Parser.")
				pssd = ParserShadowsocksD(shadowsocks_get_config(LOCAL_ADDRESS, LOCAL_PORT, TIMEOUT))
				cfgs = pssd.parseSubsConfig(b64plus.decode(rep[6:]).decode("utf-8"))
				for cfg in cfgs:
					self.__nodes.append(NodeShadowsocks(cfg))
			if parsed: continue

			#Try base64 decode
			try:
				rep = rep.strip()
				links = (b64plus.decode(rep).decode("utf-8")).split("\n")
				logger.debug("Base64 decode success.")
				self.__nodes.extend(self.parse_links(links))
				parsed = True
			except ValueError:
				logger.info("Base64 decode failed.")
			if parsed: continue

			#Try Clash Parser
			self.__nodes.extend(self.__parse_clash(rep))


	def read_gui_config(self, filename: str):
		raw_data = ""
		with open(filename, "r", encoding="utf-8") as f:
			raw_data = f.read()
		try:
			#Try Load as Json
			data = json.loads(raw_data)
			#Identification of proxy type
			#Shadowsocks(D)
			if (
				"subscriptions" in data
				or
				(
					"subscriptions" not in data
					and "serverSubscribes" not in data
					and "vmess" not in data
				)
			):
				pssb = ParserShadowsocksBasic(self.__get_ss_base_config())
				for cfg in pssb.parse_gui_data(data):
					self.__nodes.append(NodeShadowsocks(cfg))
			#ShadowsocksR
			elif "serverSubscribes" in data:
				pssr = ParserShadowsocksR(self.__get_ss_base_config())
				for cfg in pssr.parse_gui_data(data):
					self.__nodes.append(NodeShadowsocksR(cfg))
			#V2RayN
			elif "vmess" in data:
				pv2n = ParserV2RayN()
				cfgs = pv2n.parse_gui_data(data)
				for cfg in cfgs:
					self.__nodes.append(
						NodeV2Ray(
							V2RayBaseConfigs.generate_config(cfg, LOCAL_ADDRESS, LOCAL_PORT)
						)
					)
		except json.JSONDecodeError:
			#Try Load as Yaml
			self.__nodes = self.__parse_clash(raw_data)

