# start to make packages for the parsing of the CR xml files
import os
import errno
import requests
from bs4 import BeautifulSoup
import json
import re

# Download the htm files referenced in the main file for that day. Cache them 
# so you do not need to keep redownloading them. Make sure path of this file 
# is the project directory, otherwise you will need to modify .gitignore or 
# your personal exclude file
def requestHTMLFile(url, useCache = True):
    if useCache == False:
        return requests.get(url).content
    else:
        urlSplit = url.split('/')
        if urlSplit[2] != 'www.govinfo.gov':
            raise WrongWebsiteException('htm file is not from govinfo.gov. Aborting.')
        fileSavePath = url[24:len(url)]
        # Check to see if we've already created this file path
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
                    raise fileExists('Tried to create a directory that later existed. This is probably a race condition where another instance downloading CR data finished first.')
                # else:
                #     raise fileExists('Tried to create a directory that did not exist and now exists. Something is wrong in requestHTMLFile.')
            with open(fileSavePath, "w") as f:
                f.write(downloadHTML.text)
            return downloadHTML.content

#%% Clean section text
def clean_section(section):
    '''
    This function takes a section of text and:
        1. Removes extraneous page numbers
        2. Removes everything in the header
        3. Removes some newline spaces
        4. Replace some newlines with newline + tab

    Parameters
    ----------
    section : string
        string of text representing a section in the congressional crecord

    Returns
    -------
    cleaned_section : string
        Condensed text without new lines and such

    '''
    
    # Remove extraneous page #'s, which appear either as [H123] or [S123]
    page_pattern = re.compile(r"""
                        \n\n            # identify preceeding newlines to the pages.
                        \[+             # Start with one or more open brackets
                        Page            # Our string ends with something like [Page H123]]
                        \s              # Whitespace
                        [HS]            # Either 'H' or 'S'
                        \d+             # At least one digit
                        \]+             # Ending bracket(s)
                        \s              # Any remaining whitespace before the start of our text
                         """, 
                        re.VERBOSE | re.MULTILINE)
    cleaned_section = re.sub(page_pattern, ' ', section) # replace above with space.
    
    
    # Remove everything in the header (Congressional Record Volume all the way up to
    #  www.gpo.gov
    header_pattern = re.compile(r"""
                        \[             # Start with an open bracket
                        Congressional   # Then theterm Congressional Record Volume
                        \s              # Include this in case reading the PDF gives us extra white spaces in between words
                        Record          # Continuation of Congressional Record Volume
                        \s              # More undetermined whitespace
                        Volume          # End of Congressional Record Volume
                        .*              # Find everything between the beginning and end
                        \[              # Our string ends with something like [www.gpo.gov]
                        www.gpo.gov     # The URL
                        \]              # Closing bracket
                        \n+             # tack on extra newlines
                        \s+             # Any final whitespace
                        """,   
                        re.VERBOSE | re.MULTILINE | re.DOTALL)
                          
    cleaned_section = re.sub(header_pattern, '', cleaned_section)
    
    # Remove some newline spaces
    # remove formatting newlines that do not start new paragraph
    new_line_pattern = re.compile("\n(?=\S)")
    cleaned_section = re.sub(new_line_pattern, '', cleaned_section)
    
    # address new paragraph newlines... replace with newline and tab
    new_line_pattern2  = re.compile("\n\s{2}(?=[A-Z])")
    cleaned_section = re.sub(new_line_pattern2, '\n\t', cleaned_section)
    
    # remove initial space that "centers" the title text and any extra 
    # newlines at the end
    return cleaned_section.strip()

# actually make a basic parser
def parseSection(child_element):
    parsedSection = {}
    try:
        parsedSection['CR_Section'] = child_element.partName.text
        parsedSection['title'] = child_element.title.text
        urlOfReferencedText = child_element.location.find('url',{'displayLabel':"HTML rendition"}).text
        parsedSection['url'] = urlOfReferencedText
        # wrap the below function in some kind of cached file checker which will cache the html files it pulls
        html_rend_pull = requestHTMLFile(urlOfReferencedText)
        bs4_html_rend_pull = BeautifulSoup(html_rend_pull, 'html.parser')
        parsedSection['raw_text'] = bs4_html_rend_pull.body.pre.text
        parsedSection['cleaned_text'] = clean_section(parsedSection['raw_text'])
        parsedSection['speakers'] = [name.namePart.text for name in child_element.find_all('name',{'type':"personal"})]
    except AttributeError:
        return None
    try:
        parsedSection['citation'] = child_element.find('identifier',{'type':'preferred citation'}).text
    except AttributeError: #probably should be done in a cleaner way so that if the citation is missing code still runs.
        raise CitationError('Missing Preferred Citation in parseSection')
    return parsedSection

# get a specific xml for the congressional record by date
# in the future, it may be useful to simply get the zip file:
# https://www.govinfo.gov/content/pkg/CREC-2021-02-24.zip
# dateString - is in the form "year-month-day" with year 4 digits, m/d 2 digits
def getCRMetadata(dateString, returnFullDateString = False):
    fullDateString = 'CREC-' + dateString 
    urlString = 'https://www.govinfo.gov/metadata/pkg/' + fullDateString + '/mods.xml'
    cr_xml_data = requestHTMLFile(urlString)
    parsed_cr = BeautifulSoup(cr_xml_data, "xml")
    mods = list(parsed_cr.children)[0]
    if returnFullDateString == True:
        return mods, fullDateString
    return mods

# parse the metadata and return the list of parsed sections
def parseCRMetadata(mods):
    listOfParsedSections = []
    for child in mods:
        name = getattr(child, "name", None)
        if name is not None:
            temp = parseSection(child)
            if temp is not None:
                listOfParsedSections.append(temp)
    return listOfParsedSections

def makeCRJSON(listOfParsedSections):
    listAsJSON = json.dumps(listOfParsedSections)
    return listAsJSON

def saveCRMetadata(listAsJSON, jsonSavePath):
    try:
        os.makedirs(os.path.dirname(jsonSavePath))
    except FileExistsError:
        #ignore the fact the file exists and overwrite it below
        pass
    with open(jsonSavePath, "w") as f:
        f.write(listAsJSON)
    return

# method that invokes all of the above methods, optionally saves file, and returns
# the parsed data
# dataString: year-month-date as YYYY-MM-DD
# savePath, optional, where to save the CR for that day
# saveFile, optional, whether or not to save file
# returnAsJSON, optional, whether or not to return json or parsed bs4 file
#   file will not be saved if returnAsJSON is set to false
def getCR(dateString, savePath='', returnAsJSON = True, saveFile = True):
    mods, fullDateString = getCRMetadata(dateString, returnFullDateString = True)
    if savePath == '':
        jsonSavePath = 'json_output/' + fullDateString + '/cr.json'
    else:
        jsonSavePath = savePath
    listOfParsedSections = parseCRMetadata(mods)
    if returnAsJSON == True:
        listAsJSON = makeCRJSON(listOfParsedSections)
        if saveFile == True:
            saveCRMetadata(listAsJSON,jsonSavePath)
        return listAsJSON
    else:
        return listOfParsedSections
    
    


































