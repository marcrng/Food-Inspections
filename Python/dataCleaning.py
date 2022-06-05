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
    where phone is null
    '''
)

count = cursor.execute(
    '''
    select count(distinct name, address, city)
    from businesses
    where phone is null
    '''
)

result = cursor.fetchall()

num_list = []

counter = -1

for x in result:
    url = " ".join(map(str, x))
    url = url.replace(" ", "+")
    url = url.replace('#', '%23')
    url = url.replace('&', '%26')
    url = url.replace('\'', '%27')
    url = url.replace('(', '%28')
    url = url.replace(')', '%29')
    url = url.replace('@', '%40')
    url = 'http://www.google.com/search?q=' + url

    counter += 1

    print(url)

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    df = pd.DataFrame(result)

    num_list.append('Not Found')  # Add a 'Not Found' entry to be overwritten if a phone number is found

    print(counter)

    # time.sleep(2)

    for span in soup.findAll('span', class_='BNeawe tAd8D AP7Wnd'):
        phone = span.getText('aria-label')
        phonenum = re.findall(

            r'((?:\+\d{2}[-\.\s]??|\d{4}[-\.\s]??)?(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}))',
            phone
        )

        if phonenum:
            print(phonenum)
            phonenum = phone = ''.join(phonenum)
            num_list[counter] = phonenum

df['phonenummer'] = num_list
print(df)
# Create dataframe with phone numbers and id
df.to_csv('numbers.csv', encoding='utf-8', index=False)
