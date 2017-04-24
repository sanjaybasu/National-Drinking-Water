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
import traceback

conn = psycopg2.connect(dbname='drinking_water')
conn.set_session(autocommit=True)

readCur = conn.cursor()
writeCur = conn.cursor()

engine = create_engine('postgresql://localhost:5432/drinking_water')
db_setup.setup(engine)

connection = engine.connect()

if not(os.path.exists('./zip_codes.csv')):
    url = 'http://federalgovernmentzipcodes.us/free-zipcode-database-Primary.csv'
    check_output(['wget', url, '-O', 'zip_codes.csv'])

    zip_codes = pandas.read_csv('./zip_codes.csv')
    zip_codes.columns = map(lambda c: c.lower(), zip_codes.columns)
    zip_codes.to_sql('zip_codes', engine, index=False, if_exists='replace')
    engine.execute('ALTER TABLE zip_codes ADD COLUMN suppliers integer[];')



driver = webdriver.Chrome()
driver.implicitly_wait(2)

def dump():
    soup = BeautifulSoup(driver.page_source, "html.parser")
    open('out.html', 'w').write(soup.prettify().encode('utf-8'))

base = 'http://www.ewg.org/tap-water/'
driver.get(base)
driver.find_element_by_xpath('//a[@href="javascript:gotopage();"]').click()

readCur.execute('SELECT zipcode FROM zip_codes WHERE suppliers IS NULL;')
for zip_code, in readCur:
    with engine.begin() as connection:
        driver.get(base)

        str_zip_code = str(zip_code).zfill(5)

        inputElt = driver.find_element_by_xpath('//input[@class="zip"]')
        inputElt.send_keys(str_zip_code)

        prev_url = driver.current_url

        driver.find_element_by_xpath('//input[@value="Go"]').click()

        while driver.current_url == prev_url:
            sleep(0.1)

        if 'search' in driver.current_url:
            supplier = Supplier(driver, connection, zip_code)
            empty = True
            i = 0
            for id, href in supplier.parse():
                empty = False
                driver.get(href)
                vr = ViolationSummary(driver, connection, id)
                violationSummary = vr.parse()
                contaminants = Contaminants(driver, connection, id)
                contaminants.parse()
                i += 1
            if empty:
                print("UPDATE zip_codes SET suppliers='{}' WHERE zipcode=%d" % zip_code)
                connection.execute("UPDATE zip_codes SET suppliers='{}' WHERE zipcode=%d" % zip_code)
            print('Found %d suppliers for %s' % (i, str_zip_code))
        else:
            print('Found a single supplier for %s' % str_zip_code)
            supplier = SingleSupplier(driver, connection, zip_code)
            id, href = supplier.parse()
            if id is None:
                continue
            driver.get(href)
            vr = ViolationSummary(driver, connection, id)
            violationSummary = vr.parse()
            contaminants = Contaminants(driver, connection, id)
            contaminants.parse()
        print('Committing transaction')
