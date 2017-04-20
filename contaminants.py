import pdb
import pandas
import re
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

class Contaminants:
    def __init__(self, driver, engine, id):
        self.driver = driver
        self.engine = engine
        self.id = id # id of the supplier

    def processTable(self, table):
        soup = BeautifulSoup(table.get_attribute('innerHTML'), 'lxml')
        rows = soup.findAll('tbody')
        res = []
        for row in rows:
            elts = row.findAll('td')
            if len(elts) < 5:
                break
            contaminant = elts[0].find('a').children.next()
            iter = elts[1].children
            averageResult = iter.next()
            iter.next()
            maxResult = iter.next()

            healthLimitExceeded = elts[2].text
            legalLimitExceeded = elts[3].text
            res.append([contaminant, averageResult, maxResult, healthLimitExceeded, legalLimitExceeded])
        df = pandas.DataFrame(res)
        df.columns = ['contaminant', 'average_result', 'max_result', 'health_limit_exceeded', 'legal_limit_exceeded']
        df['id'] = self.id
        df.to_sql('contaminants', self.engine, index=False, if_exists='append')

    def parse(self):
        exceeding = None
        other = None
        tables = self.driver.find_elements_by_xpath('//table[@id="search2-table"]')
        map(self.processTable, tables)