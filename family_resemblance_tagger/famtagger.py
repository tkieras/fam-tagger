import argparse
import json
from pathlib import Path, PurePath

from simplejson.errors import JSONDecodeError
import requests
from requests.auth import HTTPBasicAuth
from getpass import getpass
from pydoc import locate

import file_loaders

CONFIG_HOME = str(PurePath(Path.home(), ".config", "famtagger.config"))

config = None

def load_config(path):
	data = None
	try:
		with open(path) as infile:
			data = json.loads(infile.read())
	except IOError:
		pass

	return data

def write_config(path):
	with open(path, "w") as outfile:
		json.dump(config, outfile)


class BaseRequest():
	def __init__(self):
		self.url = config["host"]
		self.auth = None

	def get(self):
		return requests.get(self.url, auth=self.auth)

	def post(self, data):
		return requests.post(self.url, auth=self.auth, json=data)

class RegistrationRequest(BaseRequest):
	authRegisterPath = "api/auth/register"

	def __init__(self):
		super().__init__()
		self.url += self.authRegisterPath

	def get(self):
		return None


class AuthenticatedRequest(BaseRequest):
	def __init__(self):
		super().__init__()
		self.auth = HTTPBasicAuth(config["username"], config["password"])

class DocumentsRequest(AuthenticatedRequest):
	documentsPath = "api/documents/"

	def __init__(self):
		super().__init__()
		self.url += self.documentsPath

	def delete(self, doc_id):
		self.url += str(doc_id)
		return requests.delete(self.url, auth=self.auth)

class AbsoluteKeywords(DocumentsRequest):
	absoluteKeywordsPath = "{}/absolute_keywords"
	
	def __init__(self):
		super().__init__()
	
	def get(self, doc_id):
		self.url += (self.absoluteKeywordsPath.format(doc_id))
		return super().get()

	def post(self):
		return None


def report(response):
	print("Status Code: {}".format(response.status_code))

	try:
		json = response.json()
		print(json)
	except JSONDecodeError:
		pass


def get_absolute_keywords(doc_id):
	report(AbsoluteKeywords().get(doc_id))
	

def register(username, password):
	return RegistrationRequest().post({"username" : username, 
									   "password" : password})
	
def add_document(name, content):
	report(DocumentsRequest().post({"name" : name, "content": content}))
	

def delete_document(doc_id):
	report(DocumentsRequest().delete(doc_id))

def load_file(path):
	loaders = file_loaders.__all__

	text = None

	for loaderName in loaders:
	    loader = locate("file_loaders." + loaderName)
	    text = loader.load(path)
	    if text is not None:
	    	return text

	return text

def init_user():
	
	if "username" not in config or "password" not in config:
		print("Initial authentication required. "
			  "Please choose a username/password:")
		username = input("Username: ").strip()
		password = getpass()

		response = register(username, password)
		
		report(response)
		
		if response.status_code == 200:
			config["username"] = username
			config["password"] = password
			print("These values are saved in: {}".format(CONFIG_HOME))
			write_config(CONFIG_HOME)
		else:
			print("Exiting")
			return False

	return True	

def main(args):
	for path in args.path:
		content = load_file(path)
		if content is None:
			print("No text content found in file: {}".format(path))
			continue

		if args.add:
			add_document(path, content)

		if args.keywords:
			# API interaction needs improvement 
			## for clients that use paths rather than ids
			## workaround enabled by server returning redirect when
			## duplicate documents added.
			add_document(path, content)
		

def run():
	parser = argparse.ArgumentParser(description="Lightweight client"
									" to interact with keywords_service API.")

	parser.add_argument("path", 
						help="path(s) of files to add as documents", 
						nargs="+")

	parser.add_argument("-a", "--add", action='store_true',
					help="Add specified paths as new documents.")

	parser.add_argument("-k", "--keywords", action='store_true',
					help="Print keywords and weights for the documents.")

	args = parser.parse_args()


	global config 
	config = load_config(CONFIG_HOME)

	if not config:
		print("Could not find user config file in {}".format(CONFIG_HOME))
		print("Loading default config file.")
		config = load_config("default_config.json")
	if not init_user():
		exit()

	main(args)
	
if __name__=="__main__":
	run()
	