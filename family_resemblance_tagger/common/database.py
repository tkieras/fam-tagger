import os
import sqlite3

database_mod_path = os.path.dirname(__file__)
datapath = database_mod_path + "/../data/database.db"

def init_db():
	conn = sqlite3.connect(datapath)
	conn.execute("create table if not exists docs (filepath, checksum, keywords, keywords_date, tags, tags_date)")


def format_keywords_for_db(keywords):
	keyword_strings = [":".join([k, str(v)]) for k, v in keywords.items()]
	all_keywords = ",".join(keyword_strings)
	return all_keywords

def format_keywords_from_db(all_keywords):
	keyword_strings = all_keywords.split(",")
	keywords = {}
	for item in keyword_strings:
		k, v = item.split(":")
		keywords[k] = float(v)
	return keywords

def check_already_added(checksum):
	conn = sqlite3.connect(datapath)

	cursor = conn.execute("select filepath from docs where checksum is ?", [checksum])
	result = cursor.fetchone()
	conn.close()

	if result is None:
		return None

	return result[0]

def update_filepath(checksum, new_filepath):
	conn = sqlite3.connect(datapath)

	conn.execute("update docs set filepath = ? where checksum is ?", [new_filepath, checksum])

	conn.commit()
	conn.close()

def insert_item(item):
	conn = sqlite3.connect(datapath)
	statement = """ insert into docs (filepath, checksum, keywords, keywords_date)
		values (?, ?, ?, ?)"""
	conn.execute(statement, [item["filepath"], item["checksum"], item["keywords"], item["keywords_date"]])
	conn.commit()
	conn.close()


def load_all_data():
	conn = sqlite3.connect(datapath)
	data = {}

	cursor = conn.execute("select * from docs")
	for item in cursor:
		entry = {}
		entry["filepath"] = item[0]
		entry["checksum"] = item[1]
		entry["keywords"] = format_keywords_from_db(item[2])
		entry["keywords_date"] = item[3]
		entry["tags"] = item[4]
		entry["tags_date"] = item[5]

		data[entry["checksum"]] = entry

	return data

