# -*- coding: utf-8 -*-

from copy import deepcopy
import logging

logger = logging.getLogger("Sub")

class NodeFilter:
	def __init__(self):
		self.__node_list = []

	def filter_node(
		self,
		nodes: list,
		kwl:list = [],
		gkwl:list = [],
		rkwl:list = [],
		ekwl:list = [],
		egkwl:list = [],
		erkwl:list = []
	):
		self.__node_list.clear()
		self.__node_list = deepcopy(nodes)
		self.__filter_node(kwl, gkwl, rkwl)
		self.__exclude_nodes(ekwl, egkwl, erkwl)
		return self.__node_list

	def __check_in_list(self,item: dict,_list: list):
		for _item in _list:
			_item = _item.config
			server1 = item.get("server", "")
			server2 = _item.get("server", "")
			port1 = item.get("server_port", item.get("port", 0))
			port2 = _item.get("server_port", _item.get("port", 0))
			if server1 and server2 and port1 and port2:
				if server1 == server2 and port1 == port2:
					logger.warn("{} - {} ({}:{}) already in list.".format(
						item.get("group", "N/A"),
						item.get("remarks", "N/A"),
						item.get("server", "Server EMPTY"),
						item.get("server_port", item.get("port", 0))
					))
					return True
			else:
				return True
		return False

	def __filter_group(self, gkwl):
		_list = []
		if (gkwl == []):return
		for gkw in gkwl:
			for item in self.__node_list:
				config = item.config
				if self.__check_in_list(config, _list): continue
				if (gkw in config["group"]):
					_list.append(item)
		self.__node_list = _list

	def __filter_remark(self,rkwl):
		_list = []
		if (rkwl == []):return
		for rkw in rkwl:
			for item in self.__node_list:
				config = item.config
				if self.__check_in_list(config, _list): continue
				if (rkw in config["remarks"]):
					_list.append(item)
		self.__node_list = _list

	def __filter_node(self,kwl = [],gkwl = [],rkwl = []):
		_list = []
	#	print(len(self.__node_list))
	#	print(type(kwl))
		if (kwl != []):
			for kw in kwl:
				for item in self.__node_list:
					config = item.config
					if self.__check_in_list(config, _list): continue
					if ((kw in config["group"]) or (kw in config["remarks"])):
					#	print(item["remarks"])
						_list.append(item)
			self.__node_list = _list
		self.__filter_group(gkwl)
		self.__filter_remark(rkwl)

	def __exclude_group(self,gkwl):
		if (gkwl == []):return
		for gkw in gkwl:
			_list = []
			for item in self.__node_list:
				config = item.config
				if self.__check_in_list(config, _list): continue
				if (gkw not in config["group"]):
					_list.append(item)
			self.__node_list = _list

	def __exclude_remark(self,rkwl):
		if (rkwl == []):return
		for rkw in rkwl:
			_list = []
			for item in self.__node_list:
				config = item.config
				if self.__check_in_list(config, _list): continue
				if (rkw not in config["remarks"]):
					_list.append(item)
			self.__node_list = _list

	def __exclude_nodes(self,kwl = [],gkwl = [],rkwl = []):

		if (kwl != []):
			for kw in kwl:
				_list = []
				for item in self.__node_list:
					config = item.config
					if self.__check_in_list(config, _list): continue
					if ((kw not in config["group"]) and (kw not in config["remarks"])):
						_list.append(item)
					else:
						logger.debug("Excluded {} - {}".format(config["group"], config["remarks"]))
				self.__node_list = _list
		self.__exclude_group(gkwl)
		self.__exclude_remark(rkwl)

