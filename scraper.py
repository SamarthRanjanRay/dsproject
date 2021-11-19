from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
from itertools import compress
import time
from argparse import ArgumentParser
import os

def build_parser():
    parser = ArgumentParser()
    parser.add_argument('--dir',
            dest='dir', help='Working Directory',
            metavar='CONTENT', required=True)
    parser.add_argument('--driver',
            dest='driver', help='Chrome Driver Path',
            metavar='DRIVER', required=True)
    parser.add_argument('--output',
            dest='output', help='output Folder',
            metavar='OUTPUT', required=True)
    parser.add_argument('--p',
        dest='param', help='Parameters to obtain',nargs = '+',
        metavar='PARAM', required=True)
    parser.add_argument('--sdate',
        dest='sdate', help='Starting Date',
        metavar='SDATE', required=True)
    parser.add_argument('--edate',
        dest='edate', help='Ending Date',
        metavar='EDATE', required=True)
    parser.add_argument('--duration',
        dest='duration', help='Duration',nargs = '+',
        metavar='DURATION', required=True)
    return parser


def getCities():
    browser = webdriver.Chrome(executable_path="{}".format(chdriverpath), chrome_options=option)
    browser.get(url)
    timeout = 20
    try:
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME,"toggle")))
    except TimeoutException:
        print("Timed out waiting for page to load")
        browser.quit()
    time.sleep(1)
    browser.find_elements_by_class_name("toggle")[0].click()
    states = [elem.text for elem in browser.find_element_by_tag_name('ul').find_elements_by_tag_name('li')]
    d = {'StateName':[],'CityName':[]}
    data = pd.DataFrame(d)
    browser.find_elements_by_class_name("toggle")[0].click()
    for state in states:
        browser.find_elements_by_class_name("toggle")[0].click()
        browser.find_element_by_tag_name("input").send_keys(state)
        browser.find_element_by_class_name("options").click()
        browser.find_elements_by_class_name("toggle")[1].click()
        city = [elem.text for elem in browser.find_element_by_tag_name('ul').find_elements_by_tag_name('li')]
        for c in city:
            data = data.append({'StateName':state,'CityName':c},ignore_index = True)
        time.sleep(1)
    browser.quit()
    return data

def getStations(ddlState, ddlCity):
    browser = webdriver.Chrome(executable_path="{}".format(chdriverpath), chrome_options=option)
    browser.get(url)
    timeout = 20
    try:
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME,"toggle")))
    except TimeoutException:
        print("Timed out waiting for page to load")
        browser.quit()
    browser.find_elements_by_class_name("toggle")[0].click()
    browser.find_element_by_tag_name("input").send_keys(ddlState)
    browser.find_element_by_class_name("options").click()
    browser.find_elements_by_class_name("toggle")[1].click()
    browser.find_element_by_tag_name("input").send_keys(ddlCity)
    browser.find_element_by_class_name("options").click()
    browser.find_elements_by_class_name("toggle")[2].click()
    content = browser.page_source.encode('utf-8').strip()
    soup = BeautifulSoup(content,"html.parser")
    st = soup.find_all("div",{"class":"options"})
    st = st[0].text.split('\n')
    b = [bool(re.search(r"\w",x)) for x in st]
    st = list(compress(st,b))
    st = [x.strip() for x in st]
    browser.quit()
    return st

def parameters(br,param):
    br.find_element_by_class_name("list-filter").find_element_by_tag_name("input").send_keys(param)
    br.find_elements_by_class_name("pure-checkbox")[1].click()
    br.find_element_by_class_name("list-filter").find_element_by_tag_name("input").clear()

