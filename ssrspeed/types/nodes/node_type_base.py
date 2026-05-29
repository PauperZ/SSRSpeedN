# -*- coding: utf-8 -*-

from copy import deepcopy

class BaseNode:
	def __init__(self, config: dict):
		self._type = ""
		if not isinstance(config, dict):
			raise TypeError("The 'config' parameter must be dict")
		self._config = config

	def __repr__(self):
		return f"<{self.__class__.__name__}>, Proxy Type: {self.node_type}"

	@property
	def node_type(self) -> str:
		if not self._type:
			raise NotImplementedError
		return self._type

	@property
	def config(self) -> dict:
		return deepcopy(self._config)

	def update_config(self, new_cfg: dict):
		if new_cfg:
			self._config.update(new_cfg)

	def __eq__(self, other):
		return (
			self._config["server"] == other.config["server"] and
			self._config["server_port"] == other.config["server_port"]
		)
		
