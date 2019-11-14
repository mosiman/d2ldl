#!/bin/python3.7

from requests_html import HTMLSession 
from bs4 import BeautifulSoup
from getpass import getpass, getuser
import json
import re
import os


# buncha functions and shit, probably move out to another file if this gets any bigger


def extractItemID(href):
    s = href.split('/')
    return s[6]

def extractFnameFromContentDisposition(cd):
    things = cd.split(' ')
    fnamething = next(x for x in things if 'filename=' in x)
    fname = fnamething.split('=')[1].split('"')[1]

    return fname

def downloadFromFolder(page, foldername):
    """
    Download anything with 'viewContent' in the href thats not a Discussion Topic 
    """
    p = session.get(page)
    soup = BeautifulSoup(p.content, 'html.parser')
    allLinks = soup.find_all("a", href=lambda href: href and "viewContent" in href)

    folderExists = os.path.isdir(foldername)
    if not folderExists:
        os.mkdir(foldername)

    for link in allLinks:
        fileid = extractItemID(link.get('href'))

        dlLink = f"https://learn.uwaterloo.ca/d2l/le/content/{unitid}/topics/files/download/{fileid}/DirectFileTopicDownload"

        if 'Discussion Topic' not in link.get('title'):
            # download the file 
            d = session.get(dlLink)
            fname = extractFnameFromContentDisposition(d.headers['Content-Disposition'])
            print(f"Saving {fname}...")
            open(os.path.join(foldername, fname), 'wb').write(d.content)


# ==================================
# ======= the goodie goods =========
# ==================================

print("Welcome to d2ldl: download shit from Learn")
print("Logging you in...")

session = HTMLSession(mock_browser=True)

r = session.get('https://learn.uwaterloo.ca/d2l/login?&noredirect=1')

user = input('WatIAm ID: ')
pw = getpass()

payload = {'nordirect': 1, 'loginPath': '/d2l/login', 'UserName': user, 'Password' : pw}

# Log in via a session, values are sent in headers as required from here on.
r = session.post('https://learn.uwaterloo.ca/d2l/lp/auth/login/login.d2l', data=payload, allow_redirects=False)
# sessionVals = r.cookies.get_dict() 


# Go to the home page
r = session.get('https://learn.uwaterloo.ca/d2l/home')
soup = BeautifulSoup(r.content, 'html.parser')

# find the term ID (is that what it is?)
# termID is needed to find the courses for this term.
# the 'calendar' URL just so happens to have this term ID
calendarURL = soup.find('a', href=lambda href: href and 'calendar' in href)
termID = calendarURL.get('href').split('/')[-1]


# Parse the courses data
courses = session.get(f'https://learn.uwaterloo.ca/d2l/lp/courseSelector/{termID}/InitPartial')
if courses.text.find('while(1);') == 0:
    coursesjson = courses.text[len('while(1);'):]
coursesdict = json.loads(coursesjson)
courseselectorsoup = BeautifulSoup(coursesdict['Payload']['Html'], 'html.parser')
courseselectoritems = courseselectorsoup.find_all('div', attrs={'class':'d2l-course-selector-item'})


print("You are taking: ")
for course in courseselectoritems:
    print(course.find('a').text)
    print('    with unit id: ' + course.get('data-org-unit-id'))

unitid = input('Download which unit id? ')
foldername = input('folder name? ')
folderExists = os.path.isdir(foldername)
if folderExists:
    print("Folder exists.")
else:
    print("Creating folder...")
    os.mkdir(foldername)

print("Downloading...")

contentlinkTOC = f'https://learn.uwaterloo.ca/d2l/le/content/{unitid}/Home?itemIdentifier=TOC'
contentlinkItemIDBase = f'https://learn.uwaterloo.ca/d2l/le/content/{unitid}/Home?itemIdentifier='

# Go to table of contents
r = session.get(contentlinkTOC)
soup = BeautifulSoup(r.content, 'html.parser')

# See if I can traverse all the folders on the page.
# TODO: recursively build content structure
# right now: only looks at TOC and immediate modules

lis = soup.find_all('li', attrs={'data-key': True, 'class': 'd2l-le-TreeAccordionItem'})
maybefolders = [x for x in lis if 'D2L.LE.Content.ContentObject.Module' in x.get('id')]

for folder in maybefolders:
    # get foldername from text (kinda convoluted)
    # folder.text  --> '\n\n\n\nTITLE\n module: contains X sub-modules \nselected'
    folderTitle = folder.text.strip().split('\n')[0]

    # Avoid downloading too much: submodules put inside folder
    # how many submodules?
    # reg = re.compile('contains (.*) sub-modules')
    # print(reg.findall(folder.text))
    # TODO actually implement this properly lol

    folderlink = contentlinkItemIDBase + folder.get('data-key')
    print(f'Downloading from {folderTitle}...')
    downloadFromFolder(folderlink, os.path.join(foldername, folderTitle))
