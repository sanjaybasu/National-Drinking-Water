#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from time import sleep
from subprocess import check_output
import os, pdb, pandas, requests
from sqlalchemy import create_engine
import psycopg2
from violation_summary import ViolationSummary
from supplier import Supplier, SingleSupplier
from contaminants import Contaminants
import db_setup

conn = psycopg2.connect(dbname='drinking_water')
conn.set_session(autocommit=True)

readCur = conn.cursor()
writeCur = conn.cursor()

engine = create_engine('postgresql://localhost:5432/drinking_water')
db_setup.setup(engine)


if not(os.path.exists('./zip_codes.csv')):
    url = 'http://federalgovernmentzipcodes.us/free-zipcode-database-Primary.csv'
    check_output(['wget', url, '-O', 'zip_codes.csv'])

    zip_codes = pandas.read_csv('./zip_codes.csv')
    zip_codes.columns = map(lambda c: c.lower(), zip_codes.columns)
    zip_codes.to_sql('zip_codes', engine, index=False, if_exists='replace')

driver = webdriver.Chrome()
driver.implicitly_wait(2)

def dump():
    soup = BeautifulSoup(driver.page_source, "html.parser")
    open('out.html', 'w').write(soup.prettify().encode('utf-8'))

base = 'http://www.ewg.org/tap-water/'
driver.get(base)
driver.find_element_by_xpath('//a[@href="javascript:gotopage();"]').click()

readCur.execute('SELECT zipcode FROM zip_codes LEFT JOIN suppliers USING (zipcode) WHERE suppliers.id IS NULL;')
for zip_code, in readCur:
    driver.get(base)

    str_zip_code = str(zip_code).zfill(5)

    inputElt = driver.find_element_by_xpath('//input[@class="zip"]')
    inputElt.send_keys(str_zip_code)

    prev_url = driver.current_url

    driver.find_element_by_xpath('//input[@value="Go"]').click()

    while driver.current_url == prev_url:
        sleep(0.1)

    if 'search' in driver.current_url:
        supplier = Supplier(driver, writeCur, zip_code)
        for id, href in supplier.parse():
            driver.get(href)
            vr = ViolationSummary(driver, engine, id)
            violationSummary = vr.parse()
            contaminants = Contaminants(driver, engine, id)
            contaminants.parse()
    else:
        supplier = SingleSupplier(driver, writeCur, zip_code)
        id, href = supplier.parse()
        if id is None:
            continue
        driver.get(href)
        vr = ViolationSummary(driver, engine, id)
        violationSummary = vr.parse()
        contaminants = Contaminants(driver, engine, id)
        contaminants.parse()







