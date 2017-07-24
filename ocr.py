
## ocr.py
## Split Bill Project

'''
{
	"data": {
		"type": "success/failure",
		"id": "xxx",
		"attributes": {
			"data":[
				{"desc":"description of item 1","price":"xx.xx"},
				{"desc":"description of item 2","price":"xx.xx"},
				{"desc":"description of item 3","price":"xx.xx"}
			]
		},
		"relationships": {
			"data":{total":"xx.xx"}
		}
	},
	"errors": {
		"id": "xxx",
		"code": "ERR1",
		"title": "semantic description"
	}
}
'''
import sys, json, re, string
import pytesseract
import cv2
import os
from PIL import Image

#get name of image(s) from stdin
def read_in():
	filenames = sys.stdin.readlines()
	return json.loads(filenames[0])

#turn the raw string given into a json object
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

def structure_json(raw_string):
	if(len(raw_string) == 0):

		json_string = '{"errors":{"id":"xx","code":"NOTXT","title":"No text was recognised from the image"}}'

		final_dict = json.loads(json_string)

		return json.dumps(final_dict)

	elif(len(raw_string) < 4):

		json_string = '{"errors":{"id":"xx","code":"GARBAGE","title":"Garbage text recognised from the image"}}'

		final_dict = json.loads(json_string)

		return json.dumps(final_dict)

	else:
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


# Returns an image object to be proccessed by the Optical Character 
# recognition softwatre Tesseract. 
# Image Argument specifies the name of the image file to be processed
# <p>
# The image is processed using the Open CV software
# The image is loaded in grayscale and subsequently denoised and thresholded
# to improve the quality of the image used to obtain Tesseract charcter data
#
# @param	image 	name of the image to be processed
# @return 			image object of the image specified by the image parameter 

def processImage(image):

	img = cv2.imread(image, 0)
	img = cv2.fastNlMeansDenoising(img,10,10,7,21)

	blur = cv2.GaussianBlur(img,(5,5),0)
	ret3,th3 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		
	cv2.imwrite('temp.tif', th3)
	im = Image.open('temp.tif')

	return im

# main process definition, for now it is only doing basic text recognition
# @todo call the structure_json() function and instead of printing a
# 		string it will print a stringified json object that conforms
# 		to the agreed upon JSON communication standard.

def main():
	filenames = read_in()
	recognised_string = ""

	for x in range(0, len(filenames)):
		im = processImage(filenames[x])	
		recognised_string += pytesseract.image_to_string(im)

	recognised_string = re.sub(r'[^a-zA-Z0-9\,\.\(\)]',' ',recognised_string)
	string_list_representation = re.split(r"[\s]",recognised_string)

	resulting_json = structure_json(string_list_representation);

	print(resulting_json)
	os.remove('temp.tif')

#starting the main process 	
if __name__ == '__main__':
	main()
