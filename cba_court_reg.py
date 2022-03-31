from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import schedule
import datetime

driver_path = "/Users/WeifanWang/workspace/cba_court_reg/chromedriver"
url = "https://clients.mindbodyonline.com/ASP/su1.asp?studioid=217228&tg=&vt=&lvl=&stype=&view=&trn=0&page=&catid=&prodid=&date=3%2f24%2f2022&classid=0&prodGroupId=&sSU=&optForwardingLink=&qParam=&justloggedin=&nLgIn=&pMode=0&loc=1"
court_dict = {11:54, 12:69, 13:56, 14:71, 15:72, 16:73, 17:50, 18:80, 19:83, 20:85}
court_url_base = "https://clients.mindbodyonline.com/asp/appt_con.asp?loc=1&tgid=5&trnid=1000000{}&rtrnid=&date={}/{}/2022&mask=False&STime={}:00:00%20{}&ETime={}:00:00%20{}"
email = "vic957b@163.com"
password = "weifan12345"
email_he = "ruxiaoyi666@gmail.com"
password_he = "Heyuguang@123"

def get_driver():
    #Initialize webdriver object
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--window-size=1920,1080')
    #Set user agent to avoid being detected headless mode: in headless, it uses 'HeadlessChrome//99.0.4844.83'
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    #driver = webdriver.Chrome(options=options, executable_path=driver_path)
    service = Service("/Users/WeifanWang/workspace/cba_court_reg/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    #driver = webdriver.Chrome(executable_path = driver_path)
    return driver

def get_url(court, month, date, shour, ehour, start_am_pm, end_am_pm):
    return court_url_base.format(court, month, date, shour, start_am_pm, ehour, end_am_pm)


def customized_set_url(court, month, date, hour24):
    shour         = hour24 if hour24 <= 12 else hour24 % 12
    ehour         = (shour+1) if (shour+1) <= 12 else ((shour+1)%12)
    start_am_pm   = "am" if hour24 < 12 else "pm"
    end_am_pm     = "am" if ((hour24+1)%24) < 12 else "pm"
    court_url1    = get_url(court, month, date, shour, ehour, start_am_pm, end_am_pm)
    #court_url1 = court_url_base.format(court, month, date, hour24%24, start_am_pm, (hour24+1)%24, end_am_pm)

    shour         = ehour
    ehour         = (shour+1) if (shour+1) <= 12 else ((shour+1)%12)
    start_am_pm   = "am" if ((hour24+1)%24) < 12 else "pm"
    end_am_pm     = "am" if ((hour24+2)%24) < 12 else "pm"
    court_url2    = get_url(court, month, date, shour, ehour, start_am_pm, end_am_pm)
    #court_url2 = court_url_base.format(court, month, date, (hour24+1)%24, start_am_pm, (hour24+2)%24, end_am_pm)
    print("month: {}, date: {}, hour: {}, start_am_pm: {}".format(month, date, hour24, start_am_pm))
    return court_url1, court_url2, hour24

def set_url(court):
    #today = datetime.datetime(2022, 4, 3)
    today         = datetime.datetime.now()
    date_nextweek = today + datetime.timedelta(days=7)
    month         = date_nextweek.strftime("%m")
    date          = date_nextweek.strftime("%d")
    week_day      = (int)(today.strftime("%w"))
    # book courts of 8pm during Monday to Friday; otherwise 10am
    hour24        = 20 if 0 < week_day and week_day < 6 else 10
    hour12        = hour24 % 12
    #hour = 10

    shour         = hour24 if hour24 <= 12 else hour24 % 12
    ehour         = (shour+1) if (shour+1) <= 12 else ((shour+1)%12)
    start_am_pm   = "am" if hour24 < 12 else "pm"
    end_am_pm     = "am" if ((hour24+1)%24) < 12 else "pm"
    court_url1    = get_url(court, month, date, shour, ehour, start_am_pm, end_am_pm)
    #start_am_pm   = "am" if hour24 < 12 else "pm"
    #end_am_pm     = "am" if ((hour24+1)%24) < 12 else "pm"
    #court_url1 = court_url_base.format(court, month, date, hour24%24, start_am_pm, (hour24+1)%24, end_am_pm)
    #court_url1 = court_url_base.format(court, month, date, hour12, start_am_pm, hour12+1, end_am_pm)

    shour         = ehour
    ehour         = (shour+1) if (shour+1) <= 12 else ((shour+1)%12)
    start_am_pm   = "am" if ((hour24+1)%24) < 12 else "pm"
    end_am_pm     = "am" if ((hour24+2)%24) < 12 else "pm"
    court_url2    = get_url(court, month, date, shour, ehour, start_am_pm, end_am_pm)
    #start_am_pm   = "am" if ((hour24+1)%24) < 12 else "pm"
    #end_am_pm     = "am" if ((hour24+2)%24) < 12 else "pm"
    #court_url2 = court_url_base.format(court, month, date, hour12+1, start_am_pm, hour12+2, end_am_pm)
    #court_url2 = court_url_base.format(court, month, date, (hour24+1)%24, start_am_pm, (hour24+2)%24, end_am_pm)
    print("month: {}, date: {}, week_day: {}, hour: {}, start_am_pm: {}".format(month, date, week_day, hour12, start_am_pm))
    return court_url1, court_url2, hour24

def login():
    print("Starting login")
    print(datetime.datetime.now().strftime("%Y-%m-%d:%H:%M:%S:%f"))
    driver.get(url)
    print(datetime.datetime.now().strftime("%Y-%m-%d:%H:%M:%S:%f"))
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "su1UserName")))
    #Step-1: login
    #email_field = WebDriverWait(driver, 10).until(lambda x: x.find_element(By.ID, "su1UserName"))
    email_field = driver.find_element(By.ID, "su1UserName")
    print("Filling email")
    email_field.send_keys(email)
    password_field = driver.find_element(By.ID, "su1Password")
    print("Filling password")
    password_field.send_keys(password)
    print("login")
    password_field.send_keys(Keys.ENTER)
    
    time.sleep(1)
    #Step-2: click the 'Appointment' tab
    print("Clicking appointment tab")
    appt_field = driver.find_element(By.ID, "tabA9")
    appt_field.click()

