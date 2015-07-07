from __future__ import unicode_literals
import requests
from bs4 import BeautifulSoup
import sys


BASE_URI = ("http://info.kingcounty.gov"
            "/health/ehs/foodsafety/inspections/Results.aspx?")

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
    with open(filename, "rb") as f:
        return f.read(), "utf-8"


def parse_source(body, encoding="utf-8"):
    return BeautifulSoup(body, "html5lib", from_encoding=encoding)


def has_two_tds(elem):
    is_tr = elem.name == 'tr'
    td_children = elem.find_all('td', recursive=False)
    has_two = len(td_children) == 2
    return is_tr and has_two


def extract_data_listings(body):
    def helper(tag):
        if tag.name != "div":
            return False
        return tag.get("id") is not None and tag.get("id").startswith("PR")
    return body.find_all(helper)


def clean_data(td):
    dta = td.string
    try:
        return dta.strip(" \n:-")
    except AttributeError:
        return u""


def extract_restaurant_metadata(elem):
    metadata_rows = listing.find('tbody').find_all(
        has_two_tds, recursive=False
    )
    data, label = {}, ""
    for row in metadata_rows:
        key, val = row.find_all('td', recursive=False)
        new_label = clean_data(key)
        if new_label:
            label = new_label
        data.setdefault(label, []).append(clean_data(val))
    return data


def is_inspection_row(elem):
    if elem.name != "tr":
        return False
    children = elem.find_all('td', recursive=False)
    text = clean_data(children[0]).lower()
    return (len(children) == 4 and "inspection" in text and
            not text.startswith("inspection"))


def extract_score_data(elem):
    inspection_rows = elem.find_all(is_inspection_row)
    samples = len(inspection_rows)
    data = {"Total Inspections": 0, "High Score": 0, "Average Score": 0}
    for row in inspection_rows:
        strval = clean_data(row.find_all('td')[2])
        try:
            intval = int(strval)
        except (ValueError, TypeError):
            samples -= 1
        else:
            data['Total Inspections'] += intval
            if intval > data["High Score"]:
                data['High Score'] = intval
            else:
                data["High Score"]
    if samples:
        data["Average Score"] = data["Total Inspections"] / float(samples)
    return data

if __name__ == "__main__":
    kwargs = {
        'Inspection_Start': '2/1/2013',
        'Inspection_End': '2/1/2015',
        'Zip_Code': '98109'
    }
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        html, encoding = load_inspection_page('inspection_page.html')
    else:
        html, encoding = get_inspection_page(**kwargs)
    doc = parse_source(html, encoding)
    listings = extract_data_listings(doc)
    for listing in listings[:5]:
        metadata = extract_restaurant_metadata(listing)
        score_data = extract_score_data(listing)
        print score_data
