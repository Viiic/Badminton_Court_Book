from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from loginfo import loginfo
from loginfo import book_info
from loginfo import name_list
import time
import schedule
import datetime
import argparse

driver_path = "/Users/WeifanWang/workspace/cba_court_reg/chromedriver"
url = "https://clients.mindbodyonline.com/ASP/su1.asp?studioid=217228&tg=&vt=&lvl=&stype=&view=&trn=0&page=&catid=&prodid=&date=3%2f24%2f2022&classid=0&prodGroupId=&sSU=&optForwardingLink=&qParam=&justloggedin=&nLgIn=&pMode=0&loc=1"
court_dict = {11:54, 12:69, 13:56, 14:71, 15:72, 16:73, 17:50, 18:80, 19:83, 20:85}
court_url_base = "https://clients.mindbodyonline.com/asp/appt_con.asp?loc=1&tgid=5&trnid=1000000{}&rtrnid=&date={}/{}/2022&mask=False&STime={}:00:00%20{}&ETime={}:00:00%20{}"

def get_driver():
    #Initialize webdriver object
    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    #Set user agent to avoid being detected headless mode: in headless, it uses 'HeadlessChrome//99.0.4844.83'
    if not args.d:
        options.add_argument('--headless')
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')
    service = Service("/Users/WeifanWang/workspace/cba_court_reg/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def get_url(court, month, date, shour, ehour, start_am_pm, end_am_pm):
    return court_url_base.format(court, month, date, shour, start_am_pm, ehour, end_am_pm)

# For testing use
def customized_set_url(court, month, date, hour24):
    shour         = hour24 if hour24 <= 12 else hour24 % 12
    ehour         = (shour+1) if (shour+1) <= 12 else ((shour+1)%12)
    start_am_pm   = "am" if hour24 < 12 else "pm"
    end_am_pm     = "am" if ((hour24+1)%24) < 12 else "pm"
    court_url1    = get_url(court, month, date, shour, ehour, start_am_pm, end_am_pm)

    shour         = ehour
    ehour         = (shour+1) if (shour+1) <= 12 else ((shour+1)%12)
    start_am_pm   = "am" if ((hour24+1)%24) < 12 else "pm"
    end_am_pm     = "am" if ((hour24+2)%24) < 12 else "pm"
    court_url2    = get_url(court, month, date, shour, ehour, start_am_pm, end_am_pm)
    log("month: {}, date: {}, hour: {}, start_am_pm: {}".format(month, date, hour24, start_am_pm))
    return court_url1, court_url2, hour24

def set_url(court, date=None, hour=None):
    if date is None:
        today         = datetime.datetime.now()
        date_nextweek = today + datetime.timedelta(days=8)
        month         = date_nextweek.strftime("%m")
        day           = date_nextweek.strftime("%d")
    else:
        month         = date.split('/')[0]
        day           = date.split('/')[1]

    hour24        = hour
    hour12        = hour24 % 12
    shour         = hour24 if hour24 <= 12 else hour24 % 12
    ehour         = (shour+1) if (shour+1) <= 12 else ((shour+1)%12)
    start_am_pm   = "am" if hour24 < 12 else "pm"
    end_am_pm     = "am" if ((hour24+1)%24) < 12 else "pm"
    court_url1    = get_url(court, month, day, shour, ehour, start_am_pm, end_am_pm)

    shour         = ehour
    ehour         = (shour+1) if (shour+1) <= 12 else ((shour+1)%12)
    start_am_pm   = "am" if ((hour24+1)%24) < 12 else "pm"
    end_am_pm     = "am" if ((hour24+2)%24) < 12 else "pm"
    court_url2    = get_url(court, month, day, shour, ehour, start_am_pm, end_am_pm)
    log("month: {}, day: {}, hour: {}, start_am_pm: {}".format(month, day, hour12, start_am_pm))
    #log("month: {}, day: {}, week_day: {}, hour: {}, start_am_pm: {}".format(month, day, week_day, hour12, start_am_pm))
    return court_url1, court_url2, hour24

def login():
    log("Starting login")
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "su1UserName")))
    #Step-1: login
    email_field = driver.find_element(By.ID, "su1UserName")
    log("Filling email")
    email_field.send_keys(email)
    password_field = driver.find_element(By.ID, "su1Password")
    log("Filling password")
    password_field.send_keys(password)
    log("login")
    password_field.send_keys(Keys.ENTER)
    
    time.sleep(1)
    #Step-2: click the 'Appointment' tab
    log("Clicking appointment tab")
    appt_field = driver.find_element(By.ID, "tabA9")
    appt_field.click()

