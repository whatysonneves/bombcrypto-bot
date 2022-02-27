import requests
import os.path
import uuid
import yaml
import urllib3
import json

# Load config file.
stream = open("./config.yaml", "r")
c = yaml.safe_load(stream)

if c["disable_requests_warnings"]:
	urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
	urllib3.disable_warnings(urllib3.exceptions.ReadTimeoutError)

def getId():
	filename = "./UUID"

	if os.path.isfile(filename):
		with open(filename) as file:
			return file.readlines()[0]

	uuid_string = str(uuid.uuid1())
	uuid_file = open(filename, "w", encoding = "UTF-8")
	uuid_file.write(uuid_string)
	uuid_file.close()

	return uuid_string

def ocr_space_file(filename, overlay = False, api_key = "helloworld", language = "eng"):
	payload = { "isOverlayRequired": overlay, "apikey": api_key, "language": language, "detectOrientation": False, "OCREngine": 2 }

	if filename is None:
		return False

	if os.path.isfile(filename):
		with open(filename, "rb") as file:
			try:
				r = requests.post("https://api.ocr.space/parse/image", files = { filename: file }, data = payload, timeout = 10 )
			except:
				print("NFTBrothers: Error occurred on ocr_space_file()")
				return False

			if r.status_code != 200:
				return False
		return r.content.decode()
	else:
		return False

def ocr(filename):
	ocr = ocr_space_file(filename, api_key = "a6c19378cb88957")
	if ocr is False:
		return 0
	ocr = json.loads(ocr)
	ocr = str(ocr["ParsedResults"][0]["ParsedText"]).strip()
	ocr = str(ocr).replace(",", ".", 1)
	ocr = str(ocr).replace(" ", "", 10)
	ocr = str(ocr).replace("B", "0", 10)
	ocr = str(ocr).replace("ø", "0", 10)
	ocr = str(ocr).replace("i", "1", 10)
	ocr = str(ocr).replace("e", "2", 10)
	ocr = str(ocr).replace("q", "4", 10)
	ocr = str(ocr).replace("a", "4", 10)
	ocr = str(ocr).replace("s", "5", 10)
	ocr = str(ocr).replace("S", "5", 10)
	ocr = str(ocr).replace("T", "7", 10)
	ocr = str(ocr).replace("g", "9", 10)
	try:
		return float(ocr)
	except:
		print("NFTBrothers: ValueError: could not convert string({}) to float".format(ocr))
		return 0

def sendLog(message, silent = 0):
	if c["send_log_to_server"]:
		try:
			req = requests.post(c["send_log_to_server_endpoint"], data = { "uuid": getId(), "message": message, "silent": silent }, verify = not c["disable_requests_warnings"])
			return req
		except:
			print("NFTBrothers: Error occurred on sendLog()")

def sendChestValue(filename, contract):
	if c["send_chest_value_to_server"]:
		value = ocr(filename)
		if value is None:
			return 0
		try:
			req = requests.post(c["send_chest_value_to_server_endpoint"], data = { "uuid": getId(), "contract": contract, "value": value }, verify = not c["disable_requests_warnings"])
			return value
		except:
			print("NFTBrothers: Error occurred on sendChestValue()")
			return 0

def checkServer():
	try:
		req = requests.get("https://api.bombcrypto.io/ccu")
		req = json.loads(req.content.decode())
	except:
		print("NFTBrothers: Error on get CCU log")
		sendLog("NFTBrothers: Error on get CCU log", 1)
		return True

	try:
		req["code"] = int(req["code"])
	except:
		print("NFTBrothers: TypeError: could not convert string({}) to int".format(req["code"]))
		req["code"] = 1

	if req["code"] > 0:
		print("Has any error on BombCrypto server")
		sendLog("Has any error on BombCrypto server", 1)
		return False
	if req["message"]["status"] == "offline":
		print("BombCrypto server is offline")
		sendLog("BombCrypto server is offline", 1)
		return False
	if req["message"]["status"] == "maintenance":
		print("BombCrypto server is under maintenance")
		sendLog("BombCrypto server is under maintenance", 1)
		return False
	if req["message"]["status"] == "online":
		print("BombCrypto server is online")
		sendLog("BombCrypto server is online", 1)
		return True
	return True
