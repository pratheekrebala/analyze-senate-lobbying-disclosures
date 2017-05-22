# Can download files needed from here
# https://www.senate.gov/legislative/Public_Disclosure/database_download.htm

import os
import csv
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
import unicodedata
import zipfile, io

REPORT_DB = 'https://www.senate.gov/legislative/Public_Disclosure/database_download.htm'

def get_available_reports():
    response = requests.get(REPORT_DB)
    html = response.content
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('table')
    rows = []
    headers = []
    procesed_years = []

    for row in table.findAll('tr'):
        row_headers = row.findAll('th')
        row_data = row.findAll('td')
        if row_headers:
            for header in row_headers:
                headers.append(header.text)
        elif row_data and len(row_data) == 3:
            row_datum = []
            for index, cell in enumerate(row_data):
                text = unicodedata.normalize("NFKD", cell.text).strip()
                link = cell.find('a')
                if index == 0:
                    if text != '':
                        procesed_years.append(text)
                    else:
                        text = procesed_years[-1]

                if link:
                    row_datum.append((text, link['href']))
                else: row_datum.append(text)
            rows.append(dict(zip(headers, row_datum)))
    return rows

# download all reports available for given years.
def download_reports(years):
    available_reports = get_available_reports()
    filtered_reports = [report for report in available_reports if report['Year'] in years]
    for report in filtered_reports:
        download_report(report)

def download_report(report):
    print('Downloading {}: {} Quarter'.format(report['Year'], report['Quarter Received'][0]))
    report_url = report['Quarter Received'][1]
    r = requests.get(report_url, allow_redirects=True, stream=True, headers={'user-agent':'LobbyingDownloader'})
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall('./xmls_to_use/{}_{}'.format(report['Year'], report['Quarter Received'][0]))

download_reports(['2016'])