#!/usr/bin/env python3

import os
import re
import json
import requests
from lxml import html
from datetime import datetime

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
        month = datetime.now().month

    if  year == '' :
        year = datetime.now().year

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

    flb = fld = './../adzan/'+city+'/'

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


def main():

    cities = get_cities()

    for id, name in cities.items():
        print('processing ' + name)
        write_file(name, get_adzans(id, '01', '2021'))


if __name__ == "__main__":
    main()
