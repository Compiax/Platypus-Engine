## ocr.py
## Split Bill Project

import sys, json, numpy as np
import pytesseract
from PIL import Image

#get name of image(s) from stdin
def read_in():
	filenames = sys.stdin.readlines()

	return json.loads(filenames[0])

#turn the raw string given into a json object
def structure_json(raw_string):
	return json.dumps(raw_string)


# main process definition, for now it is only doing basic text recognition
# @todo call the structure_json() function and instead of printing a
# 		string it will print a stringified json object that conforms
# 		to the agreed upon JSON communication standard.

def main():
	filenames = read_in()
	recognised_string = ""

	for x in range(0, len(filenames)):
		im = Image.open(filenames[x])
		recognised_string += pytesseract.image_to_string(im)

	print(recognised_string,'%s')

#starting the main process 	
if __name__ == '__main__':
	main()