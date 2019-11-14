from requests_html import HTMLSession 
from bs4 import BeautifulSoup
from getpass import getpass
import json

import pprint
pp = pprint.PrettyPrinter(indent=4)

session = HTMLSession(mock_browser=True)

r = session.get('https://learn.uwaterloo.ca/d2l/login?&noredirect=1')

email = 'd49chan'
pw = getpass()

payload = {'nordirect': 1, 'loginPath': '/d2l/login', 'UserName': email, 'Password' : pw}

r = session.post('https://learn.uwaterloo.ca/d2l/lp/auth/login/login.d2l', data=payload, allow_redirects=False)

sessionVals = r.cookies.get_dict() 

r = session.get('https://learn.uwaterloo.ca/d2l/home')

soup = BeautifulSoup(r.content, 'html.parser')

courses = session.get('https://learn.uwaterloo.ca/d2l/lp/courseSelector/6606/InitPartial?_d2l_prc%24headingLevel=2&_d2l_prc%24scope=&_d2l_prc%24hasActiveForm=false&isXhr=true&requestId=3')

if courses.text.find('while(1);') == 0:
    coursesjson = courses.text[len('while(1);'):]

coursesdict = json.loads(coursesjson)

courseselectorsoup = BeautifulSoup(coursesdict['Payload']['Html'])

courseselectoritems = courseselectorsoup.find_all('div', attrs={'class':'d2l-course-selector-item'})


print("You are taking: ")
for course in courseselectoritems:
    print(course.find('a').text)
    print('>>> with unit id: ' + course.get('data-org-unit-id'))


# example, go to the first link

r = session.get('https://learn.uwaterloo.ca' + courseselectoritems[0].find('a').get('href'))

# oh shit you can set RSS feeds for announcements lol


# go to the content page 

unitid = courseselectoritems[0].get('data-org-unit-id')

contentlink = f'https://learn.uwaterloo.ca/d2l/le/content/{unitid}/Home?itemIdentifier=TOC'
r = session.get(contentlink)

# r.html.render()

soup = BeautifulSoup(r.content, 'html.parser')

#download_menuitem = soup.find('d2l-menu-item', attrs={'text': 'Download'})

#e.g.
# https://learn.uwaterloo.ca/d2l/le/content/478148/startdownload/InitiateCourseDownload?openerId=d2l_3_58_620

#openerID = download_menuitem.get('id')

#d = session.get(f'https://learn.uwaterloo.ca/d2l/le/content/{unitid}/startdownload/InitiateCourseDownload?openerID={openerID}').html.render()

# poll the server, see the status and jobid 

# e.g. https://learn.uwaterloo.ca/d2l/le/content/478148/downloads/Course/2576831/Poll?isXhr=true&requestId=2&X-D2L-Session=no-keep-alive

# get list of all toc items 

allLinks = soup.find_all("a", href=lambda href: href and "viewContent" in href)

def extractItemID(href):
    s = href.split('/')
    return s[6]

def extractFnameFromContentDisposition(cd):

    things = cd.split(' ')

    fnamething = next(x for x in things if 'filename=' in x)

    fname = fnamething.split('=')[1].split('"')[1]

    return fname

for link in allLinks:
    fileid = extractItemID(link.get('href'))

    dlLink = f"https://learn.uwaterloo.ca/d2l/le/content/{unitid}/topics/files/download/{fileid}/DirectFileTopicDownload"

    if 'Discussion Topic' not in link.get('title'):
        # download the file 
        d = session.get(dlLink)
        fname = extractFnameFromContentDisposition(d.headers['Content-Disposition'])
        open(fname, 'wb').write(d.content)






    









