
import pdb
import pandas
import re
from selenium.common.exceptions import NoSuchElementException

class ViolationSummary:
    def __init__(self, driver, engine, id):
        self.driver = driver
        self.engine = engine
        self.id = id # id of the supplier

    def parse(self):
        try:
            table = self.driver.find_element_by_xpath('//table[@id="violation-table"]')
        except NoSuchElementException as e:
            # No violations found!
            return
        tables = table.find_elements_by_tag_name('table')
        for table in tables:
            df = pandas.read_html('<table>%s</table>' % table.get_attribute('innerHTML'))[0]
            df.columns = map(lambda c: c.lower().replace(' ', '_'), df.iloc[0])
            df = df.reindex(df.index.drop(0))
            df['id'] = self.id
            df.to_sql('violation_summary', self.engine, index=False, if_exists='append')


