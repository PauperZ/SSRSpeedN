#coding:utf-8

import logging
import copy
import socket
import socks
import time
import json
import pynat
import requests
import concurrent.futures
from bs4 import BeautifulSoup

logger = logging.getLogger("Sub")

from .test_methods import SpeedTestMethods
from ..client_launcher import ShadowsocksClient, ShadowsocksRClient, V2RayClient,TrojanClient
from ..utils.geo_ip import domain2ip, parseLocation, IPLoc
from ..utils.port_checker import check_port

from config import config

LOCAL_ADDRESS = config["localAddress"]
LOCAL_PORT = config["localPort"]
PING_TEST = config["ping"]
GOOGLE_PING_TEST = config["gping"]
NETFLIX_TEST = config["netflix"]
HBO_TEST = config["hbo"]
DISNEY_TEST = config["disney"]
YOUTUBE_TEST = config["youtube"]
TVB_TEST = config["tvb"]
ABEMA_TEST = config["abema"]
BAHAMUT_TEST = config["bahamut"]
BILIBILI_TEST = config["bilibili"]
CHATGPT_TEST = config["chatgpt"]
ntype = "None"
htype = False
dtype = False
ytype = False
ttype = False
atype = False
btype = False
ctype = False
bltype = "N/A"
inboundGeoRES = ""
outboundGeoRES = ""
inboundGeoIP = ""
outboundGeoIP = ""

