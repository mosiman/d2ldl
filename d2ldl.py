from requests_html import HTMLSession 
from bs4 import BeautifulSoup
from getpass import getpass, getuser
import json
import re

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

# doesn't go into folders (e.g. Ex2 in STA332)
# <a class="d2l-link" href="/d2l/le/content/478148/Home?itemIdentifier=D2L.LE.Content.ContentObject.ModuleCO-2713629">Ex2</a>
# this link is accessed FROM TOC/Exercise/Ex2/ex2 (the pdf file)
# this link brings us to the Ex2 folder
# use this to recurse?
# how to access from TOC?
# Look for <li> with a `data-key` and `class : d2l-le-TreeAccordionItem`
#   Then find the ones with `D2l.LE.Content.ContentObject.Module` in their id or data-key.
#   The data key is the link to the folder


print("Downloading...")


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


contentlinkTOC = f'https://learn.uwaterloo.ca/d2l/le/content/{unitid}/Home?itemIdentifier=TOC'
contentlinkItemIDBase = f'https://learn.uwaterloo.ca/d2l/le/content/{unitid}/Home?itemIdentifier='

r = session.get(contentlinkTOC)

soup = BeautifulSoup(r.content, 'html.parser')

# See if I can traverse all the folders on the page.

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








