from selenium                          import webdriver
from selenium.webdriver.common.keys    import Keys
from selenium.webdriver.common.by      import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver                import ActionChains
from selenium.webdriver.support.wait   import WebDriverWait
from selenium.webdriver.support        import expected_conditions as EC
from webdriver_manager.chrome          import ChromeDriverManager
from booking_info                      import loginfo
from booking_info                      import book_info
from booking_info                      import name_list
from logger                            import get_logger
import time
import schedule
import datetime
import argparse

driver_path = "/Users/WeifanWang/workspace/Badminton_Court_Book/chromedriver"
url = "https://clients.mindbodyonline.com/ASP/su1.asp?studioid=217228&tg=&vt=&lvl=&stype=&view=&trn=0&page=&catid=&prodid=&date=3%2f24%2f2022&classid=0&prodGroupId=&sSU=&optForwardingLink=&qParam=&justloggedin=&nLgIn=&pMode=0&loc=1"
court_dict = {11:54, 12:69, 13:56, 14:71, 15:72, 16:73, 17:50, 18:80, 19:83, 20:85}
court_url_base = "https://clients.mindbodyonline.com/asp/appt_con.asp?loc=1&tgid=5&trnid=1000000{}&rtrnid=&date={}/{}/2022&mask=False&STime={}:00:00%20{}&ETime={}:00:00%20{}"
shopping_cart_url = "https://clients.mindbodyonline.com/asp/main_shop.asp?stype=3&pMode=4&reSchedule=&origId=&recType=&recNum="
schedule_url = "https://clients.mindbodyonline.com/ASP/my_sch.asp"

idx          = 0                 # idx for screenshot
res          = False             # Result of adding court to the cart

def get_driver():
    #Initialize webdriver object
    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    #Set user agent to avoid being detected headless mode: in headless, it uses 'HeadlessChrome//99.0.4844.83'
    if not args.d:
        options.add_argument('--headless')
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')

    service = Service(driver_path)
    #service = Service("/Users/WeifanWang/workspace/cba_court_reg/chromedriver")
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
    logger.info("month: {}, date: {}, hour: {}, start_am_pm: {}".format(month, date, hour24, start_am_pm))
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
    logger.info("month: {}, day: {}, hour: {}, start_am_pm: {}".format(month, day, hour12, start_am_pm))
    #logger.info("month: {}, day: {}, week_day: {}, hour: {}, start_am_pm: {}".format(month, day, week_day, hour12, start_am_pm))
    return court_url1, court_url2, hour24

def login():
    logger.info("Starting login")
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "su1UserName")))
    #Step-1: login
    email_field = driver.find_element(By.ID, "su1UserName")
    logger.info("Filling email")
    email_field.send_keys(email)
    password_field = driver.find_element(By.ID, "su1Password")
    logger.info("Filling password")
    password_field.send_keys(password)
    logger.info("login")
    password_field.send_keys(Keys.ENTER)
    
    time.sleep(1)
    #Step-2: click the 'Appointment' tab
    logger.info("Clicking appointment tab")
    appt_field = driver.find_element(By.ID, "tabA9")
    appt_field.click()

def prepare_for_booking(stime):
    logger.info("Prepare for placing the booking order")

    try:
        #If adding court failed, go the shopping cart and try to submit the order
        driver.get(shopping_cart_url)
        checkout = driver.find_element(By.ID, "CheckoutButton")
    except Exception as e1:
        logger.info("Something wrong. Probably nothing in the cart Saving screenshot")
        save_screenshot("empty_cart_{}_{}".format(name, args.hour))
    else:
        logger.info("Screenshot the shopping cart")
        save_screenshot("cart_{}_{}".format(name, args.hour))
        logger.info("Clicking checkout button")
        checkout.click()
        time.sleep(0.2)
        logger.info("Preparation DONE")

def submit_booking(stime):
    #Start at 00:00:00.05 to avoid the attention of the CBA boss
    time.sleep(0.5)

    try:
        place_order = driver.find_element(By.ID, "buybtn")
        logger.info("Clicking place order button")
        place_order.click()
    except Exception as e:
        logger.info("Placing order failed")
        save_screenshot("place_order_except_{}_{}".format(name, args.hour))
        logger.info("Booking failed")
    else:
        time.sleep(5)
        save_screenshot("book_done_{}_{}".format(name, args.hour))
        logger.info("Booking DONE")