def book_court(court_url):
    try:
        #time.sleep(0.2)
        #print("Switching to booking page")
        driver.get(court_url)
        book_appt = driver.find_element(By.ID, "apptBtn")
        #time.sleep(0.2)
        #print("Clicking book appt button")
        book_appt.click()
        driver.get_screenshot_as_file("screenshot1.png")
        checkout = driver.find_element(By.ID, "CheckoutButton")
        #time.sleep(0.2)
        #print("Clicking checkout button")
        checkout.click()
        driver.get_screenshot_as_file("screenshot2.png")
        place_order = driver.find_element(By.ID, "buybtn")
        #time.sleep(0.2)
        #print("Clicking place order button")
        place_order.click()
    except Exception as e:
        print("Failed to book. Here's the link:{}".format(court_url))
        print(e)
    finally:
        print(datetime.datetime.now().strftime("%Y-%m-%d:%H:%M:%S:%f"))
        splitted_url = court_url.split(':')
        stime = splitted_url[1].split('=')[-1]
        etime = splitted_url[3].split('=')[-1]
        driver.get_screenshot_as_file("screenshot_{}_{}.png".format(stime, etime))
        #Open a new tab
        driver.execute_script("window.open('');")
        #Switch to the new window and open new URL
        driver.switch_to.window(driver.window_handles[1])

driver = get_driver()

#assemble the booking url for specific court and time
court = 17
#court_url1 is for the first hour, court_url2 is for the second hour
court_url1, court_url2, sched_hour = set_url(court_dict[court])
#court_url1, court_url2, sched_hour = customized_set_url(court_dict[17], '03', '30', 21)
#print(court_url1)
#print(court_url2)
#court_url1, court_url2, sched_hour = customized_set_url(court_dict[17], '03', '30', 22)
#print(court_url1)
#print(court_url2)
#court_url1, court_url2, sched_hour = customized_set_url(court_dict[17], '03', '30', 23)
#print(court_url1)
#print(court_url2)
#court_url1, court_url2, sched_hour = customized_set_url(court_dict[17], '03', '30', 24)
#print(court_url1)
#print(court_url2)
#exit()

##schedule the task for first hour
sched_time1 = "0{}:59:30" if sched_hour < 10 else "{}:59:30"
sched_time2 = "0{}:00:00" if sched_hour < 10 else "{}:00:00"
#print(sched_time1.format(sched_hour-1))
schedule.every().day.at(sched_time1.format(sched_hour-1)).do(login)
schedule.every().day.at(sched_time2.format(sched_hour)).do(book_court, court_url1)
#
##schedule the task for second hour
schedule.every().day.at(sched_time1.format(sched_hour)).do(login)
schedule.every().day.at(sched_time2.format(sched_hour+1)).do(book_court, court_url2)

#schedule.every().day.do(login)
#schedule.every().day.do(book_court, court_url1)
#schedule.every().day.at("12:09:20").do(book_court, court_url2)
#schedule.run_all()
#exit()

wait_time = schedule.idle_seconds() + 3700
print("Will execute the task within %d seconds" % wait_time)
i = 0
while i < wait_time:
    print("Waited for %d seconds" % i)
    schedule.run_pending()
    time.sleep(1)
    i = i+1

#driver.quit()
