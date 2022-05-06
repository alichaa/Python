#  This program was written to monitor new investmentes that appear in Open Sea (a side project that i did with a friend)
#  It does the following
# 1.  Open Open sea with certain filter criteria included in the URL
# 2.  Poll every 5 second
# 3.  Compare the old list to the new list to see if any new Sells have came up
# 4.  Grab the picture of the Map and various information needed for my investment friend
# 5.  Copy and paste the information to our What's app group

# Sorry have not had a chance to comment this, comments avaiable upon request




# pip install bs4 helium lxml requests selenium webdriver-manager

# Improved Finding Items feature.
# Fixed some bugs.
# Added the ability to no crush when there's a video instead of an image in the URL.
# Added Showing the old & new lists one bellow the other for Proof-Of-Working of the script.
# Improved finding PATH/Directory feature with a new command.
# Removed not-usable & ignored functions.
# Removed unused libraries

import os
import shutil
import requests
import pathlib
from datetime import datetime

from bs4 import BeautifulSoup as bs
from helium import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

DIR = str(pathlib.Path(__file__).parent.resolve()).replace('\\', '/') + '/'
web_site = 'https://opensea.io/collection/decentraland?tab=activity&search[isSingleCollection]=true&search[eventTypes][0]=AUCTION_CREATED'
#web_site =   'https://opensea.io/activity?search[eventTypes][0]=AUCTION_CREATED' # test site for faster results
group = 'Crypto Land Production'
#group = 'Test Group'
DEBUG = False


def extract(driver):
    source_code = driver.page_source
    main_page_soup = bs(source_code, 'lxml')
    return main_page_soup

def open_browser(DIR):
    options = Options()
    options.add_argument(f"user-data-dir={DIR}/Whatsapp_messages_sender_profile")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    set_driver(driver)
    return driver

def setup_tabs(driver):
    main_tab = driver.window_handles[0]
    new_tab_opening = driver.execute_script("window.open('');") ; image_download_tab = driver.window_handles[1]
    new_tab_opening = driver.execute_script("window.open('');") ; whatsapp_tab = driver.window_handles[2]
    return main_tab, image_download_tab, whatsapp_tab

def transform(new_list_raw, new_list):
    for item in new_list_raw:
        try: # Extract the info in each row
            name = str(item.find(class_='Blockreact__Block-sc-1xf18x6-0 dBFmez AssetCell--link').text)
            URL = str('https://opensea.io' + item.find(class_='Blockreact__Block-sc-1xf18x6-0 dBFmez AssetCell--link')['href'])
            price = f"{str(item.find_all(class_='Blockreact__Block-sc-1xf18x6-0 ijONnj')[0].img['alt'])} {str(item.find_all(class_='Blockreact__Block-sc-1xf18x6-0 ijONnj')[0].text)} - {str(item.find_all(class_='Blockreact__Block-sc-1xf18x6-0 ijONnj')[1].text)}"
            time = str(item.find(class_='Blockreact__Block-sc-1xf18x6-0 EventTimestamp__DivContainer-sc-3gbwf4-0 ftsyBg fgvBUA').text)
            if 'hour' in time: pass
            else:
                #print(f'{name} | {price} | {time}')
                new_list.append(str(f'{name} | {price} | {URL} | {time}')) # Add to list
        except:
            pass
    return new_list[::-1]

driver = open_browser(DIR)
main_tab, image_download_tab, whatsapp_tab = setup_tabs(driver)

# Open WhatsApp
driver.switch_to.window(whatsapp_tab) ; go_to('https://web.whatsapp.com/')

#while True and not Debug: # Check if it's the first time
if Text('To use WhatsApp on your computer:').exists() and not DEBUG:
    wait_until(Text('To use WhatsApp on your computer:').exists, interval_secs=0.1, timeout_secs=120)
    wait_until(lambda: not Text('To use WhatsApp on your computer:').exists(), interval_secs=0.1, timeout_secs=999)
    wait_until(Text(group).exists, interval_secs=0.1, timeout_secs=120) ; click(Text(group)) # Select the right conversation
#else: pass
#break



