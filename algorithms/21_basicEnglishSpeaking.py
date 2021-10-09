import warnings
warnings.filterwarnings(action='ignore')
import requests
from bs4 import BeautifulSoup

targetSite = 'https://basicenglishspeaking.com/daily-english-conversation-topics/'
request = requests.get(targetSite)
html = request.text

soup = BeautifulSoup(html, 'html.parser')


subject = []  # empty list that saves topic
divs = soup.findAll('div', {'class':'tcb-col'})
#print(len(divs))

for div in divs:
    chapter = div.findAll('a')
    for a in chapter:
        print(a.text)
        subject.append(a.text)

for i in range(len(subject)):
    print('{0:2d}. {1}'.format(i+1, subject[i]))
