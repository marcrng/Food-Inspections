import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import mysql.connector
import time
from mysql.connector import Error

# TODO: Use python to scrape and iteratively fill missing phone numbers using name and address with google search

# Connect to sql database
conn = mysql.connector.connect(
    host='localhost',
    database='inspection_data',
    user='marcrng',
    password='****'
)

cursor = conn.cursor()

cursor.execute(
    '''
    select distinct name, address, city
    from businesses
    where phone is null'''
)

result = cursor.fetchall()

num_list = []


for x in result:
    url = " ".join(map(str, x))
    url = url.replace(" ", "+")
    url = url.replace('#', '%')
    url = url.replace('&', '%26')
    url = 'http://www.google.com/search?q=' + url

    print(url)

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    df = pd.DataFrame(result)

    #time.sleep(2)

    for span in soup.findAll('span', class_='BNeawe tAd8D AP7Wnd'):
        phone = span.getText('aria-label')
        phonenum = re.findall(
            r'((?:\+\d{2}[-\.\s]??|\d{4}[-\.\s]??)?(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}))',
            phone)

        phonenum = phone = ''.join(phonenum)

        num_list.append(phonenum)
        print(phonenum)


print(num_list)
df['phonenummer'] = num_list
print(df)
# Create dataframe with phone numbers and id
df.to_csv('numbers.csv', encoding='utf-8', index=False)

# Prevent regex from allowing blanks and use elif to append 'N/A' in case of missing numbers