def getData(state, city, param,startdate,enddate,duration):
    stations = getStations(state,city)
    sd = datetime.strptime(startdate,"%d-%m-%Y")
    sd = sd.strftime("%d-%b-%Y").split("-")
    ed = datetime.strptime(enddate,"%d-%m-%Y")
    ed = ed.strftime("%d-%b-%Y").split("-")
    soups = []
    for station in stations:
        try:
            browser = webdriver.Chrome(executable_path="{}".format(chdriverpath), chrome_options=option)
            browser.get(url)
            timeout = 20
            try:
                WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME,"toggle")))
            except TimeoutException:
                print("Timed out waiting for page to load")
                browser.quit()
            browser.find_elements_by_class_name("toggle")[0].click()
            browser.find_element_by_tag_name("input").send_keys(state)
            browser.find_element_by_class_name("options").click()
            browser.find_elements_by_class_name("toggle")[1].click()
            browser.find_element_by_tag_name("input").send_keys(city)
            browser.find_element_by_class_name("options").click()
            browser.find_elements_by_class_name("toggle")[2].click()
            browser.find_element_by_tag_name("input").send_keys(station)
            browser.find_element_by_class_name("options").click()
            browser.find_elements_by_class_name("toggle")[4].click()
            browser.find_element_by_class_name("filter").find_element_by_tag_name("input").send_keys(duration)
            browser.find_element_by_class_name("options").click()
            browser.find_element_by_class_name("c-btn").click()
            for p in param:
                try:
                    parameters(browser,p)
                except:
                    browser.find_element_by_class_name("list-filter").find_element_by_tag_name("input").clear()
                    pass
            browser.find_element_by_class_name("wc-date-container").click()
            browser.find_element_by_class_name("month-year").click()
            browser.find_element_by_id("{}".format(sd[1].upper())).click()
            browser.find_element_by_class_name("year-dropdown").click()
            browser.find_element_by_id("{}".format(int(sd[2]))).click()
            browser.find_element_by_xpath('//span[text()="{}"]'.format(int(sd[0]))).click()
            browser.find_elements_by_class_name("wc-date-container")[1].click()
            browser.find_elements_by_class_name("month-year")[1].click()
            browser.find_elements_by_id("{}".format(ed[1].upper()))[1].click()
            browser.find_elements_by_class_name("year-dropdown")[1].click()
            browser.find_element_by_id("{}".format(int(ed[2]))).click()
            browser.find_elements_by_xpath('//span[text()="{}"]'.format(int(ed[0])))[1].click()
            browser.find_elements_by_tag_name("button")[-1].click()
            try:
                WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.ID,"DataTables_Table_0_wrapper")))
            except TimeoutException:
                print("Timed out waiting for page to load")
                break
            browser.find_element_by_tag_name("select").send_keys("100")
            maxpage = int(browser.find_elements(By.XPATH,"//*[@id='DataTables_Table_0_paginate']/span/a")[-1].text)
            i = 1
            while i < maxpage + 1:
                browser.find_element(By.XPATH,"//*[@id='DataTables_Table_0_paginate']/span/a[contains(text(),'{}')]".format(i)).click()
                res = browser.page_source
                soup = BeautifulSoup(res, 'html.parser')
                soup = soup.find(id = 'DataTables_Table_0')
                if i == 1:
                    data = getValsHtml(soup)
                else:
                    data = data.append(getValsHtml(soup))
                i = i + 1
                
            soups.append([(state, city, station), data])
            browser.quit()
            print("Finished Crawling for {}, {}, {}".format(state, city, station))
        except:
            print("Exception raised for {}, {}, {}".format(state, city, station))
            time.sleep(5)
    return soups
    

def getValsHtml(table):
    data = []
    heads = table.find_all('th')
    data.append([ele.text.strip() for ele in heads])
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols]) # Get rid of empty values
    data.pop(1)
    data = pd.DataFrame(data[1:],columns = data[0])
    return data

def main():
    parser = build_parser()
    options = parser.parse_args()
    global option,browser,url,param,startdate,enddate,duration,directory,chdriverpath
    param = options.param
    chdriverpath = options.driver
    directory = options.output
    startdate = options.sdate
    enddate = options.edate
    duration = ' '.join(options.duration)
    option = webdriver.ChromeOptions()
    os.chdir(options.dir)
    prefs = {'download.default_directory' : '{}'.format(options.dir)}
    option.add_experimental_option('prefs', prefs)
    url = 'https://app.cpcbccr.com/ccr/#/caaqm-dashboard-all/caaqm-landing/data'
    cities = getCities()
    if not os.path.exists(directory):
        os.makedirs(directory)
    for elem in range(cities.shape[0]):
        stateName, cityName = cities["StateName"][elem],cities["CityName"][elem]
        try:
            soups = getData(stateName, cityName, param,startdate,enddate,duration)
            for s in soups:
                state, city, station = s[0]
                s[1].to_csv("{}/{}_{}_{}.csv".format(directory,state, city, station),index = False)
            print("---")
            print("Finished Crawling city {}, {}".format(stateName, cityName))
            time.sleep(1)
        except:
            print("Error occurred at {}, {}".format(stateName, cityName))
            break

if __name__ == '__main__':
	main()


#python scraper.py --dir D:\ds\data --driver C:\Users\Samarth\Desktop\chromedriver.exe --output Data --p PM2.5 PM10 NO NO2 NOx NH3 CO SO2 O3 Benezene Toluene Xylene AQI AQI_Bucket --sdate 01-01-2015 --edate 01-07-2020 --duration 24 Hours 
