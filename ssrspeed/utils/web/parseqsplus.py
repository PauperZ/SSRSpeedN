#coding:utf-8

def parse_qs_plus(_dict):
	data = {}
	if(type(_dict) != dict):
		return _dict
	for k,v in _dict.items():
		if (type(v) == list):
			if (len(v) == 0):
				data[k] = []
			elif (len(v) == 1):
				data[k] = v[0]
			else:
				_list = []
				for item in v:
					_list.append(parse_qs_plus(item))
				data[k] = _list
		else:
			data[k] = v
	return data

