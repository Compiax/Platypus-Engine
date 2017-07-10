## ocr.py
## Split Bill Project

import sys, json, re, string, numpy as np
import pytesseract
from PIL import Image

#get name of image(s) from stdin
def read_in():
	filenames = sys.stdin.readlines()

	return json.loads(filenames[0])

# this function just checks whether it can parse the string it is sent to a float number
# if it is able to parse it, it returns the value
# if it is not able to parse it, it returns False (the string is not numeric)
def check_if_numeric(given_string):
	try: 
		float(given_string)
		return float(given_string)
	except ValueError:
		return False
	
# turn the raw string given into a json object
# @todo clean up how the json object is constructed, add the rest of the formal jsonapi structure
# 	identify and discard duplicate/trash items so they don't end up in the final json object
def structure_json(raw_string):
	item_name = ""
	json_string = '{"attributes":['
	array_flag = False

	for x in range(0, len(raw_string)):
		return_val = check_if_numeric(raw_string[x])
		
		if(return_val == False):
			if(raw_string[x] != "R"):
				item_name += raw_string[x]
		else:
			if(array_flag != False):
				json_string += ','
			json_string += '{"desc":"' + item_name + '","price":"' + raw_string[x] + '"}'
			array_flag = True
			item_name = ""
		
	json_string += ']}'

	final_dict = json.loads(json_string)

	return json.dumps(final_dict)


# main process definition, for now it is only doing basic text recognition

def main():
	filenames = read_in()
	recognised_string = ""

	for x in range(0, len(filenames)):
		im = Image.open(filenames[x])
		recognised_string += pytesseract.image_to_string(im)

	recognised_string = re.sub(r'[^a-zA-Z0-9\,\.\(\)]',' ',recognised_string)
	string_list_representation = re.split(r"[\s]",recognised_string)

	resulting_json = structure_json(string_list_representation);

	print(resulting_json)

#starting the main process 	
if __name__ == '__main__':
	main()
