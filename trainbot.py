from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import secrets

def tweet(delaytotal,delayrate,traincount):
	rate = (traincount - delayrate) / traincount
	tweet = "Donabate's trains to Connolly had "+str(delaytotal)+" minutes of delays today. Irish Rail considers this to be "+str(rate)+"% punctuality."
	
	driver = webdriver.Chrome()
	driver.get("https://m.twitter.com/login")
	time.sleep(5)

	enteruser = driver.find_element_by_name("session[username_or_email]")
	enteruser.send_keys("IgnoredDelays")
	enterpassword = driver.find_element_by_name("session[password]")
	enterpassword.send_keys(secrets.password + Keys.ENTER)
	time.sleep(4)

	driver.get("https://m.twitter.com/compose/tweet")
	time.sleep(3)
	actions = ActionChains(driver)
	actions.send_keys(tweet)
	actions.key_down(Keys.LEFT_CONTROL)
	actions.send_keys(Keys.ENTER)
	actions.key_up(Keys.LEFT_CONTROL)
	actions.perform()
	time.sleep(10)
	driver.close()
	

def getdelay(soup, number):
	block = soup.find_all("div", class_="hfs_connectionTime departure")[number]
	rt = str(block.find("span")).split(" ")
	if len(rt) == 1:
		return 0
	delay = rt[1]
	return int(delay[delay.find("+")+1:])

def gettraintime(soup, number):
	block = soup.find_all("div", class_="hfs_connectionTime departure")[number]
	traintime = block.find("div", class_="hfs_timeRow hfs_plantime").get_text().split(":")
	return int(traintime[0]),int(traintime[1])

urlpart1 = "http://journeyplanner.irishrail.ie/webapp/?REQ0JourneyStopsS0A=1&HWAI%3DJS%21js=yes&HWAI%3DJS%21ajax=yes&REQ0JourneyStopsZ0A=1&#!start|1!REQ0JourneyStopsS0G|Donabate!REQ0JourneyStopsS0ID|A=1@O=Donabate@X=-6151344@Y=53485511@U=80@L=6010015@B=1@p=1570878154@!REQ0JourneyStopsZ0G|Connolly!REQ0JourneyStopsZ0ID|A=1@O=Connolly@X=-6246693@Y=53352885@U=80@L=6000036@B=1@p=1570878154@!journey_mode|single!REQ0JourneyDate|"
urlpart2 = "!REQ0JourneyTime|0!Number_adults|1!Number_children|0!Number_students|0"


while 1:
	rn = time.localtime(time.time())
	url = urlpart1 + "%s/%s/%s" % (rn.tm_mday, rn.tm_mon, rn.tm_year) + urlpart2

	day = rn.tm_wday
	if day == 5:
		traincount = 20
		nexttrain = [7,2]
	elif day == 6:
		traincount = 15
		nexttrain = [8,27]
	else:
		traincount = 29
		nexttrain = [6,36]
	
	totaldelay = 0
	delayrate = traincount
	
	print("Starting day %s/%s/%s" % (rn.tm_mday, rn.tm_mon, rn.tm_year))
	
	for i in range(traincount):
		while 1:
			if rn.tm_hour == nexttrain[0] and rn.tm_min > nexttrain[1] - 2:
				driver = webdriver.Chrome()
				driver.get(url)
				time.sleep(4)

				dropdown = Select(driver.find_element_by_tag_name("select"))
				dropdown.select_by_value("1")
				time.sleep(1)

				go = driver.find_element_by_name("submitTPForm")
				go.click()
				time.sleep(4)

				page = driver.page_source
				soup = BeautifulSoup(page, features="html.parser")
				driver.close()
				
				delay = getdelay(soup,i)
				totaldelay += delay
				if delay > 10:
					delayrate -= 1
				
				print("train at",nexttrain,"is delayed by",delay)
				
				nexttrain = gettraintime(soup,i+1)
				print("next train is at",nexttrain)
				break
			time.sleep(60)
			rn = time.localtime(time.time())
	
	print("total delays of",totaldelay,"for day %s/%s/%s" % (rn.tm_mday, rn.tm_mon, rn.tm_year))
	print("success rate of",(traincount-delayrate)/traincount)
	tweet(delaytotal,delayrate,traincount)
	time.sleep(60*60*7)