def book_court(time):
    log("Starting to booking")

    try:
        checkout = driver.find_element(By.ID, "CheckoutButton")
        
    except Exception as e1:
        #Sometimes, will jump to 'court reservation member' page after clicking 'Book appointment' button
        try:
            court_rsv_member = driver.find_element(By.NAME, "Court Reservation Member ")
            log("Clicking court reservation button")
            court_rsv_member.click()
            checkout = driver.find_element(By.ID, "CheckoutButton")
            log("Clicking checkout button-1")
            checkout.click()
            place_order = driver.find_element(By.ID, "buybtn")
            log("Clicking place order button-2")
            place_order.click()
            
        except Exception as e3:
            log("Didn't find the 'Checkout' button. Check if already booked")

        #Sometimes, directly booking succeed after clicking 'Book appointment' button
        try:
            booked = driver.find_element(By.ID, "notifyBooking")
            log("Find notifybooking. Probably booking succeeded")
        except Exception as e2:
            log("{}: Didn't find the 'check out' button and also the notifying popup window. Probably booking failed".format(datetime.datetime.now().strftime("%Y-%m-%d:%H:%M:%S:%f")))
            log("Save screenshot for debug")
            driver.get_screenshot_as_file("screenshot_{}_{}.png".format(time, name))
            log("Booking failed")
            return
    else:
        log("Clicking checkout button")
        checkout.click()
        place_order = driver.find_element(By.ID, "buybtn")
        log("Clicking place order button")
        place_order.click()
            
    finally:
        log("Booking DONE")

def add_to_cart(court_url):
    log("Starting to add court to cart")
    #Open a new tab
    driver.execute_script("window.open('');")
    #Switch to the new window and open new URL
    driver.switch_to.window(driver.window_handles[1])

    driver.get(court_url)
    #Write down player names int note box
    note_box = driver.find_element(By.NAME, "txtNotes")
    note_box.send_keys(player_names)
    book_appt = driver.find_element(By.ID, "apptBtn")
    log("Clicking book appt button")
    book_appt.click()
    try:
        continue_shop = driver.find_element(By.ID, "ContinueShoppingLink")
    except Exception as e1:
        log ("Didn't find the 'Continue shopping' button. Check if need to choose 'court reservation member")
        #Sometimes, will jump to 'court reservation member' page after clicking 'Book appointment' button
        try:
            court_rsv_member = driver.find_element(By.NAME, "Court Reservation Member ")
            log("Clicking court reservation button")
            court_rsv_member.click()
            continue_shop = driver.find_element(By.ID, "ContinueShoppingLink")
            return   
        except Exception as e3:
            log ("Didn't find the 'Court reservation member' for Continue shopping' button. Check if already booked")
            log("Save screenshot for debug")
            splitted_url = court_url.split(':')
            stime = splitted_url[1].split('=')[-1]
            driver.get_screenshot_as_file("screenshot_{}_{}_1.png".format(stime, name))

        #Sometimes, directly booking succeed after clicking 'Book appointment' button
        try:
            booked = driver.find_element(By.ID, "notifyBooking")
            log("Find notifybooking. Probably booking succeed")
        except Exception as e2:
            log("{}: Didn't find the 'Continue shopping' button and also the notifying popup window. Probably booking failed".format(datetime.datetime.now().strftime("%Y-%m-%d:%H:%M:%S:%f")))
            log("Save screenshot for debug")
            splitted_url = court_url.split(':')
            stime = splitted_url[1].split('=')[-1]
            driver.get_screenshot_as_file("screenshot_{}_{}_2.png".format(stime, name))
            log("Booking failed: {}".foramt(court_url))
            return
    else:
        log("Added")
    finally:
        log("Added Done anyway")

def log(msg):
    ctime = datetime.datetime.now().strftime("%Y-%m-%d:%H:%M:%S:%f")
    print("{}: {}".format(ctime, msg))

def click_appt_tab():
    #This is to avoid some issues when booking the second hour of the court
    log("Clicking appointment tab")
    appt_field = driver.find_element(By.ID, "tabA9")
    appt_field.click()
    time.sleep(1)

parser = argparse.ArgumentParser(description='Process login info')
parser.add_argument('--name', type=str, required=True, help='The last name of the account')
parser.add_argument('--date', type=str,                help='The date and time to book courts.\n\tFormat: <mon>/<day>/<start hour>\n\t start hour is 24h. Auto book 2 hours')
parser.add_argument('--hour', type=int, required=True, help='The start hour to book a court. Must be 24 hour clock.')
parser.add_argument('-d',     action='store_true',     help='Debug mode')
args = parser.parse_args()

name         = args.name
email        = loginfo[name][0]
password     = loginfo[name][1]
court        = book_info[name]
player_names = name_list[name]
timestamp    = "{}:{}".format(args.date, args.hour)

court_url1, court_url2, sched_hour = set_url(court_dict[court], date=args.date, hour=args.hour)
log(court_url1)
log(court_url2)
driver = get_driver()

if not args.d:
    ##schedule the task for first hour
    schedule.every().day.at("23:59:30").do(login)
    schedule.every().day.at("23:59:40").do(add_to_cart, court_url1)
    schedule.every().day.at("23:59:45").do(click_appt_tab)
    schedule.every().day.at("23:59:48").do(add_to_cart, court_url2)
    schedule.every().day.at("00:00:00").do(book_court, timestamp)
else:
    #For test use
    login()
    add_to_cart(court_url1)
    click_appt_tab()
    add_to_cart(court_url2)
    book_court(timestamp)
    exit()

wait_time = schedule.idle_seconds() + 60
log("wait time: %d" % wait_time)
i = 0
log("Starting scheduled task")
while i < wait_time:
    log("Waited for %d seconds" % i)
    schedule.run_pending()
    time.sleep(1)
    i = i+1

log("All DONE")