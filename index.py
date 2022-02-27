# -*- coding: utf-8 -*-
from src.nftbrothers import getId
from src.nftbrothers import sendChestValue
from src.nftbrothers import checkServer
from src.date import dateFormatted
from src.logger import logger, loggerMapClicked
from cv2 import cv2
from os import listdir
from random import randint
from random import random
import numpy as np
import mss
import mss.tools
import pyautogui
import time
import sys
import yaml

# disable failsafe
# pydirectinput.FAILSAFE = False
pyautogui.FAILSAFE = False

# Load config file.
stream = open("config.yaml", "r")
c = yaml.safe_load(stream)
ct = c["threshold"]
ch = c["home"]
pause = c["time_intervals"]["interval_between_moviments"]
pyautogui.PAUSE = pause

splash = """                                                                                                
 888888b.                          888       .d8888b.                            888            
 888  "88b                         888      d88P  Y88b                           888            
 888  .88P                         888      888    888                           888            
 8888888K.   .d88b.  88888b.d88b.  88888b.  888        888d888 888  888 88888b.  888888 .d88b.  
 888  "Y88b d88""88b 888 "888 "88b 888 "88b 888        888P"   888  888 888 "88b 888   d88""88b 
 888    888 888  888 888  888  888 888  888 888    888 888     888  888 888  888 888   888  888 
 888   d88P Y88..88P 888  888  888 888 d88P Y88b  d88P 888     Y88b 888 888 d88P Y88b. Y88..88P 
 8888888P"   "Y88P"  888  888  888 88888P"   "Y8888P"  888      "Y88888 88888P"   "Y888 "Y88P"  
                                                                    888 888                     
                                                               Y8b d88P 888                     
                                                                "Y88P"  888                     
                                                                                                
                      888               888          d888           d8888                       
                      888               888         d8888          d8P888                       
                      888               888           888         d8P 888                       
                      88888b.   .d88b.  888888        888        d8P  888                       
                      888 "88b d88""88b 888           888       d88   888                       
                      888  888 888  888 888           888       8888888888                      
                      888 d88P Y88..88P Y88b.         888   d8b       888                       
                      88888P"   "Y88P"   "Y888      8888888 Y8P       888  .3                   
                                                                                                

--> Press Ctrl + C to kill the bot.
--> Some configs can be found in the config.yaml file.
"""

def addRandomness(n, randomn_factor_size = None):
	if randomn_factor_size is None:
		randomness_percentage = 0.1
		randomn_factor_size = randomness_percentage * n

	random_factor = 2 * random() * randomn_factor_size

	# fator de deslize do clique
	if random_factor > 15:
		random_factor = 15
	without_average_random_factor = n - randomn_factor_size
	randomized_n = int(without_average_random_factor + random_factor)
	return int(randomized_n)

def moveToWithRandomness(x, y, t):
	pyautogui.moveTo(addRandomness(x, 10), addRandomness(y, 10), t+random()/2)

def remove_suffix(input_string, suffix):
	if suffix and input_string.endswith(suffix):
		return input_string[:-len(suffix)]
	return input_string

def load_images(dir_path = "./targets/"):
	file_names = listdir(dir_path)
	targets = {}
	for file in file_names:
		path = "./targets/" + file
		targets[remove_suffix(file, ".png")] = cv2.imread(path)
	return targets

def loadHeroesToSendHome():
	"""Loads the images in the path and saves them as a list"""
	file_names = listdir("./targets/heroes-to-send-home")
	heroes = []
	for file in file_names:
		path = "./targets/heroes-to-send-home/" + file
		heroes.append(cv2.imread(path))

	print(">>---> %d heroes that should be sent home loaded" % len(heroes))
	return heroes

def printScreen():
	with mss.mss() as sct:
		monitor = sct.monitors[0]
		sct_img = np.array(sct.grab(monitor))
		return sct_img[:,:,:3]

def show(rectangles, img = printScreen()):
	""" Show an popup with rectangles showing the rectangles[(x, y, w, h),...]
		over img or a printScreen if no img provided. Useful for debugging"""

	for (x, y, w, h) in rectangles:
		cv2.rectangle(img, (x, y), (x + w, y + h), (255,255,255,255), 2)

	cv2.imshow("img", img)
	cv2.waitKey(0)

