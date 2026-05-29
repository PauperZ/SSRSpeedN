#coding:utf-8

import json
import urllib.parse
from flask import request

from .parseqsplus import parse_qs_plus

def getPostData():
	#print(request.content_type)
	data = {}
	if (request.content_type.startswith('application/json')):
		data = request.get_data()
		return json.loads(data.decode("utf-8"))
	elif(request.content_type.startswith("application/x-www-form-urlencoded")):
		#print(1)
		#print(urllib.parse.parse_qs(request.get_data().decode("utf-8")))
		return parse_qs_plus(urllib.parse.parse_qs(request.get_data().decode("utf-8")))
	else:
		for key, value in request.form.items():
			if key.endswith('[]'):
				data[key[:-2]] = request.form.getlist(key)
			else:
				data[key] = value
		return data
