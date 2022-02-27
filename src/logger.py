from src.date import dateFormatted
from src.nftbrothers import sendLog
import sys
import yaml

stream = open("./config.yaml", "r")
c = yaml.safe_load(stream)

def logger(message):
	formatted_message = "[{}] => {}".format(dateFormatted(), message)
	print(formatted_message)

	if (c["save_log_to_file"] == True):
		logger_file = open("./logs/logger.log", "a", encoding="UTF-8")
		logger_file.write(formatted_message + "\n")
		logger_file.close()
		sendLog(message)

	return True

def loggerMapClicked():
	logger("New Map button clicked!")

	if (c["save_log_to_file"] == True):
		logger_file = open("./logs/new-map.log", "a", encoding="UTF-8")
		logger_file.write(dateFormatted() + "\n")
		logger_file.close()

	return True
