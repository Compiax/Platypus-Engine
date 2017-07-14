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
	
def real_item(test_string):
	check_string1 = "total"
	check_string2 = "vat"
	check_string3 = "tax"
	check_string4 = "debit"
	check_string5 = "card"
	check_string6 = "payment"
	check_string7 = "due"
	check_string8 = "incl"
	check_string9 = "paid"
	check_string10 = "tendered"

	if(check_string1 in test_string.lower() or check_string1 == test_string.lower()):
		return False
	if(check_string2 in test_string.lower() or check_string2 == test_string.lower()):
		return False
	if(check_string3 in test_string.lower() or check_string3 == test_string.lower()):
		return False
	if(check_string4 in test_string.lower() or check_string4 == test_string.lower()):
		return False
	if(check_string5 in test_string.lower() or check_string5 == test_string.lower()):
		return False
	if(check_string6 in test_string.lower() or check_string6 == test_string.lower()):
		return False
	if(check_string7 in test_string.lower() or check_string7 == test_string.lower()):
		return False
	if(check_string8 in test_string.lower() or check_string8 == test_string.lower()):
		return False
	if(check_string9 in test_string.lower() or check_string9 == test_string.lower()):
		return False
	if(check_string10 in test_string.lower() or check_string10 == test_string.lower()):
		return False

	return True

# turn the raw string given into a json object
# @todo clean up how the json object is constructed, add the rest of the formal jsonapi structure
# 	identify and discard duplicate/trash items so they don't end up in the final json object
def structure_json(raw_string):
	item_name = ""
	json_string = '{"attributes":{"data":['
	array_flag = False
	item_total = 0

	for x in range(0, len(raw_string)):
		return_val = check_if_numeric(raw_string[x])
		
		if(return_val == False):
			if(raw_string[x] != "R" and len(raw_string[x]) != 0):
				item_name += raw_string[x]
		else:
			if(return_val > 0 and return_val < 80000 and item_name != ""):
				if(real_item(item_name) == True):
					item_total += return_val
					if(array_flag != False):
						json_string += ','
					json_string += '{"desc":"' + item_name + '","price":"' + raw_string[x] + '"}'
					array_flag = True
					item_name = ""
				else:
					break
		
	json_string += ']},"relationships":{"data":{"total":"'+ str(item_total) +'"}}}'
                         
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