def clickBtn(img, timeout=3, threshold = ct["default"]):
	"""Search for img in the screen, if found moves the cursor over it and clicks.
	Parameters:
		img: The image that will be used as an template to find where to click.
		timeout (int): Time in seconds that it will keep looking for the img before returning with fail
		threshold(float): How confident the bot needs to be to click the buttons (values from 0 to 1)
	"""

	start = time.time()
	has_timed_out = False
	while(not has_timed_out):
		matches = positions(img, threshold = threshold)
		# show(matches, img)

		if(len(matches)==0):
			has_timed_out = time.time()-start > timeout
			continue

		x,y,w,h = matches[0]
		pos_click_x = x+w/2
		pos_click_y = y+h/2
		moveToWithRandomness(pos_click_x,pos_click_y,1)
		pyautogui.click()
		return True

	return False

def positions(target, threshold = ct["default"], img = None):
	if img is None:
		img = printScreen()
	result = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)
	w = target.shape[1]
	h = target.shape[0]

	yloc, xloc = np.where(result >= threshold)

	rectangles = []
	for (x, y) in zip(xloc, yloc):
		rectangles.append([int(x), int(y), int(w), int(h)])
		rectangles.append([int(x), int(y), int(w), int(h)])

	rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
	return rectangles

def scroll():
	commoms = positions(images["commom-text"], threshold = ct["commom"])
	if (len(commoms) == 0):
		return
	x,y,w,h = commoms[len(commoms)-1]

	moveToWithRandomness(x,y,1)

	if not c["use_click_and_drag_instead_of_scroll"]:
		pyautogui.scroll(-c["scroll_size"])
	else:
		pyautogui.dragRel(0,-c["click_and_drag_amount"], duration = 1, button = "left")

def sendAllHeroes():
	clickBtn(images["all-work"])
	goToGame()
	logger("sending all heroes to work")

def isHome(hero, buttons):
	y = hero[1]

	for (_,button_y,_,button_h) in buttons:
		isBelow = y < (button_y + button_h)
		isAbove = y > (button_y - button_h)
		if isBelow and isAbove:
			# if send-home button exists, the hero is not home
			return False
	return True

def isWorking(bar, buttons):
	y = bar[1]

	for (_,button_y,_,button_h) in buttons:
		isBelow = y < (button_y + button_h)
		isAbove = y > (button_y - button_h)
		if isBelow and isAbove:
			return False
	return True

def clickGreenBarButtons():
	offset = 140

	green_bars = positions(images["green-bar"], threshold = ct["green_bar"])
	buttons = positions(images["go-work"], threshold = ct["go_to_work_btn"])

	not_working_green_bars = []
	for bar in green_bars:
		if not isWorking(bar, buttons):
			not_working_green_bars.append(bar)
	if len(not_working_green_bars) > 0:
		pass

	# se tiver botao com y maior que bar y-10 e menor que y+10
	hero_clicks_cnt = 0
	for (x, y, w, h) in not_working_green_bars:
		moveToWithRandomness(x+offset+(w/2),y+(h/2),1)
		pyautogui.click()
		global hero_clicks
		hero_clicks = hero_clicks + 1
		hero_clicks_cnt = hero_clicks_cnt + 1
		if hero_clicks_cnt > 20:
			logger("Too many hero clicks, try to increase the go_to_work_btn threshold")
			return
	return len(not_working_green_bars)

def clickFullBarButtons():
	offset = 100
	full_bars = positions(images["full-stamina"], threshold = ct["default"])
	buttons = positions(images["go-work"], threshold = ct["go_to_work_btn"])

	not_working_full_bars = []
	for bar in full_bars:
		if not isWorking(bar, buttons):
			not_working_full_bars.append(bar)

	if len(not_working_full_bars) > 0:
		pass

	for (x, y, w, h) in not_working_full_bars:
		moveToWithRandomness(x+offset+(w/2),y+(h/2),1)
		pyautogui.click()
		global hero_clicks
		hero_clicks = hero_clicks + 1

	return len(not_working_full_bars)

def goToHeroes():
	if clickBtn(images["go-back-arrow"]):
		global login_attempts
		login_attempts = 0

	time.sleep(1)
	clickBtn(images["hero-icon"])
	time.sleep(randint(1,3))

def goToGame():
	clickBtn(images["x"])
	clickBtn(images["x"])
	clickBtn(images["treasure-hunt-icon"])

