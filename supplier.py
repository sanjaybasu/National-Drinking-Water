
import pdb
import pandas, re
from selenium.common.exceptions import NoSuchElementException
import traceback

class Supplier:
    def __init__(self, driver, cur, zipcode):
        self.driver = driver
        self.cur = cur
        self.zipcode = zipcode

    def parse(self):
        try:
            table = self.driver.find_element_by_xpath('//table[@id="supplier-table"]')
        except NoSuchElementException as e:
            return []
        html = '<table>%s</table>' % table.get_attribute('innerHTML')
        self.df = pandas.read_html(html)[0]
        try:
            self.df['href'] = map(lambda x: x.get_attribute('href'), table.find_elements_by_xpath('//tr/td/a'))
        except Exception as e:
            pdb.set_trace()
        return self.iter()

    def iter(self):
        try:
            for idx, row in self.df.iterrows():
                row = row.apply(lambda x: x.replace('%', '%%') if type(x) is unicode or type(x) is str else x)
                res = self.cur.execute("""
                    INSERT INTO suppliers (supplier_name, locations_served, number_of_people_served, href, zipcode)
                    VALUES ('%s', '%s', %d, '%s', %d) ON CONFLICT DO NOTHING RETURNING id;
                """ % (row[0], row[1], row[2], row[3], self.zipcode))
                rows = res.fetchall()
                if len(rows) == 0:
                    # Already did this one...
                    print('Already processed %s' % row[0])
                    continue
                else:
                    self.cur.execute("""
                        UPDATE zip_codes SET suppliers=%d || suppliers
                        WHERE zipcode=%d
                    """ %(rows[0][0], self.zipcode))
                    yield rows[0][0], row['href']
        except Exception as e:
            traceback.print_exc()
            pdb.set_trace()

class SingleSupplier:
    def __init__(self, driver, cur, zipcode):
        self.driver = driver
        self.cur = cur
        self.zipcode = zipcode

    def parse(self):
        header = self.driver.find_elements_by_xpath('//div[contains(@class, "node")]//h3')[0].text
        [supplier_name, locations_served] = header.split(' - ')
        href = self.driver.current_url
        pop_elt = self.driver.find_elements_by_xpath('//div[contains(@class, "node")]//p')[0].text
        number_of_people_served = pop_elt.split(' - ')[0]
        number_of_people_served = int(re.findall(r'\d+', number_of_people_served.replace(',', ''))[0])
        res = self.cur.execute("""
            INSERT INTO suppliers (supplier_name, locations_served, number_of_people_served, href, zipcode)
            VALUES ('%s', '%s', %d, '%s', %d) ON CONFLICT DO NOTHING RETURNING id;
        """ % (supplier_name, locations_served, number_of_people_served, href, self.zipcode))
        rows = res.fetchall()
        if len(rows) == 0:
            self.cur.execute("""
                UPDATE zip_codes SET suppliers = suppliers.id || COALESCE(suppliers, '{}')
                FROM suppliers
                WHERE suppliers.href='%s' AND zip_codes.zipcode=%d
            """ % (href, self.zipcode))
            # Already did this one...
            print('Already processed %s' % supplier_name)
            return None, None
        else:
            self.cur.execute("""
                UPDATE zip_codes SET suppliers=%d || COALESCE(suppliers, '{}')
                WHERE zipcode=%d
            """ %(rows[0][0], self.zipcode))
            return rows[0][0], href
