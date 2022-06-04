import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import mysql.connector
from mysql.connector import Error

# TODO: Use python to scrape and iteratively fill missing phone numbers using name and address with google search


url = 'https://www.google.com/search?q=BALLARD+HIGH+SCHOOL+KITCHEN1418+NW+65TH+ST&oq=BALLARD+HIGH+SCHOOL+KITCHEN1418+NW+65TH+ST&aqs=edge..69i57j0i546l2.6105j0j9&sourceid=chrome&ie=UTF-8'

page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")

df = pd.DataFrame({
    'column':['one']
})

num_list = []

for span in soup.findAll('span', class_='BNeawe tAd8D AP7Wnd'):
    phone = span.getText('aria-label')
    phonenum = re.findall(
        r'((?:\+\d{2}[-\.\s]??|\d{4}[-\.\s]??)?(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}))',
        phone)



    if phonenum:
        phonenum = phone = ''.join(phonenum)

        num_list.append(phonenum)
        print(phonenum)
    else:
        continue

print(num_list)
df['phonenummer'] = num_list
print(df)
# Create dataframe with phone numbers and id
