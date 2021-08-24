# -*- coding: utf-8 -*-

from .node_type_base import BaseNode

class NodeShadowsocks(BaseNode):
	def __init__(self, config: dict):
		super(NodeShadowsocks, self).__init__(config)
		self._type = "Shadowsocks"