def login():
	global login_attempts
	logger("Checking if game has disconnected")

	if login_attempts > 3:
		logger("Too many login attempts, refreshing")
		login_attempts = 0
		pyautogui.hotkey("ctrl", "shift", "r")
		return

	if clickBtn(images["connect-wallet"], timeout = 10):
		clickBtn(images["connect-metamask"], timeout = 3)
		logger("Connect wallet button detected, logging in!")
		login_attempts = login_attempts + 1

	if c["metamask"] == "pt":
		wallet_metamask = "select-wallet-2-pt"
	else:
		wallet_metamask = "select-wallet-2-en"

	if clickBtn(images[wallet_metamask], timeout = 8):
		login_attempts = login_attempts + 1
		if clickBtn(images["treasure-hunt-icon"], timeout = 15):
			login_attempts = 0
		return

	if clickBtn(images[wallet_metamask], timeout = 20):
		login_attempts = login_attempts + 1
		if clickBtn(images["treasure-hunt-icon"], timeout = 25):
			login_attempts = 0

	if clickBtn(images["ok"], timeout=5):
		pass

	goToGame()

def getChestPositions(target, threshold = 0.7, img = printScreen()):
	start = time.time()
	has_timed_out = False
	while(not has_timed_out):
		chest = positions(target, threshold, img)

		if(len(chest) == 0):
			has_timed_out = time.time()-start > c["chest_print"]["attempts"]
			continue

		x, y, w, h = chest[0]
		nx = x + w
		ny = y + 47
		return [x, y, nx, ny, w, h]

	return False

def cropAndSaveChestPrint(target, img = printScreen()):
	positions = getChestPositions(images["chest-" + target], 0.7, img)

	if positions is False:
		return login()

	with mss.mss() as sct:
		if target == "bkeys":
			if c["chest_print"]["only_number_to_ocr"]:
				monitor = {"left": int(positions[0] + positions[5] - 10), "top": int(positions[1] - 3), "width": 90, "height": 47}
			else:
				monitor = {"left": int(positions[0] - 3), "top": int(positions[1] - 3), "width": int(positions[4] + 90), "height": 47}
		else:
			if c["chest_print"]["only_number_to_ocr"]:
				monitor = {"left": int(positions[0]), "top": int(positions[1]+positions[5]), "width": int(positions[4]), "height": 47}
			else:
				monitor = {"left": int(positions[0]), "top": int(positions[1]), "width": int(positions[4]), "height": int(positions[5] + 47)}
		output = "./prints/"+dateFormatted("%Y-%m-%d-%H-%M-%S")+"-"+target+".png"
		sct_img = sct.grab(monitor)
		mss.tools.to_png(sct_img.rgb, sct_img.size, output = output)
	return output

def saveChestPrint():
	time.sleep(1)
	if not c["chest_print"]["save"]:
		return
	bkeys = cropAndSaveChestPrint("bkeys")

	clickBtn(images["chest"])
	# caso o servidor demore para carregar
	time.sleep(3)
	img = printScreen()
	bcoins = cropAndSaveChestPrint("bcoins", img)
	bheros = cropAndSaveChestPrint("bheros", img)
	if c["chest_print"]["ocr"]:
		bkeys = sendChestValue(bkeys, "bkey")
		bcoins = sendChestValue(bcoins, "bcoin")
		bheros = sendChestValue(bheros, "bhero")
	goToGame()

def refreshHeroesPositions(log = True):
	if log:
		logger("Refreshing Heroes Positions")

	clickBtn(images["go-back-arrow"])
	clickBtn(images["treasure-hunt-icon"])

	time.sleep(3)
	clickBtn(images["treasure-hunt-icon"])

def checkIfExists(target):
	check = positions(images[target])
	if(len(check) == 0):
		return False
	return True

def checkLogin():
	if checkIfExists("ok"):
		clickBtn(images["ok"])
		pyautogui.hotkey("ctrl", "shift", "r")
		time.sleep(10)

	if checkIfExists("connect-wallet"):
		if checkServer():
			login()
			return True
		stop = randint(10, 25)
		print("Bot will stop for {} minutes".format(stop))
		time.sleep(stop * 60)
		return False

