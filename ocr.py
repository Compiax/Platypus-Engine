
## ocr.py
## Split Bill Project

import sys, json, re, string, math, time
import numpy as np
import pytesseract
import Levenshtein
import cv2
import os
import jsonTemplate
from billItem import BillItem
from PIL import Image

currentJsonTemplate = jsonTemplate.JsonTemplate()
commonWords = set(line.strip().lower() for line in open('commonWords.txt'))


def subprocess_main_call(fileLocation, templateName):

	jsonTemplateSetup(templateName)

	recognised_string = ""

	im = processImage(fileLocation)
	recognised_string += pytesseract.image_to_string(im)

	#turns the single string into an array split on endlines
	line_by_line = re.split(r"[\n]", recognised_string)

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
			if(e < lines[i].getSize()-2 and lines[i].getField(e).isdigit() == True and lines[i].getField(e+1) in [".", ","] and lines[i].getField(e+2).isdigit() == True):
				lines[i].setField(e, lines[i].getField(e) + "." + lines[i].getField(e+2))
				lines[i].pop(e+2)
				lines[i].pop(e+1)


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
	img = cv2.GaussianBlur(img, (5,5), 0)
	img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)

	cv2.imwrite('temp.tif', img)
	im = Image.open('temp.tif')

	return im



def is_valid_line(test_string):

	check_strings = [
		"cashier",
		"---",
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

		print("\nRAW DATA TO JSONIFY: "+str(len(lines))+" lines")
		for thing in lines:
			print(thing.printAll())
		print("")

		for i in range(len(lines)):

			numeric_value = False
			for e in range(lines[i].getSize()):

				test_numeric_value = is_numeric_price(lines[i].getField(e))

				if test_numeric_value != False and test_numeric_value < numeric_value:
					numeric_value = test_numeric_value

				current_field = lines[i].getField(e).split().lower()

			elif current_field != "r" and len(current_field) != 0 and len(current_field) >= 2 and is_unit(current_field) == False and is_too_numeric(current_field) == False:

						closestWord = ""
						smallestDistance = 100

						# Levenshtein distance of half the size of the tested word, where 3 is the greatest size the distance may be
						distanceLimit = min(math.floor(len(current_field))/2.0), 3)

						# Find closest word in common word dictionary if any
						for word in commonWords:
							if current_field != word:
								newDistance = Levenshtein.distance(str(current_field), word)
								if newDistance <= distanceLimit and newDistance < smallestDistance:
									closestWord = word
									smallestDistance = newDistance
							else:
								closestWord = ""
								break

						if closestWord != "":
							print("Levenshtein: "+current_field+" changed to "+closestWord)
							lines[i].setField(e, closestWord)

						# Concat word to description of item
						if item_name == "":
							item_name = current_field
						else:
							item_name += " " + current_field

			# If the numeric value is valid then save the bill item/row
			if numeric_value != False and numeric_value > 0 and numeric_value < 80000 and item_name != "":
				# If the item description is a illegal word (Total, Vat, Tax, etc) then it is the end of the relevant bill
				if real_item(item_name) == True or item_id == 1:
					item_total += numeric_value
					if array_flag != False:
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

		json_string = json.loads(json_string)
		return json.dumps(json_string)



"""
Checks whether the string that is passed through to the function can be parsed to a float value

:param given_string: The string to be checked
:returns: False if the parameter that is passed through cannot be parsed to a float value, the float value if it can be parsed
"""
def is_numeric_price(given_string):
	given_string = given_string.strip()

	if(len(re.findall(r'[0-9\,\.]', given_string.strip()))/float(len(given_string)) > 0.5):

		given_string = re.sub(r'[\,]', '.', given_string)
		given_string = re.sub(r'[o\(\)JuUoOQDCcae]', '0', given_string)
		given_string = re.sub(r'[R]', '', given_string)
		given_string = re.sub(r'[iIltTj]', '1', given_string)
		given_string = re.sub(r'[sS]', '5', given_string)
		given_string = re.sub(r'[zZ]', '2', given_string)

		try:
			try:
				int(given_string)
				return False
			except ValueError:
				real_number = float(given_string)
				return real_number
		except ValueError:
			return False
	else:
		return False

def is_too_numeric(test_string):
	test_string = test_string.lower().strip()

	if(len(re.findall(r'[0-9\,\.]', test_string.strip()))/float(len(test_string)) > 0.5):
		return True
	return False


def is_unit(test_string):
	check_strings = [
			"ml",
			"gr",
			"gm",
			"li",
			"grm",
			"mil"
	]

	for check_string in check_strings:
		if(check_string == test_string.lower()):
			return True
	return False



"""
Brute force checks whether the string it is being passed is a predefined keyword,
if it is a predefined keyword the string being passed should not be added as an item

:param test_string: The string that is checked for keywords
:returns: False if the test_string is a keyword, but True if the test_string is not a keyword (thusly a real item on the bill)
"""
def real_item(test_string):
	test_string = test_string.strip()
	check_string_parts = [
		"total",
		"vat",
		"tax",
		"debit",
		"card",
		"payment",
		"due",
		"incl",
		"paid",
		"tendered",
	]

	for check_string in check_string_parts:
		if(check_string in test_string or check_string == test_string):
			return False

	return True
