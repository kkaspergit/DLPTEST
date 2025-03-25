#!/usr/bin/env python3

import datetime
import argparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

PostUrl="https://dlptest.com/https-post"
textInput="item_meta[6]"

def http_post(content):
	retVal='ERROR'
	driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
	driver.get(PostUrl)
	text_box = driver.find_element("name",textInput)
	text_box.clear()
	text_box.send_keys(content)
	text_box.send_keys(Keys.RETURN)
	text_box.submit()
	msgDiv = driver.find_element(By.CLASS_NAME, "frm_message")
	retVal=str(msgDiv.get_attribute("innerHTML")).strip()
	return retVal

def get_content():
	retVal=[]
	haveFiles=True
	try:
		fList=open(args.file,'r')
	except Exception as e:
		haveFiles=False
		print('ERROR:')
		print(e)
	if haveFiles:
		for fName in fList:
			haveContent=True
			fRec={}
			fRec['filename'] = fName.strip()
			fRec['content'] = 'ERROR'
			try:
				fContent = open(fName.strip(),'r')
			except Exception as e:
				haveContent = False
				print('ERROR:')
				print(e)
			if haveContent:
				fRec['content'] = fContent.read()
				fContent.close()
			retVal.append(fRec)
		fList.close()
	return retVal


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Send Files to dlptest HTTPS POST")
	parser.add_argument("-f", "--file", help="File with list of files to send", required=True)
	parser.add_argument("-o", "--output", help="Capture output to file", default="dlptest.rpt")
	parser.add_argument("-v", "--verbose", action="store_true", default=0, help="Verbose")
	args = parser.parse_args()
	resultLog=[]
	testFiles=get_content()
	for testFile in testFiles:
		res2log='"'+str(datetime.datetime.now())+'","'
		res2log=res2log+str(testFile['filename'])+'","'
		res2log=res2log+http_post(testFile['content'])+'"'
		if args.verbose:
			print(res2log)
		resultLog.append(res2log)
	haveOutFile = True
	try:
		reportFile=open(args.output,'w')
	except Exception as e:
		haveOutFile = False
		print('ERROR: writing output')
		print(e)
	if haveOutFile:
		for res in resultLog:
			reportFile.write(str(res)+'\n')
		reportFile.close()

