#!/usr/bin/env python3

import os
import time
import getpass
import datetime
import argparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

GitHubUser="kkaspergit"
CredSet={}
CredSet['username']='kkasper.pub@gmail.com'
CredSet['password']=''
LoginUrl="https://github.com/login"
RepoName="ISTST-PUT-DST-"+str(datetime.datetime.now().strftime('%Y%m%d%H%M'))
RepoUrl="https://github.com/"+GitHubUser+"/"+RepoName
HomeUrl="https://github.com"
UploadUrl=RepoUrl+"/upload/main"
# Success Indicators
LoginSuccessTitle="GitHub"
RepoSuccessTitle=GitHubUser+'/'+RepoName
UploadPageTitle="Upload files · "+GitHubUser+"/"+RepoName
UploadSuccessTitle=""



def env_creds():
	# For use in CI/CD deployment
	global CredSet
	# Pull Password from ENV
	CredSet['password'] = os.getenv("GITHUB_PASSWORD")
	return True


def prompt_creds():
	# For interactive Use
	global CredSet
	# Prompt for Password
	CredSet['password'] = getpass.getpass(prompt="Password for "+CredSet['username']+": ")
	return True


def github_login():
	cont_login=True
	global LoginUrl
	username_field_id = "login_field"
	password_field_id = "password"
	try:
		driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
	except Exception as e:
		print('Chrome init failed')
		print(e)
		cont_login=False
		driver=None
	if cont_login:
		driver.get(LoginUrl)
		username_field = driver.find_element("id", username_field_id)
		password_field = driver.find_element("id", password_field_id)
		username_field.clear()
		password_field.clear()
		username_field.send_keys(CredSet['username'].strip())
		password_field.send_keys(CredSet['password'].strip())
		password_field.submit()
	# VERIFY LOGIN SUCCESS
	checkVal=driver.title
	if checkVal != LoginSuccessTitle:
		driver.quit()
		driver=None
		print('Failure to Login: '+str(checkVal))
	return driver


def github_logout(driver):
	retVal=True
	return retVal


def create_repo(driver):
	retVal=True
	global RepoName
	global HomeUrl
	driver.get(HomeUrl)
	checkVal=driver.title
	if checkVal != LoginSuccessTitle:
		retVal=False
		print('Failure to Navigate to Home')
	else:
		# Create Repo
		# - Press New Button
		driver.find_element(By.LINK_TEXT, "New").click()
		# - Set Repo Name
		driver.find_element(By.ID, ":r5:").send_keys(RepoName)
		# - Mark Repo Private
		driver.find_element(By.ID, ":rg:").click()
		# - Enable README.md creation
		driver.find_element(By.ID, ":ri:").click()
		# - Submit FORM
		time.sleep(3)
		subButton=driver.find_element(By.ID, ":r5:").submit()
		time.sleep(3)
	return retVal
	


def file_upload(driver, file_name):
	retVal=True
	global RepoUrl
	if retVal:
		# Navigate to Repo
		driver.get(RepoUrl)
		checkVal=driver.title
		if checkVal != RepoSuccessTitle:
			retVal=False
			print('Failure to Navigate to DEST Repo: '+str(checkVal))
	if retVal:
		# Navigate to Repo's Upload Page
		driver.get(UploadUrl)
		checkVal=driver.title
		if checkVal != UploadPageTitle:
			retVal=False
			print('Failed to navigate to repo upload page')
		time.sleep(3)
	if retVal:
		# Set File for Upload
		fileInput = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
		fileInput.send_keys(os.path.abspath(file_name))
		time.sleep(10)
	if retVal:
		# Commit Upload
		subForm=driver.find_element(By.CSS_SELECTOR, 'form.file-commit-form').submit()
		time.sleep(10)
		print(driver.title)
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
				#fRec['content'] = fContent.read()
				fRec['content'] = 'SUCCESS'
				fContent.close()
			retVal.append(fRec)
		fList.close()
	return retVal


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Send Files to dlptest HTTPS POST")
	parser.add_argument("-f", "--file", help="File with list of files to send", required=True)
	parser.add_argument("-o", "--output", help="Capture output to file (defaults to dlptest.rpt)", default="dlptest.rpt")
	parser.add_argument("-p", "--prompt", action="store_true", default=0, help="Prompt for password")
	parser.add_argument("-v", "--verbose", action="store_true", default=0, help="Verbose")
	args = parser.parse_args()
	cont=True
	resultLog=[]
	if args.verbose:
		print('Retrieving files for HTTP PUTs')
	testFiles=get_content()
	if args.verbose:
		print('Logging into GitHub')
	if args.prompt:
		prompt_creds()
	else:
		env_creds()
	drv=github_login()
	if drv != None:
		# CREATE REPO
		if args.verbose:
			print('Creating DST Repository: '+str(RepoName))
		cont=create_repo(drv)
		if cont:
			# SEND FILES
			if args.verbose:
				print('Sending files via HTTP PUTs')
			for testFile in testFiles:
				res2log='"'+str(datetime.datetime.now())+'","'
				res2log=res2log+str(testFile['filename'])+'","'
				res2log=res2log+str(file_upload(drv, testFile['filename']))+'"'
				if args.verbose:
					print(res2log)
				resultLog.append(res2log)
			# CREATE REPORT
			if args.verbose:
				print('Creating Report: '+str(args.output))
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
			if args.verbose:
				print('Done.')

