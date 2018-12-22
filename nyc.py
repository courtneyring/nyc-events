import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from bs4 import BeautifulSoup

SCOPES ='https://www.googleapis.com/auth/calendar'

store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))


with open('data.json') as json_file:  
    data = json.load(json_file)


driver = webdriver.Chrome('./chromedriver')

driver.get("https://www.nycgo.com/things-to-do/events-in-nyc/dont-miss-this-month/december?type=all&startDate=2018-12-09&endDate=2018-12-15")

driver.execute_script("scroll(0, 1000);")



time.sleep(2)
closeButton = driver.find_element_by_css_selector('.modal-dialog > .modal-content > .close')
background = driver.find_element_by_css_selector('.ng-scope > img')
closeButton.click()
#background.click()
#wait = WebDriverWait(driver, 10)
#wait.until(EC.element_to_be_clickable(driver.find_element_by_xpath("//h4[@class='item-title ng-scope']/a")))

time.sleep(2)
#print(driver.find_element_by_id("newsletter-modal-wrapper")).className

pagination = driver.find_elements_by_xpath("//ul[@class='pagination']/li")
numPages = len(pagination)



for x in range(2, numPages+1):
    
    nextPage = "//ul[@class='pagination']/li[" + str(x) + "]/a"
    print(nextPage)
    driver.find_element_by_xpath(nextPage).click()
    time.sleep(2)
    
    html = driver.execute_script("return document.documentElement.outerHTML;")
    soup = BeautifulSoup(html, features="html.parser")
    items = soup.find_all('nycgo-item-card')
    for item in items: 
        event = {}
        event['title'] = item.h4.a.contents[4]
        event['dates'] = item.h4.a.span.string
        
        print(event['title'])
        
        try:
            desc = item.find('div', class_='card-desc').span.p.contents
            event['description'] = ' '.join(str(e) for e in desc)
        except:
            event['description'] = 'None'
            
        duplicate = False
        for d in data['events']:
            if d['name'] == event['title'] and d['description'] == event['description']:
                duplicate = True

        if duplicate == False:
            dates = event['dates'][2:]
            if 'ongoing' in dates:
                start = datetime.datetime.now().strftime('%Y-%m-%d')
            else:
                year = datetime.date.today().year
                if '-' in dates:
                    start = dates.split('-')[0].strip()
                else: 
                    start = dates.strip()
                
                if ',' in start:
                    start = start.replace(',', '')
                else:
                    start = start + ' ' + str(year)
                startDateTime = datetime.datetime.strptime(start, '%b %d %Y')
                startDateTime = startDateTime.strftime('%Y-%m-%d')
               
                if '-' in dates:
                    end = dates.split('-')[1].strip()
                    if ',' in end:
                        end = end.replace(',', '')
                    else:
                        end = end + ' ' + str(year)

                    endDateTime = datetime.datetime.strptime(end, '%b %d %Y')
                    endDateTime = endDateTime.strftime('%Y-%m-%d')
                else: 
                    endDateTime = startDateTime
                    
                    
            data['events'].append({
                'name': event['title'],
                'description': event['description']
            })

            event = {
              'summary': event['title'],
              'description': event['description'],
              'start': {
                'date': startDateTime
              },
              'end': {
                'date': endDateTime
              },
            }

            event = service.events().insert(calendarId='rm7gfttr8tbif0o1qu2vn0mnco@group.calendar.google.com', body=event).execute()

#        quit()
#        time.sleep(2)
        
    
    
with open('data.json', 'w') as outfile:  
    json.dump(data, outfile)
    
driver.close()
