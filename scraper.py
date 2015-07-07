from __future__ import unicode_literals
import requests
from bs4 import BeautifulSoup
import sys


BASE_URI = ("http://info.kingcounty.gov"
            "/health/ehs/foodsafety/inspections/Results.aspx?")

QUERY_PARAMS = {
    "Output": "W",
    "Business_Name": None,
    "Business_Address": None,
    "Longitude": None,
    "Latitude": None,
    "City": "Seattle",
    "Zip_Code": None,
    "Inspection_Type": "All",
    "Inspection_Start": "01/01/2015",
    "Inspection_End": "07/01/2015",
    "Inspection_Closed_Business": "A",
    "Violation_Points": None,
    "Violation_Red_Points": None,
    "Violation_Descr": None,
    "Fuzzy_Search": "N",
    "Sort": "B"
}


def get_inspection_page(**kwargs):
    url = BASE_URI
    params = QUERY_PARAMS.copy()
    for key in kwargs:
        if key in QUERY_PARAMS:
            params[key] = kwargs[key]
        else:
            raise ValueError("{} is not a valid parameter".format(key))
    resp = requests.get(url, params)
    resp.raise_for_status()

    return resp.content, resp.encoding


def load_inspection_page(filename="inspection_page.html"):
    return open(filename, "rb").read(), "utf-8"


def parse_source(body, encoding="utf-8"):
    return BeautifulSoup(body, "html5lib", from_encoding=encoding)

if __name__ == "__main__":
    Zip_Code = 98109
    Date = "2/1/2015"
    if sys.argv[-1] == "test":
        body, encoding = load_inspection_page()
    else:
        body, encoding = get_inspection_page()
    doc = parse_source(body)
    print doc.prettify(encoding=encoding)
