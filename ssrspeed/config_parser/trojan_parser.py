# -*- coding: utf-8 -*-

from urllib.parse import quote, unquote
from base64 import urlsafe_b64decode, urlsafe_b64encode
import re
import logging
logger = logging.getLogger("Sub")


from . import BaseParser


class TrojanParser(BaseParser):
	def __init__(self):
		super(TrojanParser, self).__init__()

	# From: https://github.com/NyanChanMeow/SSRSpeed/issues/105
	def _parseLink(self, link :str):
		if not link.startswith("trojan://"):
			logger.error("Unsupport link: {}".format(link))
			return None

		def percent_decode(s):
			try:
				s = unquote(s, encoding="gb2312", errors="strict")
			except:
				try:
					s = unquote(s, encoding="utf8", errors="strict")
				except:
					# error decoding
					# raise # warning is enough
					pass
			return s

		link = link[len("trojan://"):]
		if not link: return None

		result = {
			"password": [],
			"remote_addr": "",
			"remote_port": 443,
			"ssl": {
				"verify": False
			},
			"tcp": {
				"fast_open": False
			},
			"remark": "N/A"
		}
		if "#" in link:
			link, result["remark"] = link.split("#")
		result["remark"] = re.sub(r"\s|\n", "", percent_decode(result["remark"]))

		password = ""
		if "@" in link:
			password, link = link.split("@")
		password = percent_decode(password)
		result["password"].append(password)

		result["remote_addr"], result["remote_port"] = link.split(":")
		result["remote_port"] = int(re.match(r"^\d+", result["remote_port"]).group(0))

		if "?" in link:
			result["ssl"]["verify"] = link[link.index("?") + len("?allowinsecure=")] == "1"

		if "&" in link:
			result["tcp"]["fast_open"] = link[link.index("&") + len("&tfo=")] == "1"

		return result
