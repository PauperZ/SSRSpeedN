#coding:utf-8

import base64

def fillb64(data):
	if len(data) % 4:
		data += "=" * (4 - (len(data) % 4))
	return data

def _url_safe_decode(s: str):
	s = fillb64(s)
	s = s.replace("-", "+").replace("_", "/")
	return base64.b64decode(s, validate=True)

def encode(s):
	s = s.encode("utf-8")
	return base64.urlsafe_b64encode(s)

def decode(s):
	return _url_safe_decode(s)
