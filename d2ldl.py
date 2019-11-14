from requests_html import HTMLSession 
from bs4 import BeautifulSoup
from getpass import getpass, getuser
import json

import os

print("Welcome to d2ldl: download shit from Learn")
print("Logging you in...")

session = HTMLSession(mock_browser=True)

r = session.get('https://learn.uwaterloo.ca/d2l/login?&noredirect=1')

user = input('WatIAm ID: ')
pw = getpass()

payload = {'nordirect': 1, 'loginPath': '/d2l/login', 'UserName': user, 'Password' : pw}

r = session.post('https://learn.uwaterloo.ca/d2l/lp/auth/login/login.d2l', data=payload, allow_redirects=False)

# sessionVals = r.cookies.get_dict() 

r = session.get('https://learn.uwaterloo.ca/d2l/home')

soup = BeautifulSoup(r.content, 'html.parser')

courses = session.get('https://learn.uwaterloo.ca/d2l/lp/courseSelector/6606/InitPartial?_d2l_prc%24headingLevel=2&_d2l_prc%24scope=&_d2l_prc%24hasActiveForm=false&isXhr=true&requestId=3')

if courses.text.find('while(1);') == 0:
    coursesjson = courses.text[len('while(1);'):]

coursesdict = json.loads(coursesjson)

courseselectorsoup = BeautifulSoup(coursesdict['Payload']['Html'], 'html.parser')

courseselectoritems = courseselectorsoup.find_all('div', attrs={'class':'d2l-course-selector-item'})


print("You are taking: ")
for course in courseselectoritems:
    print(course.find('a').text)
    print('>>> with unit id: ' + course.get('data-org-unit-id'))

unitid = input('Download which unit id? ')


# example, go to the first link

# r = session.get('https://learn.uwaterloo.ca' + courseselectoritems[0].find('a').get('href'))

# oh shit you can set RSS feeds for announcements lol


# go to the content page 

contentlink = f'https://learn.uwaterloo.ca/d2l/le/content/{unitid}/Home?itemIdentifier=TOC'
r = session.get(contentlink)


soup = BeautifulSoup(r.content, 'html.parser')

allLinks = soup.find_all("a", href=lambda href: href and "viewContent" in href)

def extractItemID(href):
    s = href.split('/')
    return s[6]

def extractFnameFromContentDisposition(cd):

    things = cd.split(' ')

    fnamething = next(x for x in things if 'filename=' in x)

    fname = fnamething.split('=')[1].split('"')[1]

    return fname

foldername = input('folder name? ')

folderExists = os.path.isdir(foldername)

if folderExists:
    print("Folder exists.")
else:
    print("Creating folder...")
    os.mkdir(foldername)

print("Downloading...")
for link in allLinks:
    fileid = extractItemID(link.get('href'))

    dlLink = f"https://learn.uwaterloo.ca/d2l/le/content/{unitid}/topics/files/download/{fileid}/DirectFileTopicDownload"

    if 'Discussion Topic' not in link.get('title'):
        # download the file 
        d = session.get(dlLink)
        fname = extractFnameFromContentDisposition(d.headers['Content-Disposition'])
        print(f"Saving {fname}...")
        open(os.path.join(foldername, fname), 'wb').write(d.content)

