import warnings
warnings.filterwarnings(action='ignore')
import requests
from bs4 import BeautifulSoup


class Conversation:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer
    def __str__(self):
        return 'Question: {}\nAnswer: {}'.format(self.question, self.answer)

c = Conversation('Who are you', 'I am ____')
#print(c)

# Takes 75 conversations url -> crawl and return
def getSubject():
    targetSite = 'https://basicenglishspeaking.com/daily-english-conversation-topics/'
    request = requests.get(targetSite)
    html = request.text
    soup = BeautifulSoup(html, 'html.parser')

    subject = []  # empty list that saves topic
    contentLink = []
    divs = soup.findAll('div', {'class':'tcb-col'})
    for div in divs:
        chapter = div.findAll('a')
        for a in chapter:
            subject.append(a.text)
#            print(a.get('href'))
            contentLink.append(a.get('href'))

    return subject, contentLink

subject, contentLink = getSubject()
#for i in range(len(subject)):
#    print('{0:2d}. {1} - {2}'.format(i + 1, subject[i], contentLink[i]))

# Creat list for saving all of the conversation topics
conversation = []

i = 0 # counts the number of topics => list index
for s in subject[:]:
    conversation.append('{0:2d}. {1} - {2}'.format(i + 1, subject[i], contentLink[i]))

    request = requests.get(contentLink[i])
    html = request.text
    soup = BeautifulSoup(html, 'html.parser')

    # conversation content is placed in 'sc_player_container1'(class) div tag which is next sibling
    divs = soup.findAll('div', {'class': 'sc_player_container1'})

    for div in divs:
        # index() method
        # divs.index(div) => From entire play button, get specific play button
        # next_sibling
        if divs.index(div) % 2 == 0: # decides if Q or A
#            print('Question: {}'.format(div.next_sibling))
            question = div.next_sibling
        else:
            answer = div.next_sibling
#            print('Answer: {}'.format(div.next_sibling))
            c = Conversation(question, answer)
            conversation.append(c)


    i += 1

for c in conversation:
    print(c)
