#!/usr/bin/env python
from selenium import webdriver

browser = webdriver.Firefox()
browser.get('http://news.baidu.com')
browser.save_screenshot('screenie.png')
browser.quit()
