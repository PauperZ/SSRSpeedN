#coding:utf-8

import os
import shutil
import json

__version__ = "2.7.3"
__web_api_version__ = "0.5.2"

config = {
	"VERSION": __version__,
	"WEB_API_VERSION": __web_api_version__
}

LOADED = False

if not LOADED:
	if os.path.exists("ssrspeed_config.json"):
		if os.path.isdir("ssrspeed_config.json"):
			shutil.rmtree("ssrspeed_config.json")
			if not os.path.exists("ssrspeed_config.example.json"):
				raise FileNotFoundError("Default configuraton file not found, please download from the official repo and try again.")
			shutil.copy("ssrspeed_config.example.json", "ssrspeed_config.json")
	else:
		if not os.path.exists("ssrspeed_config.example.json"):
			raise FileNotFoundError("Default configuraton file not found, please download from the official repo and try again.")
		shutil.copy("ssrspeed_config.example.json", "ssrspeed_config.json")

	with open("ssrspeed_config.json", "r", encoding = "utf-8") as f:
		try:
			file_config = json.load(f)
			config.update(file_config)
		finally:
			pass
	LOADED = True

