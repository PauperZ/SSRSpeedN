#coding:utf-8

from PIL import Image,ImageDraw,ImageFont
import json
import os
import sys
import time
import logging
import requests
logger = logging.getLogger("Sub")

from .upload_result import pushToServer
from .sorter import Sorter
from .exporters import ExporterWps

from config import config

'''
	resultJson
		{
			"group":"GroupName",
			"remarks":"Remarks",
			"loss":0,#Data loss (0-1)
			"ping":0.014,
			"gping":0.011,
			"dspeed":12435646 #Bytes
			"maxDSpeed":12435646 #Bytes
		}
'''

class ExportResult(object):
	def __init__(self):
		self.__config = config["exportResult"]
		self.__hide_max_speed = config["exportResult"]["hide_max_speed"]
		self.__hide_ntt = not config["ntt"]["enabled"]
		self.__hide_netflix = not config["netflix"]
		self.__hide_stream = not config["stream"]
		self.__hide_stspeed = not config["StSpeed"]
		self.__test_method = not config["method"]
		self.__hide_ping = not config["ping"]
		self.__hide_gping = not config["gping"]
		self.__hide_speed = not config["speed"]
		self.__hide_port = not config["port"]
		self.__hide_geoip = not config["geoip"]
		self.__hide_multiplex = not config["multiplex"]
		self.__colors = {}
		self.__colorSpeedList = []
		self.__font = ImageFont.truetype(self.__config["font"],18)
		self.__timeUsed = "N/A"
	#	self.setColors()

	def setColors(self,name = "origin"):
		for color in self.__config["colors"]:
			if (color["name"] == name):
				logger.info("Set colors as {}.".format(name))
				self.__colors = color["colors"]
				self.__colorSpeedList.append(0)
				for speed in self.__colors.keys():
					try:
						self.__colorSpeedList.append(float(speed))
					except:
						continue
				self.__colorSpeedList.sort()
				return
		logger.warn("Color {} not found in config.".format(name))

	def setTimeUsed(self, timeUsed):
		self.__timeUsed = time.strftime("%H:%M:%S", time.gmtime(timeUsed))
		logger.info("Time Used : {}".format(self.__timeUsed))

	def export(self,result,split = 0,exportType = 0,sortMethod = ""):
		if (not exportType):
			self.__exportAsJson(result)
		sorter = Sorter()
		result = sorter.sortResult(result,sortMethod)
		self.__exportAsPng(result)

	def exportWpsResult(self, result, exportType = 0):
		if not exportType:
			result = self.__exportAsJson(result)
		epwps = ExporterWps(result)
		epwps.export()

	def __getMaxWidth(self,result):
		font = self.__font
		draw = ImageDraw.Draw(Image.new("RGB",(1,1),(255,255,255)))
		maxGroupWidth = 0
		maxRemarkWidth = 0
		lenIn = 0
		lenOut = 0
		for item in result:
			group = item["group"]
			remark = item["remarks"]
			inres = item["InRes"]
			outres = item["OutRes"]
			maxGroupWidth = max(maxGroupWidth,draw.textsize(group,font=font)[0])
			maxRemarkWidth = max(maxRemarkWidth,draw.textsize(remark,font=font)[0])
			lenIn = max(lenIn, draw.textsize(inres, font=font)[0])
			lenOut = max(lenOut, draw.textsize(outres, font=font)[0])
		return (maxGroupWidth + 10,maxRemarkWidth + 10,lenIn + 20,lenOut + 20)
	
	'''
	def __deweighting(self,result):
		_result = []
		for r in result:
			isFound = False
			for i in range(0,len(_result)):
				_r = _result[i]
				if (_r["group"] == r["group"] and _r["remarks"] == r["remarks"]):
					isFound = True
					if (r["dspeed"] > _r["dspeed"]):
						_result[i] = r
					elif(r["ping"] < _r["ping"]):
						_result[i] = r
					break
			if (not isFound):
				_result.append(r)
		return _result
	'''

	def __getBasePos(self, width, text):
		font = self.__font
		draw = ImageDraw.Draw(Image.new("RGB",(1,1),(255,255,255)))
		textSize = draw.textsize(text, font=font)[0]
		basePos = (width - textSize) / 2
		logger.debug("Base Position {}".format(basePos))
		return basePos

	def __exportAsPng(self,result):
		if (self.__colorSpeedList == []):
			self.setColors()
	#	result = self.__deweighting(result)
		resultFont = self.__font
		generatedTime = time.localtime()
		imageHeight = len(result) * 30 + 30 
		weight = self.__getMaxWidth(result)
		groupWidth = weight[0]
		remarkWidth = weight[1]
		inWidth = weight[2]
		outWidth = weight[3]
		if (groupWidth < 60):
			groupWidth = 60
		if (remarkWidth < 60):
			remarkWidth = 90
		if (inWidth < 180):
			inWidth = 180
		if (outWidth < 180):
			outWidth = 180
		otherWidth = 100

		abema_logo = Image.open("./logos/abema.png")
		abema_logo.thumbnail((28,28))
		bahamut_logo = Image.open("./logos/Bahamut.png")
		bahamut_logo.thumbnail((28,28))
		disney_logo = Image.open("./logos/DisneyPlus.png")
		disney_logo.thumbnail((28,28))
		hbo_logo = Image.open("./logos/HBO.png")
		hbo_logo.thumbnail((28,28))
		netflix_logo = Image.open("./logos/Netflix.png")
		netflix_logo.thumbnail((28,28))
		tvb_logo = Image.open("./logos/tvb.png")
		tvb_logo.thumbnail((28,28))
		youtube_logo = Image.open("./logos/YouTube.png")
		youtube_logo.thumbnail((28,28))

		groupRightPosition = groupWidth
		remarkRightPosition = groupRightPosition + remarkWidth
		imageRightPosition = remarkRightPosition
        
		if not self.__hide_gping:
			imageRightPosition = remarkRightPosition + otherWidth
		lossRightPosition = imageRightPosition
        
		if not self.__hide_ping:
			imageRightPosition = lossRightPosition + otherWidth
		tcpPingRightPosition = imageRightPosition

		if not self.__hide_gping:
			imageRightPosition = tcpPingRightPosition + otherWidth + 25
		googlePingRightPosition = imageRightPosition

		if not self.__hide_port:
			imageRightPosition = googlePingRightPosition + otherWidth
		portRightPosition = imageRightPosition

		if not self.__hide_speed:
			imageRightPosition = portRightPosition + otherWidth
		dspeedRightPosition = imageRightPosition

		if not (self.__hide_max_speed or self.__hide_speed):
			imageRightPosition = dspeedRightPosition + otherWidth
		maxDSpeedRightPosition = imageRightPosition

		if not self.__hide_ntt:
			imageRightPosition = imageRightPosition + otherWidth + 80
		ntt_right_position = imageRightPosition
            
		if not self.__hide_netflix:
			imageRightPosition = imageRightPosition + otherWidth + 60
		netflix_right_position = imageRightPosition

		if not self.__hide_stream:
			imageRightPosition = imageRightPosition + otherWidth + 160
		stream_right_position = imageRightPosition

		if not self.__hide_geoip:
			imageRightPosition = imageRightPosition + inWidth
		inbound_right_position = imageRightPosition

		if not self.__hide_geoip:
			imageRightPosition = imageRightPosition + outWidth
		outbound_right_position = imageRightPosition

		if not self.__hide_multiplex:
			imageRightPosition = imageRightPosition + otherWidth + 10
		multiplex_right_position = imageRightPosition

		newImageHeight = imageHeight + 30 * 3
		resultImg = Image.new("RGB",(imageRightPosition, newImageHeight),(255,255,255))
		draw = ImageDraw.Draw(resultImg)

		
	#	draw.line((0,newImageHeight - 30 - 1,imageRightPosition,newImageHeight - 30 - 1),fill=(127,127,127),width=1)
		text = "便宜机场测速 With SSRSpeed N ( v{} )".format(config["VERSION"])
		draw.text((self.__getBasePos(imageRightPosition, text), 4),
			text,
			font=resultFont,
			fill=(0,0,0)
		)
		draw.line((0, 30, imageRightPosition - 1, 30),fill=(127,127,127),width=1)

		draw.line((1, 0, 1, newImageHeight - 1),fill=(127,127,127),width=1)
		draw.line((groupRightPosition, 30, groupRightPosition, imageHeight + 30 - 1),fill=(127,127,127),width=1)
		draw.line((remarkRightPosition, 30, remarkRightPosition, imageHeight + 30 - 1),fill=(127,127,127),width=1)

		if not self.__hide_gping:
			draw.line((lossRightPosition, 30, lossRightPosition, imageHeight + 30 - 1),fill=(127,127,127),width=1)

		if not self.__hide_ping:
			draw.line((tcpPingRightPosition, 30, tcpPingRightPosition, imageHeight + 30 - 1),fill=(127,127,127),width=1)

		if not self.__hide_gping:
			draw.line((googlePingRightPosition, 30, googlePingRightPosition, imageHeight + 30 - 1),fill=(127,127,127),width=1)

		if not self.__hide_port:
			draw.line((portRightPosition, 30, portRightPosition, imageHeight + 30 - 1),fill=(127,127,127),width=1)

		if not self.__hide_speed:
			draw.line((dspeedRightPosition, 30, dspeedRightPosition, imageHeight + 30 - 1),fill=(127,127,127),width=1)
			if not self.__hide_max_speed:
				draw.line((maxDSpeedRightPosition, 30, maxDSpeedRightPosition, imageHeight + 30 - 1),fill=(127,127,127),width=1)
        
		if not self.__hide_ntt:
			draw.line((ntt_right_position, 30, ntt_right_position, imageHeight + 30 - 1),fill=(127,127,127),width=1)    

		if not self.__hide_netflix:
			draw.line((netflix_right_position, 30, netflix_right_position, imageHeight + 30 - 1),fill=(127,127,127),width=1)

		if not self.__hide_stream:
			draw.line((stream_right_position, 30, stream_right_position, imageHeight + 30 - 1),fill=(127,127,127),width=1)

		if not self.__hide_geoip:
			draw.line((inbound_right_position, 30, inbound_right_position, imageHeight + 30 - 1),fill=(127,127,127),width=1)

		if not self.__hide_geoip:
			draw.line((outbound_right_position, 30, outbound_right_position, imageHeight + 30 - 1),fill=(127,127,127),width=1)

		if not self.__hide_multiplex:
			draw.line((multiplex_right_position, 30, multiplex_right_position, imageHeight + 30 - 1),fill=(127,127,127),width=1)
            
		draw.line((imageRightPosition, 0, imageRightPosition, newImageHeight - 1),fill=(127,127,127),width=1)
	
		draw.line((0,0,imageRightPosition - 1,0),fill=(127,127,127),width=1)

		draw.text(
			(
				self.__getBasePos(groupRightPosition, "Group"), 30 + 4
			),
			"Group", font=resultFont, fill=(0,0,0)
		
		)

		draw.text(
			(
				groupRightPosition + self.__getBasePos(remarkRightPosition - groupRightPosition, "Remarks"), 30 + 4
			),
			"Remarks", font=resultFont, fill=(0,0,0)
		
		)

		if not self.__hide_gping:
			draw.text(
				(
					remarkRightPosition + self.__getBasePos(lossRightPosition - remarkRightPosition, "Loss"), 30 + 4
				),
				"Loss", font=resultFont, fill=(0,0,0)
			)

		if not self.__hide_ping:
			draw.text(
				(
					lossRightPosition + self.__getBasePos(tcpPingRightPosition - lossRightPosition, "Ping"), 30 + 4
				),
				"Ping", font=resultFont, fill=(0,0,0)
			)

		if not self.__hide_gping:
			draw.text(
				(
					tcpPingRightPosition + self.__getBasePos(googlePingRightPosition - tcpPingRightPosition, "Google Ping"), 30 + 4
				),
				"Google Ping", font=resultFont, fill=(0,0,0)
			)

		if not self.__hide_port:
			draw.text(
				(
					googlePingRightPosition + self.__getBasePos(portRightPosition - googlePingRightPosition, "Port"), 30 + 4
				),
				"Port", font=resultFont, fill=(0, 0, 0)
			)

		if not (self.__hide_stspeed or self.__hide_speed):
			if(self.__test_method == "NETFLIX"):
				draw.text(
					(
						portRightPosition + self.__getBasePos(dspeedRightPosition - portRightPosition,"EndSpeed"),
						30 + 4
					),
					"EndSpeed", font=resultFont, fill=(0, 0, 0)
				)
			elif (self.__test_method == "YOUTUBE"):
				draw.text(
					(
						portRightPosition + self.__getBasePos(dspeedRightPosition - portRightPosition,
																	"StSpeed"),
						30 + 4
					),
					"StSpeed", font=resultFont, fill=(0, 0, 0)
				)
			else:
				draw.text(
					(
						portRightPosition + self.__getBasePos(dspeedRightPosition - portRightPosition, "单线程"), 30 + 4
					),
					"单线程", font=resultFont, fill=(0,0,0)
				)
		elif not self.__hide_speed:
			if (self.__test_method == "NETFLIX"):
				draw.text(
					(
						portRightPosition + self.__getBasePos(dspeedRightPosition - portRightPosition,
																	"EndSpeed"),
						30 + 4
					),
					"EndSpeed", font=resultFont, fill=(0, 0, 0)
				)
			elif (self.__test_method == "YOUTUBE"):
				draw.text(
					(
						portRightPosition + self.__getBasePos(dspeedRightPosition - portRightPosition,
																	"StSpeed"),
						30 + 4
					),
					"StSpeed", font=resultFont, fill=(0, 0, 0)
				)
			else:
				draw.text(
					(
						portRightPosition + self.__getBasePos(dspeedRightPosition - portRightPosition,"AvgSpeed"),
						30 + 4
					),
					"AvgSpeed", font=resultFont, fill=(0, 0, 0)
				)

		if not (self.__hide_max_speed or self.__hide_speed):
			if not self.__hide_stspeed:
				draw.text(
					(
						dspeedRightPosition + self.__getBasePos(maxDSpeedRightPosition - dspeedRightPosition, "多线程"), 30 + 4
						),
					"多线程", font=resultFont, fill=(0,0,0)
				)
			else:
				draw.text(
					(
						dspeedRightPosition + self.__getBasePos(maxDSpeedRightPosition - dspeedRightPosition, "MaxSpeed"),
						30 + 4
					),
					"MaxSpeed", font=resultFont, fill=(0, 0, 0)
				)

		if not self.__hide_ntt:
			draw.text(
				(
					maxDSpeedRightPosition + self.__getBasePos(ntt_right_position - maxDSpeedRightPosition, "UDP NAT Type"), 30 + 4
					),
				"UDP NAT Type", font=resultFont, fill=(0,0,0)
			)
            
		if not self.__hide_netflix:
			draw.text(
				(
					ntt_right_position + self.__getBasePos(netflix_right_position - ntt_right_position, "Netfilx 解锁"), 30 + 4
					),
				"Netfilx 解锁", font=resultFont, fill=(0,0,0)
			)

		if not self.__hide_stream:
			draw.text(
				(
					netflix_right_position + self.__getBasePos(stream_right_position - netflix_right_position, "流媒体解锁"), 30 + 4
					),
				"流媒体解锁", font=resultFont, fill=(0,0,0)
			)
		draw.line((0, 60, imageRightPosition - 1, 60),fill=(127,127,127),width=1)

		if not self.__hide_geoip:
			draw.text(
				(
					stream_right_position + self.__getBasePos(inbound_right_position - stream_right_position, "Inbound Geo"),
					30 + 4
				),
				"Inbound Geo", font=resultFont, fill=(0, 0, 0)
			)

		if not self.__hide_geoip:
			draw.text(
				(
					inbound_right_position + self.__getBasePos(outbound_right_position - inbound_right_position, "Outbound Geo"),
					30 + 4
				),
				"Outbound Geo", font=resultFont, fill=(0, 0, 0)
			)

		if not self.__hide_multiplex:
			draw.text(
				(
					outbound_right_position + self.__getBasePos(multiplex_right_position - outbound_right_position, "复用检测"),
					30 + 4
				),
				"复用检测", font=resultFont, fill=(0, 0, 0)
			)

		totalTraffic = 0
		onlineNode = 0
		for i in range(0,len(result)):
			totalTraffic += result[i]["trafficUsed"] if (result[i]["trafficUsed"] > 0) else 0
			if ((result[i]["ping"] > 0 and result[i]["gPing"] > 0) or (result[i]["dspeed"] > 0)):
				onlineNode += 1
			
			j = i + 1
			draw.line((0,30 * j + 60, imageRightPosition, 30 * j + 60), fill=(127,127,127), width=1)
			item = result[i]

			group = item["group"]
			draw.text((5,30 * j + 30 + 4),group,font=resultFont,fill=(0,0,0))

			remarks = item["remarks"]
			draw.text((groupRightPosition + 5,30 * j + 30 + 4),remarks,font=resultFont,fill=(0,0,0,0))

			if not self.__hide_gping:
				loss = "%.2f" % (item["gPingLoss"] * 100) + "%"
				pos = remarkRightPosition + self.__getBasePos(lossRightPosition - remarkRightPosition, loss)
				draw.text((pos, 30 * j + 30 + 4),loss,font=resultFont,fill=(0,0,0))

			if not self.__hide_ping:
				ping = "%.2f" % (item["ping"] * 1000)
				pos = lossRightPosition + self.__getBasePos(tcpPingRightPosition - lossRightPosition, ping)
				draw.text((pos, 30 * j + 30 + 4),ping,font=resultFont,fill=(0,0,0))

			if not self.__hide_gping:
				gPing = "%.2f" % (item["gPing"] * 1000)
				pos = tcpPingRightPosition + self.__getBasePos(googlePingRightPosition - tcpPingRightPosition, gPing)
				draw.text((pos, 30 * j + 30 + 4),gPing,font=resultFont,fill=(0,0,0))

			if not self.__hide_port:
				port = "%d" % (item["port"])
				pos = googlePingRightPosition + self.__getBasePos(portRightPosition - googlePingRightPosition, port)
				draw.text((pos, 30 * j + 30 + 4), port, font=resultFont, fill=(0, 0, 0))

			if not self.__hide_speed:
				speed = item["dspeed"]
				if (speed == -1):
					pos = portRightPosition + self.__getBasePos(dspeedRightPosition - portRightPosition, "N/A")
					draw.text((pos, 30 * j + 30 + 1),"N/A",font=resultFont,fill=(0,0,0))
				else:
					draw.rectangle((portRightPosition + 1,30 * j + 30 + 1,dspeedRightPosition - 1,30 * j + 60 -1),self.__getColor(speed))
					speed = self.__parseSpeed(speed)
					pos = portRightPosition + self.__getBasePos(dspeedRightPosition - portRightPosition, speed)
					draw.text((pos, 30 * j + 30 + 1), speed,font=resultFont,fill=(0,0,0))

			if not (self.__hide_max_speed or self.__hide_speed):
				maxSpeed = item["maxDSpeed"]
				if (maxSpeed == -1):
					pos = dspeedRightPosition + self.__getBasePos(maxDSpeedRightPosition - dspeedRightPosition, "N/A")
					draw.text((pos, 30 * j + 30 + 1),"N/A",font=resultFont,fill=(0,0,0))
				else:
					draw.rectangle((dspeedRightPosition + 1,30 * j + 30 + 1,maxDSpeedRightPosition - 1,30 * j + 60 -1),self.__getColor(maxSpeed))
					maxSpeed = self.__parseSpeed(maxSpeed)
					pos = dspeedRightPosition + self.__getBasePos(maxDSpeedRightPosition - dspeedRightPosition, maxSpeed)
					draw.text((pos, 30 * j + 30 + 1), maxSpeed,font=resultFont,fill=(0,0,0))

			if not self.__hide_ntt:
				nat_type = item["ntt"]["type"]
				if not nat_type:
					pos = maxDSpeedRightPosition + self.__getBasePos(ntt_right_position - maxDSpeedRightPosition, "Unknown")
					draw.text((pos, 30 * j + 30 + 1),"Unknown",font=resultFont,fill=(0,0,0))
				else:
					pos = maxDSpeedRightPosition + self.__getBasePos(ntt_right_position - maxDSpeedRightPosition, nat_type)
					draw.text((pos, 30 * j + 30 + 1), nat_type,font=resultFont,fill=(0,0,0))
		
			if not self.__hide_netflix:
				netflix_type = item["Ntype"]
				pos = ntt_right_position + self.__getBasePos(netflix_right_position - ntt_right_position, netflix_type)
				draw.text((pos, 30 * j + 30 + 1), netflix_type,font=resultFont,fill=(0,0,0))

			if not self.__hide_stream:
				netflix_type = item["Ntype"]
				hbo_type = item["Htype"]
				disney_type = item["Dtype"]
				youtube_type = item["Ytype"]
				abema_type = item["Atype"]
				bahamut_type = item["Btype"]
				tvb_type = item["Ttype"]
				if(netflix_type == "Full Native" or netflix_type == "Full DNS"):
					n_type = True
				else:
					n_type = False
				sums = n_type + hbo_type + disney_type + youtube_type + abema_type + bahamut_type + tvb_type
				pos = netflix_right_position + (stream_right_position - netflix_right_position - sums * 35) / 2
				if n_type:
					resultImg.paste(netflix_logo, (int(pos), 30 * j + 30 + 1))
					pos += 35
				if hbo_type:
					resultImg.paste(hbo_logo, (int(pos), 30 * j + 30 + 1))
					pos += 35
				if disney_type:
					resultImg.paste(disney_logo, (int(pos), 30 * j + 30 + 1))
					pos += 35
				if youtube_type:
					resultImg.paste(youtube_logo, (int(pos), 30 * j + 30 + 1))
					pos += 35
				if abema_type:
					resultImg.paste(abema_logo, (int(pos), 30 * j + 30 + 1))
					pos += 35
				if bahamut_type:
					resultImg.paste(bahamut_logo, (int(pos), 30 * j + 30 + 1))
					pos += 35
				if tvb_type:
					resultImg.paste(tvb_logo, (int(pos), 30 * j + 30 + 1))
					pos += 35

			if not self.__hide_geoip:
				inbound_geo = item["InRes"]
				pos = stream_right_position + self.__getBasePos(inbound_right_position - stream_right_position, inbound_geo)
				draw.text((pos, 30 * j + 30 + 1), inbound_geo,font=resultFont,fill=(0,0,0))

			if not self.__hide_geoip:
				outbound_geo = item["OutRes"]
				pos = inbound_right_position + self.__getBasePos(outbound_right_position - inbound_right_position, outbound_geo)
				draw.text((pos, 30 * j + 30 + 1), outbound_geo,font=resultFont,fill=(0,0,0))

			if not self.__hide_geoip:
				inbound_ip = item["InIP"]
				outbound_ip = item["OutIP"]
				if outbound_ip != "N/A":
					inbound_mul = -1
					outbound_mul = -1
					if inbound_ip == "N/A":
						inbound_mul = 0
					for ip in range(0, len(result)):
						ipitem = result[ip]
						if (ipitem["InIP"] == inbound_ip and inbound_ip != "N/A"):
							inbound_mul += 1
						if (ipitem["OutIP"] == outbound_ip):
							outbound_mul += 1
					if inbound_mul and outbound_mul:
						multiplex_res = "完全复用"
					elif (not inbound_mul) and (not outbound_mul):
						multiplex_res = "无复用"
					elif inbound_mul:
						multiplex_res = "中转复用"
					elif outbound_mul:
						multiplex_res = "落地复用"
				else:
					multiplex_res = "未知"

				pos = outbound_right_position + self.__getBasePos(multiplex_right_position - outbound_right_position, multiplex_res)
				draw.text((pos, 30 * j + 30 + 1), multiplex_res,font=resultFont,fill=(0,0,0))
                    
		files = []
		if (totalTraffic < 0):
			trafficUsed = "N/A"
		else:
			trafficUsed = self.__parseTraffic(totalTraffic)

		if not self.__hide_speed:
			t1 = "Traffic used : {}. ".format(trafficUsed)
		else:
			t1 = ""

		if not self.__hide_gping:
			t2 = " Online Node(s) : [{}/{}]".format(onlineNode,len(result))
		else:
			t2 = ""

		with open(r'test.txt', 'a+', encoding='utf-8') as test:
			test.seek(0, 0)
			url = test.readline()
			sum0 = int(test.readline())
		os.remove(r'test.txt')

		if not self.__hide_speed:
			ClashUA = {
				"User-Agent": "Clash"
			}

			try:
				r = requests.get(url, headers=ClashUA, timeout=15)
				t = r.headers["subscription-userinfo"]
				dl = int(t[t.find("download") + 9:t.find("total") - 2])
				sum = dl
			except:
				sum = 0
			Avgrate = (sum - sum0) / totalTraffic
			if (sum - sum0) > 0:
				t3 = ".  AvgRate : {:.2f}".format(Avgrate)
			else:
				t3 = ""
		else:
			t3 = ""

		draw.text((5, imageHeight + 30 + 4),
			t1 + "Time used: {}.".format(self.__timeUsed,) + t2 + t3,
			font=resultFont,
			fill=(0,0,0)
		)

	#	draw.line((0,newImageHeight - 30 * 3 - 1,imageRightPosition,newImageHeight - 30 * 3 - 1),fill=(127,127,127),width=1)
		draw.text((5,imageHeight + 30 * 2 + 4),
			"测速频道：@Cheap_Proxy   Generated at {}".format(
				time.strftime("%Y-%m-%d %H:%M:%S", generatedTime)
			),
			font=resultFont,
			fill=(0,0,0)
		)
		draw.line((0,newImageHeight - 30 - 1,imageRightPosition,newImageHeight - 30 - 1),fill=(127,127,127),width=1)
		'''
		draw.line((0,newImageHeight - 30 - 1,imageRightPosition,newImageHeight - 30 - 1),fill=(127,127,127),width=1)
		draw.text((5,imageHeight + 30 * 2 + 4),
			"By SSRSpeed {}.".format(
				config["VERSION"]
			),
			font=resultFont,
			fill=(0,0,0)
		)
		'''
		
		draw.line((0,newImageHeight - 1,imageRightPosition,newImageHeight - 1),fill=(127,127,127),width=1)
		filename = "./results/" + time.strftime("%Y-%m-%d-%H-%M-%S", generatedTime) + ".png"
		resultImg.save(filename)
		files.append(filename)
		logger.info("Result image saved as %s" % filename)
		
		for _file in files:
			if (not self.__config["uploadResult"]):
				break
			pushToServer(_file)

	def __parseTraffic(self,traffic):
		traffic = traffic / 1024 / 1024
		if (traffic < 1):
			return("%.2f KB" % (traffic * 1024))
		gbTraffic = traffic / 1024
		if (gbTraffic < 1):
			return("%.2f MB" % traffic)
		return ("%.2f GB" % gbTraffic)

	def __parseSpeed(self,speed):
		speed = speed / 1024 / 1024
		if (speed < 1):
			return("%.2fKB" % (speed * 1024))
		else:
			return("%.2fMB" % speed)

	def __newMixColor(self,lc,rc,rt):
	#	print("RGB1 : {}, RGB2 : {}, RT : {}".format(lc,rc,rt))
		return (
			int(lc[0]*(1-rt)+rc[0]*rt),
			int(lc[1]*(1-rt)+rc[1]*rt),
			int(lc[2]*(1-rt)+rc[2]*rt)
		)

	def __getColor(self,data):
		if (self.__colorSpeedList == []):
			return (255,255,255)
		rt = 1
		curSpeed = self.__colorSpeedList[len(self.__colorSpeedList)-1]
		backSpeed = 0
		if (data >= curSpeed  * 1024 * 1024):
			return (self.__colors[str(curSpeed)][0],self.__colors[str(curSpeed)][1],self.__colors[str(curSpeed)][2])
		for i in range (0,len(self.__colorSpeedList)):
			curSpeed = self.__colorSpeedList[i] * 1024 * 1024
			if (i > 0):
				backSpeed = self.__colorSpeedList[i-1]
			backSpeedStr = str(backSpeed)
		#	print("{} {}".format(data/1024/1024,backSpeed))
			if (data < curSpeed):
				rgb1 = self.__colors[backSpeedStr] if backSpeed > 0 else (255,255,255)
				rgb2 = self.__colors[str(self.__colorSpeedList[i])]
				rt = (data - backSpeed * 1024 * 1024)/(curSpeed - backSpeed * 1024 * 1024)
				logger.debug("Speed : {}, RGB1 : {}, RGB2 : {}, RT : {}".format(data/1024/1024,rgb1,rgb2,rt))
				return self.__newMixColor(rgb1,rgb2,rt)
		return (255,255,255)


	def __exportAsJson(self,result):
	#	result = self.__deweighting(result)
		filename = "./results/" + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".json"
		with open(filename,"w+",encoding="utf-8") as f:
			f.writelines(json.dumps(result,sort_keys=True,indent=4,separators=(',',':')))
		logger.info("Result exported as %s" % filename)
		return result

