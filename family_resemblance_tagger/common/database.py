import json
import os

database_mod_path = os.path.dirname(__file__)
datapath = database_mod_path + "/../data/database.json"

def load_data():

	if not os.path.isfile(datapath):
		return {}
		
	try:
		with open(datapath, "r") as d:
			data = json.load(d)
	except json.JSONDecodeError:
		data = {}

	return data

def save_data(data):
	with open(datapath, "w") as d:
		json.dump(data, d)



