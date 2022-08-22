# -*- coding: utf-8 -*-

from .node_type_base import BaseNode

class NodeTrojan(BaseNode):
	def __init__(self, config: dict):
		super(NodeTrojan, self).__init__(config)
		self._type = "Trojan"
