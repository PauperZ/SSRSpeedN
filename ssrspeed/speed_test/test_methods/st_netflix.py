import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging

logger = logging.getLogger("Sub")

LOCAL_PORT = 1080

def setProxyPort(port):
    global LOCAL_PORT
    LOCAL_PORT = port

def speedTestNetflix(port):
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:%d" % port)
        driver = webdriver.Chrome(executable_path="./drivers/chromedriver.exe", options=chrome_options)
        driver.get('https://fast.com/')

        MaxSpeed = 0
        TOTAL_RECEIVED = 0
        SpeedList = []
        for i in range(0,60):
            time.sleep(0.5)
            CurrentSpeed = 0
            CurrentSpeed = float(driver.find_element_by_class_name("speed-results-container").text)
            unit = driver.find_element_by_class_name("speed-units-container").text
            SpeedList.append(CurrentSpeed * 128 * 1024)
            if (unit == 'Kbps'):
                CurrentSpeed = CurrentSpeed / 1024
            if (unit == 'Gbps'):
                CurrentSpeed = CurrentSpeed * 1024
            if(CurrentSpeed > MaxSpeed):
                MaxSpeed = CurrentSpeed
            TOTAL_RECEIVED += CurrentSpeed * 128 * 1024
            print("\r[" + "=" * i + "> CurrentInternetSpeed: [%.2f MB/s]" % (CurrentSpeed / 8), end='')
            done = len(driver.find_element_by_id("your-speed-message").text)
            if done:
                break

        logger.info("\nNetflix test: EndSpeed {:.2f} MB/s, MaxSpeed {:.2f} MB/s.".format(CurrentSpeed / 8, MaxSpeed / 8 ))
        driver.close()
        os.system('taskkill /im chromedriver.exe /F')
        return (CurrentSpeed * 128 * 1024, MaxSpeed * 128 * 1024, SpeedList, TOTAL_RECEIVED)


    except Exception as e:
        driver.close()
        os.system('taskkill /im chromedriver.exe /F')
        logger.error('Netflix speedtest ERROR ：Re-test node ' + str(e.args))
        return (0, 0, [], 0)