driver.switch_to.window(main_tab) ; go_to(web_site)
driver.execute_script("document.body.style.zoom = '0.5'") #Zoom out to capture lot of items

old_list = []
count = 0
printed = False

while True:
    if Text('Error 504').exists():
        refresh() ; scroll_down(700)

    new_list_raw = [] ; new_list = []; old_list_edited = [] ; new_list_edited = [] ; old_list_print = [] ; new_list_print = [] 

    # Get the items
    main_page_soup = extract(driver) ; new_list_raw = main_page_soup.find_all('div', role='listitem')
    new_list = transform(new_list_raw, new_list)

    #if count >= 1 and printed == False:
    #    for new in new_list: new_list_edited.append('|'.join(new_list.split('|')[:-1]))
    #    for i in new_list_edited: print(i)
    #    printed = True
    
    # Record current items for the first time
    if old_list == []:
        old_list = new_list.copy()
        for old in old_list: old_list_edited.append('|'.join(old.split('|')[:-1]))
        now = datetime.now()
        if  old_list == []:
            pass
        else:
            current_time = now.strftime("%H:%M:%S")
            print('')
            print("Current Time =", current_time)
            print('------------------------------')
            for i in old_list: 
               print( "|".join(i.split("|")[:2]) + "|" + i.split("|")[-1] ) # Eliminate URL
    else: # Compare if there's new items

        for old in old_list:
           old_list_edited.append('|'.join(old.split('|')[:-1]))
        for new in new_list:
           new_list_edited.append('|'.join(new.split('|')[:-1]))

        
        printed = False
        for i,new in enumerate(new_list_edited):
            if new not in old_list_edited: ## If there's new items, Send in WhatsApp
                temp_new = new.split('|')[:-1]
                #print(f'========== [+++] Sending {temp_new} ... ============')
                
                if not printed:
                    print(f'OLD :') # OLD
                    for item in old_list:  print( "|".join(item.split("|")[:2]) + "|" + item.split("|")[-1] ) # Eliminate URL
                    printed = True
                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    print(f'\nNEW :', current_time) # NEW

 
                print( "|".join(new_list[i].split("|")[:2]) + "|" + new_list[i].split("|")[-1] ) 
                #for i in new_list_edited:
                #    now = datetime.now()
                #    current_time = now.strftime("%H:%M:%S")
                #    #print("Current Time =", current_time)
                #    print('|'.join(i.split('|')[:-1]) + ' | ' + current_time)
                
                driver.switch_to.window(whatsapp_tab) # Look for the group & Send
                message = str(f"{new}| {new_list[new_list_edited.index(new)].split('|')[-1]}")
                #write(message) ; press(ENTER) # Send data
                #write(message, into='type a message') ; press(ENTER)
                try:
                    #if DEBUG: break
                    write(message, into='type a message') ; press(ENTER)
                    sleep(1)
                except Exception as e: print(f'[***********] Error occured ************************************************* - {e}')

                # Get the image & send it
                try:
                    if DEBUG: break
                    driver.switch_to.window(image_download_tab)
                    go_to(new.split('|')[-1])
                    source_code = driver.page_source
                    SOUP = bs(source_code, 'lxml')
                    image_url = SOUP.find(class_='Image--image')['src']
                    response = requests.get(image_url, stream=True)
                    img_path = f'{DIR}/img.png'
                    with open(img_path, 'wb') as out_file: shutil.copyfileobj(response.raw, out_file)
                    del response
                    driver.switch_to.window(whatsapp_tab)
                    wait_until(Text(group).exists, interval_secs=0.1, timeout_secs=120) ; click(Text(group)) # Select the right conversation
                    sleep(1)
                    click(S('._2jitM'))
                    input_img = driver.find_element_by_tag_name('input').send_keys(img_path)
                    click(S('._165_h._2HL9j')) # Button that looks like envolope (telegram icon - sending icon)
                    #sleep(1)
                    #os.remove(img_path) # Remove the downloaded image from the directory
                except:
                    pass

                driver.switch_to.window(main_tab)

    # Make the old results list looks like the new one
    old_list = new_list.copy()
    
    # Wait for 5 seconds
    #print('\n[...] Waiting 1 sec...\n')
    sleep(1)
    count += 1
