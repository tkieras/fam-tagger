import platform
import subprocess
from family_resemblance_tagger.common import config

def linux_write(data):
	for key, value in data.items():
		path = value["filepath"]
		
		preexisting_tagstring = subprocess.run(['getfattr', '--only-values', '--absolute-names', '-n', 'user.tags', path], 
			stdout=subprocess.PIPE).stdout.decode('utf-8')

		preexisting_tags = list(map(lambda t: t.strip(), preexisting_tagstring.split(",")))
		
		reserved_tags = list(filter(lambda t: not t.startswith(config.dict["tag_prefix"]), preexisting_tags))
		
		if value["atags"] is None:
			prefixed_tags = []
		else:
			prefixed_tags = list(map(lambda t: config.dict["tag_prefix"] + t, value["atags"]))

		if not reserved_tags:
			all_tags = prefixed_tags
		else:
			all_tags = prefixed_tags + reserved_tags

		tagstring = ", ".join(all_tags)
		tagstring = '"' + tagstring + '"'
		subprocess.run(['setfattr', '-n', 'user.tags', '-v', tagstring, path], 
			stdout=subprocess.PIPE).stdout.decode('utf-8')

def macos_write(data):

	xml_template_start = '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"><plist version="1.0"><array>'
	xml_template_tagstart = '<string>'
	xml_template_tagend = '</string>'
	xml_template_end = '</array></plist>'


	for key, value in data.items():
		path = value["filepath"]

		get_tags_command = ['mdls', '-raw', '-name', 'kMDItemUserTags', path]

		preexisting_tagstring = subprocess.run(get_tags_command, stdout=subprocess.PIPE).stdout.decode('utf-8')

		preexisting_tags = list(map(lambda t: t.strip(), preexisting_tagstring[1:-1].split(",")))
		
		reserved_tags = list(filter(lambda t: not t.startswith(config.dict["tag_prefix"]), preexisting_tags))
		
		if value["atags"] is None:
			prefixed_tags = []
		else:
			prefixed_tags = list(map(lambda t: config.dict["tag_prefix"] + t, value["atags"]))

		if not reserved_tags:
			all_tags = prefixed_tags
		else:
			all_tags = prefixed_tags + reserved_tags

		xml_string = xml_template_start

		for tag in all_tags:
			xml_tag = xml_template_tagstart + tag + xml_template_tagend
			xml_string += xml_tag

		xml_string += xml_template_end


		tag_command = ['xattr', '-w', 'com.apple.metadata:_kMDItemUserTags', xml_string, path]
		subprocess.run(tag_command, stdout=subprocess.PIPE).stdout.decode('utf-8')






def write_tags(data):
	if platform.system() == "Linux":
		linux_write(data)
	elif platform.system() == "Darwin":
		macos_write(data)
	elif platform.system() == "Windows":
		pass

def remove_tags(data):
	for key, value in data.items():
		value["atags"] = None

	write_tags(data)



