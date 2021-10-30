import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import logging

logger = logging.getLogger("Sub")

from config import config

#VIDEO_QUALITY = config["Youtube"]["Quality"]
LOCAL_PORT = 1080

def setProxyPort(port):
	global LOCAL_PORT
	LOCAL_PORT = port

def speedTestYtb(port):
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:%d" % port)
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36")
        driver = webdriver.Chrome(executable_path="./drivers/chromedriver.exe",options=chrome_options)
        driver.set_window_size(3840, 2160)
        driver.get('https://www.youtube.com/watch?v=mkggXE5e2yk&list=RDCMUCve7_yAZHFNipzeAGBI5t9g')
        driver.find_element_by_class_name("ytp-large-play-button").click()
        driver.find_element_by_class_name("ytp-fullscreen-button").click()
        driver.find_element_by_class_name("ytp-settings-button").click()
        driver.find_elements_by_class_name("ytp-menuitem-label")[2].click()
        #print(driver.page_source)
        p = driver.find_element_by_class_name("ytp-settings-button")
        print(driver.get_window_position())
        print(driver.get_window_size())
        print(driver.get_window_rect())
        time.sleep(0.5)
        logger.info("Youtube view quality : " + driver.find_elements_by_class_name("ytp-menuitem-label")[0].text)
        driver.find_elements_by_class_name("ytp-menuitem-label")[0].click()
        t = driver.find_element_by_class_name("html5-main-video")
        ActionChains(driver).context_click(t).perform()
        time.sleep(0.5)
        driver.find_elements_by_class_name("ytp-menuitem-label")[9].click()
        #driver.find_element_by_xpath("//div[contains(text(),'详细统计信息')]").click()
        '''t = driver.find_element_by_class_name("ytp-scrubber-container")
        ac = ActionChains(driver)
        ac.click_and_hold(t)
        ac.move_by_offset(300, 0)
        ac.release()
        ac.perform()'''
        logger.info("Youtube view frame : " + driver.find_element_by_xpath("//span[contains(text(),'@60')]").text)
        MaxSpeed = 0
        TOTAL_RECEIVED = 0
        SpeedList = []
        for i in range(0,20):
            time.sleep(1)
            s1 = driver.find_element_by_xpath("//*[contains(text(),'Kbps')]").text
            CurrentSpeed = int(s1[0:s1.find(' ')])
            TOTAL_RECEIVED += CurrentSpeed * 128
            SpeedList.append(CurrentSpeed * 128)
            if not i:
                StSpeed = CurrentSpeed
            if(CurrentSpeed > MaxSpeed):
                MaxSpeed = CurrentSpeed
            print("\r[" + "=" * i + "> [%d%%/100%%] [%.2f MB/s]" % (int(i * 5 + 5), CurrentSpeed / 8 / 1024), end='')

        driver.close()
        os.system('taskkill /im chromedriver.exe /F')
        logger.info("\nYoutube test: StartSpeed {:.2f} MB/s, MaxSpeed {:.2f} MB/s.".format(StSpeed / 1024 / 8, MaxSpeed / 8 / 1024))
        return (StSpeed * 128, MaxSpeed * 128, SpeedList, TOTAL_RECEIVED)


    except Exception as e:
        driver.close()
        os.system('taskkill /im chromedriver.exe /F')
        logger.error('Youtube test ERROR ：Re-testing node. ' + str(e.args))
        return (0, 0, [], 0)