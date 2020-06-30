from multiprocessing.connection import Client
import argparse
import hashlib
from family_resemblance_tagger.common import config

def prepare_message(path):
	checksum = hashlib.md5()
	for line in open(path, "rb"):
		checksum.update(line)

	checksum = checksum.hexdigest()

	msg = {"checksum" : checksum, "filepath" : path}
	return msg

def send_message(msg):
	try:
		conn = Client(addr, authkey=conf["preprocess_server_authkey"])
		conn.send(msg)
		conn.close()
	except ConnectionRefusedError:
		print("Could not establish connection with tagger server. Make sure extract_potential_tags/main.py is running.")
		exit()

def main():

	for path in args.path:
		msg = prepare_message(path)
		print(msg)
		send_message(msg)


if __name__=="__main__":

	parser = argparse.ArgumentParser(description="Add file/folder to queue for tagging)")

	parser.add_argument("path", help="path(s) of files to add to queue", nargs="+")

	args = parser.parse_args()
	conf = config.dict
	addr = (conf["preprocess_server_addr"], conf["preprocess_server_port"])
	main()


