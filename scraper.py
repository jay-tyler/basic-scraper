from __future__ import unicode_literals
import requests
from bs4 import BeautifulSoup
import os
import sys
import re

BASE_URI = "http://info.kingcounty.gov/health/ehs/foodsafety/inspections\
/Results.aspx?"

QUERY_PARAMS = {
    'Output': 'W',
    'Business_Name': '',
    'Business_Address': '',
    'Longitude': '',
    'Latitude': '',
    'City': '',
    'Zip_Code': '',
    'Inspection_Type': 'All',
    'Inspection_Start': '',
    'Inspection_End': '',
    'Inspection_Closed_Business': 'A',
    'Violation_Points': '',
    'Violation_Red_Points': '',
    'Violation_Descr': '',
    'Fuzzy_Search': 'N',
    'Sort': 'H'
}


def get_inspection_page(**kwargs):
    params = QUERY_PARAMS.copy()
    for key in kwargs:
        if key in params:
            params[key] = kwargs[key]
        else:
            raise ValueError("{} is not a valid parameter".format(key))

    resp = requests.get(BASE_URI, params=params)
    resp.raise_for_status()
    return resp.content, resp.encoding


def load_inspection_page():
    return open('inspection_page.html', "rb").read(), 'utf-8'


def parse_source(body, encoding='utf-8'):
    return BeautifulSoup(body, "html5lib", from_encoding=encoding)


def extract_data_listings(html):
    id_finder = re.compile(r'PR[\d]+~')
    return html.find_all('div', id=id_finder)


def has_two_tds(elem):
    if elem.name == 'tr':
        #  Test if tr has exactly two td children
        return len(elem.find_all('td', recursive=False)) == 2


if __name__ == "__main__":
    kwargs = {
        'Inspection_Start': '01/01/2013',
        'Inspection_End': '07/06/2015',
        'Zip_Code': 98109
    }

    if sys.argv[-1] == "test":
        content, encoding = load_inspection_page()
    else:
        content, encoding = get_inspection_page(**kwargs)
    doc = parse_source(content, encoding)
    listings = extract_data_listings(doc)
    for listing in listings:
        metadata_rows = listing.find('tbody').find_all(
            has_two_tds, recursive=False)
    print len(metadata_rows)
