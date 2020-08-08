from .parser import Parser
from bs4 import BeautifulSoup

content_key = ('Statement Period',
               'Total Amount Due',
               'Minimum Amount Due',
               'Payment Due Date')

class YesBankParser(Parser):

    def extract_information(self, raw_data: str, content_type: str):
        results = dict()
        if content_type == 'text/html':
            soup = BeautifulSoup(raw_data, 'html.parser')
            td_data = soup.find_all('td')
            for i, td in enumerate(td_data):
                if td.text in content_key:
                    results[td.text] = td_data[i+1].text

        return results
