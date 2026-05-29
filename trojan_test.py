# -*- coding: utf-8 -*-

from base64 import urlsafe_b64encode, urlsafe_b64decode

from ssrspeed.config_parser import TrojanParser

if __name__ == "__main__":
	links = "trojan://66666666@helloworld.xyz:440?allowinsecure=0&tfo=1#%E4%BD%A0%E5%A5%BD\n" \
			"trojan://2457@a.helloworld.xyz:441?allowinsecure=1&tfo=0#%E4%BD%A0%E5%A5%BD\n" \
			"trojan://57678@b.helloworld.xyz:442?allowinsecure=0&tfo=1#%E4%BD%A0%E5%A5%BD\n" \
			"trojan://45375@c.helloworld.xyz:443?allowinsecure=1&tfo=0#%E4%BD%A0%E5%A5%BD\n" \

	raw = urlsafe_b64encode(links.encode("utf8"))
	tropar = TrojanParser()
	for link in urlsafe_b64decode(raw).decode("utf8").split("\n"):
		if link:
			print(tropar.parse_single_link(link))
