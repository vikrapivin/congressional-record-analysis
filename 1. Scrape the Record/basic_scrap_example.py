# scrape a certain date
import os
import errno
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

#%%

# get a specific xml for the congressional record
# in the future, it may be useful to simply get the zip file:
# https://www.govinfo.gov/content/pkg/CREC-2021-02-24.zip
dateString = 'CREC-2021-02-24'
urlString = 'https://www.govinfo.gov/metadata/pkg/'+dateString+'/mods.xml'

cr_xml_data = requests.get(urlString).content


#%%

# use BS4
parsed_cr = BeautifulSoup(cr_xml_data, "xml")

#%%

# explore the structure of the xml file
mods = list(parsed_cr.children)[0]
ii = 0
for child in mods:
    name = getattr(child, "name", None)
    if name is not None:
        # print(name)
        # print(child.title)
        try:
            if child.partName.text == 'Senate':
                # example of pulling the htm link data for a particular part of the CR
                print(child.title.text)
                urlOfReferencedText = child.location.find('url',{'displayLabel':"HTML rendition"}).text
                print(urlOfReferencedText)
                speakersInSection = [name.namePart.text for name in child.find_all('name',{'type':"personal"})]
                print(speakersInSection)
                # html_rend_pull = requests.get(urlOfReferencedText).content
                # bs_html_rend_pull = BeautifulSoup(html_rend_pull, 'html.parser')
                # print(bs_html_rend_pull.body.pre.text)
        except Exception:
            pass
    elif not child.isspace(): # leaf node, don't print spaces
        print(child)
        pass
    ii += 1
    if ii>=3009:
        break

#%% explore scraping and parsing data

# download the htm files referenced in the main file for that day. Cache them so you do not need to keep redownloading them.
# make sure path of this file is the project directory, otherwise you will need to modify .gitignore or your personal exclude file
def requestHTMLFile(url, useCache = True):
    if useCache == False:
        return requests.get(url).content
    else:
        urlSplit = url.split('/')
        if urlSplit[2] != 'www.govinfo.gov':
            raise WrongWebsiteException('htm file is not from govinfo.gov. Aborting.')
        fileSavePath = url[24:len(url)]
        if os.path.exists(os.path.dirname(fileSavePath)) and os.path.exists(fileSavePath):
            # handle getting cached file
            cachedHTMLFile = open(fileSavePath, "r")
            cachedHTML = cachedHTMLFile.read()
            cachedHTMLFile.close()
            return cachedHTML
        else:
            # handle caching new file
            downloadHTML = requests.get(url)
            try:
                os.makedirs(os.path.dirname(fileSavePath))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise fileExists('Tried to create file that later existed. Something is wrong in requestHTMLFile.')
            with open(fileSavePath, "w") as f:
                f.write(downloadHTML.text)
            return downloadHTML.content
        
    
# actually make a basic parser
def parseSection(child_element):
    parsedSection = {}
    try:
        parsedSection['CR_Section'] = child_element.partName.text
        parsedSection['title'] = child.title.text
        urlOfReferencedText = child.location.find('url',{'displayLabel':"HTML rendition"}).text
        # wrap the below function in some kind of cached file checker which will cache the html files it pulls
        html_rend_pull = requestHTMLFile(urlOfReferencedText)
        bs4_html_rend_pull = BeautifulSoup(html_rend_pull, 'html.parser')
        parsedSection['raw_text'] = bs4_html_rend_pull.body.pre.text
        parsedSection['speakers'] = [name.namePart.text for name in child.find_all('name',{'type':"personal"})]
        return parsedSection
    except AttributeError:
        return None

# run parser through all sections in the Congressional Record index htm
listOfParsedSections = []
mods = list(parsed_cr.children)[0]
# ii = 0
for child in mods:
    name = getattr(child, "name", None)
    if name is not None:
        temp = parseSection(child)
        if temp is not None:
            listOfParsedSections.append(temp)
    # ii += 1
    # if ii>=1000:
    #     break






