class SpeedTest(object):
	def __init__(self, parser, method = "SOCKET", use_ssr_cs = False):
		self.__configs = parser.nodes
		self.__use_ssr_cs = use_ssr_cs
		self.__testMethod = method
		self.__results = []
		self.__current = {}
		self.__baseResult = {
			"group": "N/A",
			"remarks": "N/A",
			"loss": 1,
			"ping": 0,
			"gPingLoss": 1,
			"gPing": 0,
			"dspeed": -1,
			"maxDSpeed": -1,
			"trafficUsed": 0,
			"geoIP":{
				"inbound":{
					"address": "N/A",
					"info": "N/A"
				},
				"outbound":{
					"address": "N/A",
					"info": "N/A"
				}
			},
			"rawSocketSpeed": [],
			"rawTcpPingStatus": [],
			"rawGooglePingStatus": [],
			"webPageSimulation":{
				"results":[]
			},
			"ntt": {
				"type": "",
				"internal_ip": "",
				"internal_port": 0,
				"public_ip": "",
				"public_port": 0
			},
            "Ntype": "None",
			"Htype": False,
			"Dtype": False,
			"Ytype": False,
			"Ttype": False,
			"Atype": False,
			"Btype": False,
			"Ctype": False,
			"Bltype":"N/A",
			"InRes":"N/A",
			"OutRes":"N/A",
			"InIP":"N/A",
			"OutIP":"N/A",
			"port": 0,
		}

	def __getBaseResult(self):
		return copy.deepcopy(self.__baseResult)

	def __get_next_config(self):
		try:
			return self.__configs.pop(0)
		except IndexError:
			return None
	
	def __get_client(self, client_type: str):
		if client_type == "Shadowsocks":
			return ShadowsocksClient()
		elif client_type == "ShadowsocksR":
			client = ShadowsocksRClient()
			if self.__use_ssr_cs:
				client.useSsrCSharp = True
			return client
		elif client_type == "V2Ray":
			return V2RayClient()
		elif client_type == "Trojan":
			return TrojanClient()
		else:
			return None

	def resetStatus(self):
		self.__results = []
		self.__current = {}

	def getResult(self):
		return self.__results
	
	def getCurrent(self):
		return self.__current

	def getResponse(self, url):
		response = 0
		try:
			if type(url) == type(""):
				headers = {
					"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36"}
				response = requests.get(url, proxies={
					"http": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
					"https": "socks5h://127.0.0.1:%d" % LOCAL_PORT
				}, headers=headers, timeout=8)
			else:
				headers = {
					"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"}
				response = requests.get(url[0], proxies={
					"http": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
					"https": "socks5h://127.0.0.1:%d" % LOCAL_PORT
				}, headers=headers, timeout=8, cookies=url[1])

		except Exception as e:
			logger.error('代理服务器连接异常：' + str(e.args))

		return response

	def __geoIPInbound(self,config):
		inboundIP = domain2ip(config["server"])
		global inboundGeoIP
		inboundGeoIP = inboundIP
		inboundInfo = IPLoc(inboundIP)
		inboundGeo = "{} {}, {}".format(
			inboundInfo.get("country","N/A"),
			inboundInfo.get("city","Unknown City"),
			inboundInfo.get("organization","N/A")
		)
		global inboundGeoRES
		inboundGeoRES = "{}, {}".format(
			inboundInfo.get("city","Unknown City"),
			inboundInfo.get("organization", "N/A")
		)
		logger.info(
			"Node inbound IP : {}, Geo : {}".format(
				inboundIP,
				inboundGeo
			)
		)
		return (inboundIP,inboundGeo,inboundInfo.get("country_code", "N/A"))

	def __geoIPOutbound(self):
		outboundInfo = IPLoc()
		outboundIP = outboundInfo.get("ip","N/A")
		global outboundGeoIP
		outboundGeoIP = outboundIP
		outboundGeo = "{} {}, {}".format(
			outboundInfo.get("country","N/A"),
			outboundInfo.get("city","Unknown City"),
			outboundInfo.get("organization","N/A")
		)
		global outboundGeoRES
		outboundGeoRES = "{}, {}".format(
			outboundInfo.get("country_code", "N/A"),
			outboundInfo.get("organization", "N/A")
		)
		logger.info(
			"Node outbound IP : {}, Geo : {}".format(
				outboundIP,
				outboundGeo
			)
		)

		urls = []
		global ntype
		global htype
		global dtype
		global ytype
		global ttype
		global atype
		global btype
		global ctype
		global bltype

		ntype = "None"
		htype = False
		dtype = False
		ytype = False
		ttype = False
		atype = False
		btype = False
		ctype = False
		bltype = "N/A"

		if NETFLIX_TEST and outboundIP != "N/A":
			urls.append("https://www.netflix.com/title/70242311")
			urls.append("https://www.netflix.com/title/70143836")

		if HBO_TEST and outboundIP != "N/A":
			urls.append("https://www.hbomax.com/")

		if DISNEY_TEST and outboundIP != "N/A":
			urls.append("https://www.disneyplus.com/")
			urls.append("https://global.edge.bamgrid.com/token")

		if YOUTUBE_TEST and outboundIP != "N/A":
			urls.append("https://music.youtube.com/")

		if TVB_TEST and outboundIP != "N/A":
			urls.append("https://www.mytvsuper.com/api/auth/getSession/self/")

		if ABEMA_TEST and outboundIP != "N/A":
			urls.append("https://api.abema.io/v1/ip/check?device=android")

		if BAHAMUT_TEST and outboundIP != "N/A":
			BAHAMUT_CODE = 1
			try:
				headers = {
					"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"}
				r = requests.get("https://ani.gamer.com.tw/ajax/getdeviceid.php", proxies={
					"http": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
					"https": "socks5h://127.0.0.1:%d" % LOCAL_PORT
				}, headers=headers, timeout=8)

				deviceID = json.loads(r.text)['deviceid']
				logger.info("BAHAMUT device id: {}".format(deviceID))
				urls.append(("https://ani.gamer.com.tw/ajax/token.php?adID=89422&sn=14667&device={}".format(deviceID), r.cookies))
			except Exception as e:
				#logger.error(str(e.args))
				BAHAMUT_CODE = 0

		if CHATGPT_TEST and outboundIP != "N/A":
			urls.append("https://chat.openai.com/backend-api/accounts/check")
			urls.append("https://chat.openai.com/cdn-cgi/trace")
		
		if BILIBILI_TEST and outboundIP != "N/A":
			urls.append("https://api.bilibili.com/pgc/player/web/playurl?avid=18281381&cid=29892777&qn=0&type=&otype=json&ep_id=183799&fourk=1&fnver=0&fnval=16")
			urls.append("https://api.bilibili.com/pgc/player/web/playurl?avid=50762638&cid=100279344&qn=0&type=&otype=json&ep_id=268176&fourk=1&fnver=0&fnval=16")

		with concurrent.futures.ThreadPoolExecutor() as executor:
			results = executor.map(self.getResponse, urls)

		results = list(results)

		if NETFLIX_TEST and outboundIP != "N/A":
			logger.info("Performing netflix test LOCAL_PORT: {:d}.".format(LOCAL_PORT))
			try:
				sum = 0
				r1 = results.pop(0)
				r2 = results.pop(0)
				if r1 != 0 and r2 != 0:
					if (r1.status_code == 200):
						sum += 1
						soup = BeautifulSoup(r1.text, "html.parser")
						netflix_ip_str = str(soup.find_all("script"))
						p1 = netflix_ip_str.find("requestIpAddress")
						netflix_ip_r = netflix_ip_str[p1 + 19:p1 + 60]
						p2 = netflix_ip_r.find(",")
						netflix_ip = netflix_ip_r[0:p2]
						logger.info("Netflix IP : " + netflix_ip)

					rg = ""
					if (r2.status_code == 200):
						sum += 1
						rg = r2.url.split("com/")[1].split("/")[0]
						if rg != "title":
							rg = str.upper(rg[:2])
							rg = "(" + rg + ")"
						else:
							rg = ""
					# 测试连接状态

					if (sum == 0):
						logger.info("Netflix test result: None.")
						ntype = "None"
					elif (sum == 1):
						logger.info("Netflix test result: Only Original.")
						ntype = "Only Original"
					elif (outboundIP == netflix_ip):
						logger.info("Netflix test result: Full Native.")
						ntype = "Full Native" + rg
					else:
						logger.info("Netflix test result: Full DNS.")
						ntype = "Full DNS" + rg
				else:
					ntype = "Unknown"

			except Exception as e:
				logger.error('代理服务器连接异常：' + str(e.args))

		if HBO_TEST and outboundIP != "N/A":
			logger.info("Performing HBO max test LOCAL_PORT: {:d}.".format(LOCAL_PORT))
			try:
				r = results.pop(0)
				if r != 0:
					if (r.status_code == 200):
						htype = True
					else:
						htype = False
				else:
					htype = False

			except Exception as e:
				logger.error('代理服务器连接异常：' + str(e.args))

		if DISNEY_TEST and outboundIP != "N/A":
			logger.info("Performing Disney plus test LOCAL_PORT: {:d}.".format(LOCAL_PORT))
			try:
				r1 = results.pop(0)
				r2 = results.pop(0)
				if r1 != 0 and r2 != 0:
					if (r1.status_code == 200 and r2.status_code != 403):
						dtype = True
					else:
						dtype = False
				else:
					dtype = False

			except Exception as e:
				logger.error('代理服务器连接异常：' + str(e.args))

		if YOUTUBE_TEST and outboundIP != "N/A":
			logger.info("Performing Youtube Premium test LOCAL_PORT: {:d}.".format(LOCAL_PORT))
			try:
				r = results.pop(0)

				if r != 0:
					if ("is not available" in r.text):
						ytype = False
					elif (r.status_code == 200):
						ytype = True
					else:
						ytype = False
				else:
					ytype = False

			except Exception as e:
				logger.error('代理服务器连接异常：' + str(e.args))

		if TVB_TEST and outboundIP != "N/A":
			logger.info("Performing TVB test LOCAL_PORT: {:d}.".format(LOCAL_PORT))
			try:
				r = results.pop(0)
				if r != 0:
					tvb_region = json.loads(r.text)['region']
					if (tvb_region == 1):
						ttype = True
					else:
						ttype = False
				else:
					ttype = False

			except Exception as e:
				logger.error('代理服务器连接异常：' + str(e.args))

		if ABEMA_TEST and outboundIP != "N/A":
			logger.info("Performing Abema test LOCAL_PORT: {:d}.".format(LOCAL_PORT))
			try:
				r = results.pop(0)
				if r != 0:
					if (r.text.count("Country") > 0):
						atype = True
					else:
						atype = False
				else:
					atype = False

			except Exception as e:
				logger.error('代理服务器连接异常：' + str(e.args))

		if BAHAMUT_TEST and outboundIP != "N/A" and BAHAMUT_CODE:
			logger.info("Performing Bahamut test LOCAL_PORT: {:d}.".format(LOCAL_PORT))
			try:
				r = results.pop(0)
				if r != 0:
					if (r.text.count("animeSn") > 0):
						btype = True
					else:
						btype = False
				else:
					btype = False

			except Exception as e:
				logger.error('代理服务器连接异常：' + str(e.args))

		if CHATGPT_TEST and outboundIP != "N/A":
			logger.info("Performing ChatGPT test LOCAL_PORT: {:d}.".format(LOCAL_PORT))
			CHATGPT_REGION_LIST = ['T1', 'XX', 'AL', 'DZ', 'AD', 'AO', 'AG', 'AR', 'AM', 'AU', 'AT', 'AZ', 'BS', 'BD', 'BB', 'BE', 'BZ', 'BJ', 'BT', 'BA', 'BW', 'BR',
								   'BG', 'BF', 'CV', 'CA', 'CL', 'CO', 'KM', 'CR', 'HR', 'CY', 'DK', 'DJ', 'DM', 'DO', 'EC', 'SV', 'EE', 'FJ', 'FI', 'FR', 'GA', 'GM',
								   'GE', 'DE', 'GH', 'GR', 'GD', 'GT', 'GN', 'GW', 'GY', 'HT', 'HN', 'HU', 'IS', 'IN', 'ID', 'IQ', 'IE', 'IL', 'IT', 'JM', 'JP', 'JO',
								   'KZ', 'KE', 'KI', 'KW', 'KG', 'LV', 'LB', 'LS', 'LR', 'LI', 'LT', 'LU', 'MG', 'MW', 'MY', 'MV', 'ML', 'MT', 'MH', 'MR', 'MU', 'MX',
								   'MC', 'MN', 'ME', 'MA', 'MZ', 'MM', 'NA', 'NR', 'NP', 'NL', 'NZ', 'NI', 'NE', 'NG', 'MK', 'NO', 'OM', 'PK', 'PW', 'PA', 'PG', 'PE',
								   'PH', 'PL', 'PT', 'QA', 'RO', 'RW', 'KN', 'LC', 'VC', 'WS', 'SM', 'ST', 'SN', 'RS', 'SC', 'SL', 'SG', 'SK', 'SI', 'SB', 'ZA', 'ES',
								   'LK', 'SR', 'SE', 'CH', 'TH', 'TG', 'TO', 'TT', 'TN', 'TR', 'TV', 'UG', 'AE', 'US', 'UY', 'VU', 'ZM', 'BO', 'BN', 'CG', 'CZ', 'VA',
								   'FM', 'MD', 'PS', 'KR', 'TW', 'TZ', 'TL', 'GB']
			try:
				r1 = results.pop(0)
				r2 = results.pop(0)
				if r1 != 0 and r2 != 0:
					r2text = r2.text
					r2index = r2text.find('loc=')
					country_code = r2text[r2index + 4: r2index + 6]
					if r1.text.count('Error reference number: 1020') == 0 and country_code in CHATGPT_REGION_LIST:
						ctype = True
					else:
						ctype = False
				else:
					ctype = False

			except Exception as e:
				logger.error('代理服务器连接异常：' + str(e.args))

		if BILIBILI_TEST and outboundIP != "N/A":
			logger.info("Performing Bilibili test LOCAL_PORT: {:d}.".format(LOCAL_PORT))
			try:
				r1 = results.pop(0)
				r2 = results.pop(0)
				sumb = 0
				if r1 != 0 and r2 != 0:
					if r1.text.count('抱歉您所在地区不可观看') == 0:
						bltype = "仅限港澳台"
						sumb += 1
					if r2.text.count('抱歉您所在地区不可观看') == 0:
						bltype = "仅限台湾"
						sumb += 1
					if sumb == 0:
						bltype = "N/A"
					if sumb == 2:
						bltype = "全解锁"
				else:
					bltype = "N/A"

			except Exception as e:
				logger.error('代理服务器连接异常：' + str(e.args))

		return (outboundIP, outboundGeo, outboundInfo.get("country_code", "N/A"))


	def __tcpPing(self, server, port):
		res = {
			"loss": self.__baseResult["loss"],
			"ping": self.__baseResult["ping"],
			"rawTcpPingStatus": self.__baseResult["rawTcpPingStatus"],
			"gPing": self.__baseResult["gPing"],
			"gPingLoss": self.__baseResult["gPingLoss"],
			"rawGooglePingStatus": self.__baseResult["rawGooglePingStatus"]
		}

		if PING_TEST:
			st = SpeedTestMethods()
			latencyTest = st.tcpPing(server, port)
			res["loss"] = 1 - latencyTest[1]
			res["ping"] = latencyTest[0]
			res["rawTcpPingStatus"] = latencyTest[2]
			logger.debug(latencyTest)
			time.sleep(1)

		if ((not PING_TEST) or (latencyTest[0] > 0)):
			if GOOGLE_PING_TEST:
				try:
					st = SpeedTestMethods()
					googlePingTest = st.googlePing()
					res["gPing"] = googlePingTest[0]
					res["gPingLoss"] = 1 - googlePingTest[1]
					res["rawGooglePingStatus"] = googlePingTest[2]
				except:
					logger.exception("")
					pass
		return res

	def __nat_type_test(self):

		s = socks.socksocket(socket.AF_INET, socket.SOCK_DGRAM)
		s.set_proxy(socks.PROXY_TYPE_SOCKS5, LOCAL_ADDRESS, LOCAL_PORT)
		sport = config["ntt"]["internal_port"]
		try:
			logger.info("Performing UDP NAT Type Test")
			t, eip, eport, sip = pynat.get_ip_info(
				source_ip=config["ntt"]["internal_ip"],
				source_port=sport,
				include_internal=True,
				sock=s
			)
			return t, eip, eport, sip, sport
		except:
			logger.exception("\n")
			return None, None, None, None, None
		finally:
			s.close()

	
	def __start_test(self, test_mode = "FULL"):
		self.__results = []
		total_nodes = len(self.__configs)
		done_nodes = 0
		node = self.__get_next_config()
		while node:
			done_nodes += 1
			try:
				cfg = node.config
				logger.info(
					"Starting test {group} - {remarks} [{cur}/{tol}]".format(
						group = cfg["group"],
						remarks = cfg["remarks"],
						cur = done_nodes,
						tol = total_nodes
					)
				)
				client = self.__get_client(node.node_type)
				if not client:
					logger.warning(f"Unknown Node Type: {node.node_type}")
					node = self.__get_next_config()
					continue
				_item = self.__getBaseResult()
				_item["group"] = cfg["group"]
				_item["remarks"] = cfg["remarks"]
				self.__current = _item
				cfg["server_port"] = int(cfg["server_port"])
				_item["port"] = cfg["server_port"]
				client.startClient(cfg)

				# Check client started
				time.sleep(1)
				ct = 0
				client_started = True
				while not client.check_alive():
					ct += 1
					if ct > 3:
						client_started = False
						break
					client.startClient(cfg)
					time.sleep(1)
				if not client_started:
					logger.error("Failed to start client.")
					continue
				logger.info("Client started.")

				# Check port
				ct = 0
				port_opened = True
				while True:
					if ct >= 3:
						port_opened = False
						break
					time.sleep(1)
					try:
						check_port(LOCAL_PORT)
						break
					except socket.timeout:
						ct += 1
						logger.error("Port {} timeout.".format(LOCAL_PORT))
					except ConnectionRefusedError:
						ct += 1
						logger.error("Connection refused on port {}.".format(LOCAL_PORT))
					except:
						ct += 1
						logger.exception("An error occurred:\n")
				if not port_opened:
					logger.error("Port {} closed.".format(LOCAL_PORT))
					continue

				inboundInfo = self.__geoIPInbound(cfg)
				_item["geoIP"]["inbound"]["address"] = inboundInfo[0]
				_item["geoIP"]["inbound"]["info"] = inboundInfo[1]
				pingResult = self.__tcpPing(cfg["server"], cfg["server_port"])
				if (isinstance(pingResult, dict)):
					for k in pingResult.keys():
						_item[k] = pingResult[k]
				outboundInfo = self.__geoIPOutbound()
				_item["geoIP"]["outbound"]["address"] = outboundInfo[0]
				_item["geoIP"]["outbound"]["info"] = outboundInfo[1]

				if ((not GOOGLE_PING_TEST) or _item["gPing"] > 0 or outboundInfo[2] == "CN"):
					st = SpeedTestMethods()
					if test_mode == "WPS":
						res = st.startWpsTest()
						_item["webPageSimulation"]["results"] = res
						logger.info("[{}] - [{}] - Loss: [{:.2f}%] - TCP Ping: [{:.2f}] - Google Loss: [{:.2f}%] - Google Ping: [{:.2f}] - [WebPageSimulation]".format
							(
								_item["group"],
								_item["remarks"],
								_item["loss"] * 100,
								int(_item["ping"] * 1000),
								_item["gPingLoss"] * 100,
								int(_item["gPing"] * 1000)
							)
						)
					elif test_mode == "PING":
						nat_info = ""
						if config["ntt"]["enabled"]:
							t, eip, eport, sip, sport = self.__nat_type_test()
							_item["ntt"]["type"] = t
							_item["ntt"]["internal_ip"] = sip
							_item["ntt"]["internal_port"] = sport
							_item["ntt"]["public_ip"] = eip
							_item["ntt"]["public_port"] = eport

							if t:
								nat_info += " - NAT Type: " + t
								if t != pynat.BLOCKED:
									nat_info += " - Internal End: {}:{}".format(sip, sport)
									nat_info += " - Public End: {}:{}".format(eip, eport)

						logger.info("[{}] - [{}] - Loss: [{:.2f}%] - TCP Ping: [{:.2f}] - Google Loss: [{:.2f}%] - Google Ping: [{:.2f}]{}".format
							(
								_item["group"],
								_item["remarks"],
								_item["loss"] * 100,
								int(_item["ping"] * 1000),
								_item["gPingLoss"] * 100,
								int(_item["gPing"] * 1000),
								nat_info
							)
						)

					elif test_mode == "FULL":
						nat_info = ""
						if config["ntt"]["enabled"]:
							t, eip, eport, sip, sport = self.__nat_type_test()
							_item["ntt"]["type"] = t
							_item["ntt"]["internal_ip"] = sip
							_item["ntt"]["internal_port"] = sport
							_item["ntt"]["public_ip"] = eip
							_item["ntt"]["public_port"] = eport

							if t:
								nat_info += " - NAT Type: " + t
								if t != pynat.BLOCKED:
									nat_info += " - Internal End: {}:{}".format(sip, sport)
									nat_info += " - Public End: {}:{}".format(eip, eport)

						testRes = st.startTest(self.__testMethod)
						if (int(testRes[0]) == 0):
							logger.warning("Re-testing node.")
							testRes = st.startTest(self.__testMethod)
						global ntype
						global htype
						global dtype
						global ytype
						global ttype
						global atype
						global btype
						global ctype
						global bltype
						global inboundGeoRES
						global outboundGeoRES
						global inboundGeoIP
						global outboundGeoIP
						_item["dspeed"] = testRes[0]
						_item["maxDSpeed"] = testRes[1]
						_item["Ntype"] = ntype
						_item["Htype"] = htype
						_item["Dtype"] = dtype
						_item["Ytype"] = ytype
						_item["Ttype"] = ttype
						_item["Atype"] = atype
						_item["Btype"] = btype
						_item["Ctype"] = ctype
						_item["Bltype"] = bltype
						_item["InRes"] = inboundGeoRES
						_item["OutRes"] = outboundGeoRES
						_item["InIP"] = inboundGeoIP
						_item["OutIP"] = outboundGeoIP
						try:
							_item["trafficUsed"] = testRes[3]
							_item["rawSocketSpeed"] = testRes[2]
						except:
							pass

						logger.info("[{}] - [{}] - Loss: [{:.2f}%] - TCP Ping: [{:.2f}] - Google Loss: [{:.2f}%] - Google Ping: [{:.2f}] - AvgStSpeed: [{:.2f}MB/s] - AvgMtSpeed: [{:.2f}MB/s]{}".format
							(
								_item["group"],
								_item["remarks"],
								_item["loss"] * 100,
								int(_item["ping"] * 1000),
								_item["gPingLoss"] * 100,
								int(_item["gPing"] * 1000),
								_item["dspeed"] / 1024 / 1024,
								_item["maxDSpeed"] / 1024 / 1024,
								nat_info
							)
						)
					else:
						logger.error(f"Unknown Test Mode {test_mode}")
			except Exception:
				logger.exception("\n")
			finally:
				self.__results.append(_item)
				if client:
					client.stopClient()
				node = self.__get_next_config()
				time.sleep(1)

		self.__current = {}

	def webPageSimulation(self):
		logger.info("Test mode : Web Page Simulation")
		self.__start_test("WPS")

	def tcpingOnly(self):
		logger.info("Test mode : tcp ping only.")
		self.__start_test("PING")

	def fullTest(self):
		logger.info("Test mode : speed and tcp ping.Test method : {}.".format(self.__testMethod))
		self.__start_test("FULL")

