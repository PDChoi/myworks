import warnings
warnings.filterwarnings(action='ignore')

import requests
from bs4 import BeautifulSoup

targetSite = 'http://www.dowellcomputer.com/main.jsp'
request = requests.get(targetSite)
#print(request)

html = request.text
print(type(html))
#print(html)

# using BesutifulSoup() func of bs4 module 

soup = BeautifulSoup(html, 'html.parser')
#print(type(soup))

notices = soup.findAll('b')

#for notice in notices[:2]:
#    print(notice.text)


notices = soup.findAll('td', {'class': 'tail'})
#for notice in notices:
#    print(notice)

notices = soup.select('td > a')
#print(notices)

for notice in notices:
#    print(notice)
#    print(notice.get('href'))
    if notice.get('href').find('notice') >= 0:
        print(notice.text)
