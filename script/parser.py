#!/usr/bin/env python3
# thanks to https://beckernick.github.io/faster-web-scraping-python/
# !!: PLEASE RUN on the base path folder, not from the script folder
# !!: python3 script/parser.py

import os
import re
import json
import time
import pytz
import requests
import concurrent.futures
from lxml import html
from datetime import datetime

tz = pytz.timezone('Asia/Jakarta')
base_url = 'https://www.jadwalsholat.org/adzan/monthly.php'

def strip_lower(str):

    return re.sub(r'\W+', '', str).lower()


def get_cities() :

    first_page = requests.get(base_url)
    first_page_doc = html.fromstring(first_page.content)

    city_ids = first_page_doc.xpath('//select[@name="kota"]/option/@value')
    city_names = first_page_doc.xpath('//select[@name="kota"]/option/text()')
    city_names = [strip_lower(d) for d in city_names]

    return dict(zip(city_ids, city_names))


def get_adzans(city_id, month = '', year = '') :

    if  month == '' :
        month = datetime.now(tz).month

    if  year == '' :
        year = datetime.now(tz).year

    url = base_url + '?id={}&m={}&y={}'.format(city_id, month, year)

    page = requests.get(url)

    doc = html.fromstring(page.content)

    rows = doc.xpath('//tr[contains(@class, "table_light") or contains(@class, "table_dark") or contains(@class, "table_highlight")]')

    result = []

    for row in rows:
        data = row.xpath('td//text()')
        result.append({
            'tanggal': '{}-{}-{}'.format(year, month, data[0]),
            'imsyak': data[1],
            'shubuh': data[2],
            'terbit': data[3],
            'dhuha': data[4],
            'dzuhur': data[5],
            'ashr': data[6],
            'magrib': data[7],
            'isya': data[8]
        })

    return result


def write_file(city, adzans):

    flb = fld = './adzan/'+city+'/'

    # monthly
    dt = adzans[0]['tanggal'].replace('-', '/')
    fld = flb+dt[:4]
    if not os.path.exists(fld):
        os.makedirs(fld, mode=0o777)
    fl = open(fld+'/'+dt[5:7]+'.json', 'w+')
    fl.write(json.dumps(adzans))
    fl.close()

    # daily
    # for adzan in adzans:
    #     dt = adzan['tanggal'].replace('-', '/')
    #     fld = flb+dt[:8]
    #     if not os.path.exists(fld):
    #         os.makedirs(fld, mode=0o777)
    #     fl = open(fld+dt[8::]+'.json', 'w+')
    #     fl.write(json.dumps(adzan))
    #     fl.close()


def process_city(name, id):

    month = os.getenv('JWO_MONTH', f"{datetime.now(tz).month:02d}")
    year = os.getenv('JWO_YEAR', f"{datetime.now(tz).year:02d}")

    write_file(name, get_adzans(id, month, year))
    print('processing ' + name + ' done')


def main():

    start = time.time()
    cities = get_cities()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for id, name in cities.items():
            print('processing ' + name)
            futures.append(executor.submit(process_city, name=name, id=id))
        for future in concurrent.futures.as_completed(futures):
            pass

    print('\n It took', time.time()-start, 'seconds.')

    print("\n Current working dir:")
    print(os.getcwd())

    print("\n List dir:")
    print(os.listdir(os.getcwd()))

    print("\n Git status:")
    print(os.system('git status'))

if __name__ == "__main__":
    main()
