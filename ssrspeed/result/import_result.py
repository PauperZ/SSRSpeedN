#coding:utf-8

import json

def importResult(filename):
	fi = None
	with open(filename,"r",encoding="utf-8") as f:
		fi = json.loads(f.read())
	return fi