def sendHeroesHome():
	if not ch["enable"]:
		return
	heroes_positions = []
	for hero in home_heroes:
		hero_positions = positions(hero, threshold = ch["hero_threshold"])
		if not len (hero_positions) == 0:
			hero_position = hero_positions[0]
			heroes_positions.append(hero_position)

	n = len(heroes_positions)
	if n == 0:
		print("No heroes that should be sent home found.")
		return
	print(" %d heroes that should be sent home found" % n)
	# if send-home button exists, the hero is not home
	go_home_buttons = positions(images["send-home"], threshold = ch["home_button_threshold"])
	# TODO pass it as an argument for both this and the other function that uses it
	go_work_buttons = positions(images["go-work"], threshold = ct["go_to_work_btn"])

	for position in heroes_positions:
		if not isHome(position,go_home_buttons):
			print(isWorking(position, go_work_buttons))
			if(not isWorking(position, go_work_buttons)):
				print ("hero not working, sending him home")
				moveToWithRandomness(go_home_buttons[0][0]+go_home_buttons[0][2]/2,position[1]+position[3]/2,1)
				pyautogui.click()
			else:
				print ("hero working, not sending him home(no dark work button)")
		else:
			print("hero already home, or home full(no dark home button)")

def refreshHeroes(select_heroes_mode = c["select_heroes_mode"]):
	global hero_clicks
	if checkIfExists("go-back-arrow") is False:
		logger("Go back arrow not found")
		checkLogin()
		goToGame()

	goToHeroes()

	if select_heroes_mode == "all": return sendAllHeroes()

	buttonsClicked = 1
	empty_scrolls_attempts = c["scroll_attemps"]

	while(empty_scrolls_attempts > 0):
		if select_heroes_mode == "full":
			buttonsClicked = clickFullBarButtons()
		else:
			buttonsClicked = clickGreenBarButtons()

		sendHeroesHome()

		if buttonsClicked == 0:
			empty_scrolls_attempts = empty_scrolls_attempts - 1
		scroll()
		time.sleep(2)
	if hero_clicks == 0:
		logger("no heroes available to send to work")
	elif hero_clicks == 1:
		logger("1 hero sent to work")
	else:
		logger("{} heroes sent to work".format(hero_clicks))
	hero_clicks = 0
	goToGame()

def refreshInterval():
	r = c["time_intervals"]["refresh_interval"]
	return randint(r["start"], r["end"])

def refresh():
	refresh_interval = refreshInterval()
	if c["refresh"] == False:
		return refresh_interval

	logger("Refreshing the page")
	goToHeroes()
	clickBtn(images["all-rest"])
	time.sleep(randint(1, 3))
	pyautogui.hotkey("ctrl", "shift", "r")
	logger("The page will be refresh in {} minutes".format(refresh_interval))
	return refresh_interval

def main():

	"""Main execution setup and loop"""
	global hero_clicks
	global login_attempts
	global last_log_is_progress
	hero_clicks = 0
	login_attempts = 0
	last_log_is_progress = False

	global images
	images = load_images()

	print(splash)
	print("Your UUID to Logger is: " + getId())
	print("")

	time.sleep(7)
	t = c["time_intervals"]

	last = {
		"refresh": time.time(),
		"refresh_interval": refreshInterval(),
		"all_heroes": 0,
		"heroes": 0,
		"new_map": 0,
		"refresh_heroes": 0,
		"chest_value": 0
	}

	if c["refresh"]:
		logger("The page will be refresh in {} minutes".format(last["refresh_interval"]))

	while True:
		now = time.time()

		if checkLogin() is False:
			continue

		if now - last["refresh"] > addRandomness(last["refresh_interval"] * 60):
			last["refresh"] = now
			last["refresh_interval"] = refresh()

		if now - last["chest_value"] > addRandomness(t["check_and_save_chest"] * 60):
			last["chest_value"] = now
			saveChestPrint()

		if now - last["all_heroes"] > addRandomness(t["send_all_heroes_for_work"] * 60):
			last["heroes"] = now + (20 * 60) # pausando o refresh por 15 min
			last["refresh_heroes"] = now
			last["all_heroes"] = now
			refreshHeroes("all")

		if now - last["heroes"] > addRandomness(t["send_heroes_for_work"] * 60):
			last["heroes"] = now
			last["refresh_heroes"] = now
			refreshHeroes()

		if now - last["new_map"] > t["check_for_new_map_button"]:
			last["new_map"] = now
			if clickBtn(images["new-map"]):
				loggerMapClicked()
				if c["chest_print"]["save"]:
					saveChestPrint()

		if now - last["refresh_heroes"] > addRandomness(t["refresh_heroes_positions"] * 60):
			last["refresh_heroes"] = now
			refreshHeroesPositions()

		sys.stdout.flush()

		time.sleep(1)

if __name__ == "__main__":
	main()
