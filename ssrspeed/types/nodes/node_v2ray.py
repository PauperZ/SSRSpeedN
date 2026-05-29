# -*- coding: utf-8 -*-

from .node_type_base import BaseNode

class NodeV2Ray(BaseNode):
	def __init__(self, config: dict):
		super(NodeV2Ray, self).__init__(config)
		self._type = "V2Ray"
