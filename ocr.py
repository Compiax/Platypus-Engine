
## ocr.py
## Split Bill Project

import sys, json, re, string
import numpy as np
import pytesseract
import cv2
import os
import jsonTemplate
from billItem import BillItem
from PIL import Image

currentJsonTemplate = jsonTemplate.JsonTemplate()

def subprocess_main_call(fileLocation, templateName):

	jsonTemplateSetup(templateName)

	recognised_string = ""

	im = processImage(fileLocation)
	recognised_string += pytesseract.image_to_string(im)

	#turns the single string into an array split on endlines
	line_by_line = re.split(r"[\n]",recognised_string)

	#remove specific irrelevant lines
	count = len(line_by_line)
	i = 0
	while i < count:
		if( is_valid_line(line_by_line[i]) == False):
			line_by_line.pop(i)
			count = count - 1
		i = i + 1

	#removes random garbage characters like $, ~, and @
	for i in range(len(line_by_line)):
		line_by_line[i] = re.sub(r'[^a-zA-Z0-9\s\,\.\(\)]', '', line_by_line[i])

	lines = []
	for i in range(len(line_by_line)):
		lines.append(BillItem(line_by_line[i].split()[:]))



	#if the ['23']['.']['99'] situation occurs, this loop will ensure the float value is sent through as a single item
	for i in range(len(lines)):
		for e in range(lines[i].getSize()):
			if(e < lines[i].getSize()-2 and lines[i].getField(e).isdigit() == True and (lines[i].getField(e+1) == "." or lines[i].getField(e+1) == ",") and lines[i].getField(e+2).isdigit() == True):
				lines[i].setField(e, lines[i].getField(e) + "." + lines[i].getField(e+2))
				lines[i].pop(e+1)
				lines[i].pop(e+2)


	resulting_json = structure_json(lines)

	print("\nJSON RESULT:\n"+resulting_json)
	#os.remove('temp.tif')
	return resulting_json



def jsonTemplateSetup(templateName):
	global currentJsonTemplate
	currentJsonTemplate = {
		"PIQ" : jsonTemplate.PIQ(),
		"PQI" : jsonTemplate.PQI(),
		"QIP" : jsonTemplate.QIP(),
		"QPI" : jsonTemplate.QPI(),
		"IQP" : jsonTemplate.IQP(),
		"IPQ" : jsonTemplate.IPQ()
	}[templateName]



"""
Returns an image object to be proccessed by the Optical Character
recognition softwatre Tesseract. Image Argument specifies the name of the image file to be processed
The image is processed using the Open CV software. The image is loaded in grayscale and subsequently denoised and thresholded
to improve the quality of the image used to obtain Tesseract charcter data

:param	image: 	name of the image to be processed
:returns: image object of the image specified by the image parameter
"""
def processImage(image):


	img = cv2.imread(image, 0)

	cv2.fastNlMeansDenoising(img,img,20,7,21)

	ret3,th3 = cv2.threshold(img,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
	# ret3,th3 = cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	# th1 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)

	cv2.imwrite('temp.tif', th3)
	im = Image.open('temp.tif')

	return im



def is_valid_line(test_string):

	check_strings = [
		"cashier",
		"--------",
		"date",
		"table"
	]

	try:
		float(test_string)
		return False
	except ValueError:
		if(test_string == "\s" or test_string == ""):
				return False
		for check_string in check_strings:
			if(check_string in test_string.lower() or check_string == test_string.lower()):
				return False
		return True



"""
This function takes the raw array and creates a structured JSON object

@todo: perfect the quantity of item recognised, as of now (19/08/2017) each item has a quantity of 1 by default.

:param lines: The string array that the JSON object is built up out of
:returns: the final JSON object
"""
def structure_json(lines):

	if(len(lines) == 0):

		return json.dumps(json.loads('{"type":"failure","errors":{"id":"xx","code":"NOTXT","title":"No text was recognised from the image"}}'))

	elif(len(lines) <= 1):

		return json.dumps(json.loads('{"type":"failure","errors":{"id":"xx","code":"GARBAGE","title":"Garbage text recognised from the image"}}'))

	else:

		# TEMPLATING COMES IN HERE
		currentJsonTemplate.structure_json()

		item_name = ""
		json_string = '{"type":"success","attributes":{"data":['
		array_flag = False
		item_total = 0
		item_id = 1

		print("\nRAW DATA TO JSONIFY:")
		for thing in lines:
			thing.printAll()
		print("")

		for i in range(len(lines)):
			numeric_value = False
			for e in range(lines[i].getSize()):
				numeric_value = check_if_numeric(lines[i].getField(e))

				if(numeric_value == False):
					if(lines[i].getField(e) != "R" and len(lines[i].getField(e)) != 0 and len(lines[i].getField(e)) >= 2):
						if(item_name == ""):
							item_name = lines[i].getField(e)
						else:
							item_name += " " + lines[i].getField(e)

			if(numeric_value != False and numeric_value > 0 and numeric_value < 80000 and item_name != ""):
				if(real_item(item_name) == True):
					item_total += numeric_value
					if(array_flag != False):
						json_string += ','
					json_string += '{"id":"' + str(item_id) + '","desc":"' + item_name + '","price":"' + str(numeric_value) + '","quantity":"1"}'
					item_id += 1
					array_flag = True
					item_name = ""
				else:
					break
			else:
				item_name = ""
				numeric_value = False

		json_string += ']},"relationships":{"data":{"total":"'+ str(item_total) +'"}}}'

		final_dict = json.loads(json_string)

		return json.dumps(final_dict)



"""
Checks whether the string that is passed through to the function can be parsed to a float value

:param given_string: The string to be checked
:returns: False if the parameter that is passed through cannot be parsed to a float value, the float value if it can be parsed
"""
def check_if_numeric(given_string):
	stringList = list(given_string)
	for i in range(len(stringList)):
		if stringList[i] == ',':
			stringList[i] = '.'
	newString = "".join(stringList)
	try:
		float(newString)
		try:
			int(newString)
			return False
		except ValueError:
			return float(newString)
	except ValueError:
		return False



"""
Brute force checks whether the string it is being passed is a predefined keyword,
if it is a predefined keyword the string being passed should not be added as an item

:param test_string: The string that is checked for keywords
:returns: False if the test_string is a keyword, but True if the test_string is not a keyword (thusly a real item on the bill)
"""
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
