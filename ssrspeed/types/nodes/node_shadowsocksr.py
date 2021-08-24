# -*- coding: utf-8 -*-

from .node_type_base import BaseNode

class NodeShadowsocksR(BaseNode):
	def __init__(self, config: dict):
		super(NodeShadowsocksR, self).__init__(config)
		self._type = "ShadowsocksR"
