import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import mysql.connector
from mysql.connector import Error

# TODO: Use python to scrape and iteratively fill missing phone numbers using name and address with google search

# Connect to sql database
conn = mysql.connector.connect(host='localhost',
                                   database='inspection_data',
                                   user='marcrng',
                                   password='****'
                                )

cursor = conn.cursor()

cursor.execute(
    '''
    select distinct name, address, city, id
    from businesses
    where phone is null'''
)

result = cursor.fetchmany(2)

for x in result:
    url = " ".join(map(str, x))
    url = url.replace(" ", "+")
    url = url.replace('#', '%')
    url = 'http://www.google.com/search?q=' + url

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    for span in soup.findAll('span', class_='BNeawe tAd8D AP7Wnd'):
        phone = span.getText('aria-label')
        phonenum = re.findall(r'((?:\+\d{2}[-\.\s]??|\d{4}[-\.\s]??)?(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}))', phone)
        phonenum = phone = ''.join(phonenum)
        print(phonenum)
# Build the url from dataframe