def add_to_cart(court_url):
    global idx
    global res
    logger.info("Starting to add court to cart")
    #Open a new tab
    driver.execute_script("window.open('');")
    #Switch to the new window and open new URL
    driver.switch_to.window(driver.window_handles[1])

    driver.get(court_url)
    #Write down player names int note box
    try:
        note_box = driver.find_element(By.NAME, "txtNotes")
    except:
        logger.info("Didn't get into the right page to fill the names")
        save_screenshot("no_text_box_{}_{}_{}".format(name, args.hour, idx))
        return

    note_box.send_keys(player_names)
    book_appt = driver.find_element(By.ID, "apptBtn")
    logger.info("Clicking book appt button")
    book_appt.click()
    try:
        continue_shop = driver.find_element(By.ID, "ContinueShoppingLink")
    except Exception as e1:
        logger.info ("Didn't find the 'Continue shopping' button. Check if need to choose 'court reservation member")
        #Sometimes, will jump to 'court reservation member' page after clicking 'Book appointment' button
        try:
            court_rsv_member = driver.find_element(By.NAME, "Court Reservation Member ")
            logger.info("Clicking court reservation button")
            court_rsv_member.click()
            continue_shop = driver.find_element(By.ID, "ContinueShoppingLink")
            logger.info("Retrying to add courts succeeded!")
            res = True
            return
        except Exception as e3:
            logger.info ("Didn't find the 'Court reservation member' for Continue shopping' button. Check if already booked")
            save_screenshot("crt_rsv_{}_{}_{}".format(name, args.hour, idx))

        #Sometimes, directly booking succeed after clicking 'Book appointment' button
        try:
            booked = driver.find_element(By.ID, "notifyBooking")
            logger.info("Find notifybooking. Probably booking succeed")
            return
        except Exception as e2:
            logger.info("Didn't find the 'Continue shopping' button and also the notifying popup window. Probably booking failed".format(datetime.datetime.now().strftime("%Y-%m-%d:%H:%M:%S:%f")))
            save_screenshot("no_notice_{}_{}_{}".format(name, args.hour, idx))
            logger.info("Adding court failed: {}".format(court_url))
    else:
        logger.info("Adding courts succeeded!")
        res = True
    finally:
        idx += 1
        logger.info("Adding Done")

def get_court_list_screenshot():
    driver.get(schedule_url)
    save_screenshot("court_list_{}".format(name))

def save_screenshot(filename):
    logger.info("Save screenshot for debug")
    driver.get_screenshot_as_file("screenshot_{}.png".format(filename))
    logger.info("Saving screenshot DONE")

def log(msg):
    ctime = datetime.datetime.now().strftime("%Y-%m-%d:%H:%M:%S:%f")
    print("{}: {}".format(ctime, msg))

def click_appt_tab():
    #TODO: refreash the page before clicking the tab since sometimes the tab is not clickable, e.g. hit the CAPTCH
    driver.navigate().refresh();
    #This is to avoid some issues when booking the second hour of the court
    logger.info("Clicking appointment tab")
    appt_field = driver.find_element(By.ID, "tabA9")
    appt_field.click()
    time.sleep(1)

def reset_result():
    res = False

parser = argparse.ArgumentParser(description='Process login info')
parser.add_argument('--name', type=str, required=True, help='The last name of the account')
parser.add_argument('--date', type=str,                help='The date and time to book courts.\n\tFormat: <mon>/<day>\n')
parser.add_argument('--hour', type=int, required=True, help='The start hour to book a court. Must be 24 hour clock.')
parser.add_argument('-d',     action='store_true',     help='Debug mode')
args = parser.parse_args()

name         = args.name
email        = loginfo[name][0]
password     = loginfo[name][1]
court        = book_info[name]
player_names = name_list[name]
timestamp    = "{}:{}".format(args.date, args.hour)
logger       = get_logger(__name__, "debug_log_{}.txt".format(name))

pre_court_url, _, _ = set_url(court_dict[court], date="5/10", hour=16)
logger.info(pre_court_url)

court_url1, court_url2, sched_hour = set_url(court_dict[court], date=args.date, hour=args.hour)
logger.info(court_url1)
logger.info(court_url2)
driver = get_driver()

#if args.d:
if not args.d:
    sched_time_1 = "23:58:{}"
    sched_time_2 = "00:00:{}"
    #sched_time_1 = "09:29:{}"
    #sched_time_2 = "09:30:{}"
    ##schedule the task for first hour
    # Booking any court in advance
    schedule.every().day.at(sched_time_1.format("00")).do(login)
    schedule.every().day.at(sched_time_1.format("10")).do(add_to_cart, pre_court_url)
    schedule.every().day.at(sched_time_1.format("15")).do(prepare_for_booking, timestamp)
    schedule.every().day.at(sched_time_1.format("20")).do(submit_booking, timestamp)
    schedule.every().day.at(sched_time_1.format("30")).do(reset_result)
    schedule.every().day.at(sched_time_1.format("31")).do(click_appt_tab)

    #Booking the courts
    schedule.every().day.at(sched_time_2.format("00")).do(add_to_cart, court_url1)
    schedule.every().day.at(sched_time_2.format("01")).do(click_appt_tab)
    schedule.every().day.at(sched_time_2.format("02")).do(add_to_cart, court_url2)
    schedule.every().day.at(sched_time_2.format("03")).do(prepare_for_booking, timestamp)
    schedule.every().day.at(sched_time_2.format("04")).do(submit_booking, timestamp)
else:
    #For test use
    login()
    add_to_cart(pre_court_url)
    prepare_for_booking(timestamp)
    submit_booking(timestamp)

    reset_result()
    click_appt_tab()
    add_to_cart(court_url1)
    click_appt_tab()
    #add_to_cart(court_url2)

    if res:
        prepare_for_booking(timestamp)
        submit_booking(timestamp)

    get_court_list_screenshot()
    exit()

wait_time = schedule.idle_seconds() + 60
logger.info("wait time: %d" % wait_time)
i = 0
logger.info("Starting scheduled task")
while i < wait_time:
    logger.info("Waited for %d seconds" % i)
    schedule.run_pending()
    time.sleep(1)
    i = i+1

get_court_list_screenshot()
logger.info("All DONE")
driver.quit()