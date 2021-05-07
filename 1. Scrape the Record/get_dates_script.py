#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  6 20:51:46 2021

@author: Owner
"""

#%% Import Packages
import requests
from bs4 import BeautifulSoup
import re
from dateutil.parser import parse
from datetime import datetime 

#%%
###### This script aims to find the list of available dates
# on the Congressional Record Site.
url = 'https://www.congress.gov/congressional-record/117th-congress/browse-by-date' 


results = requests.get(url).text
soup = BeautifulSoup(results, 'html.parser')

# Let's see what we've got for soup today!
# print(soup.prettify())




#%%
def clean_date_text(soup):
    '''
    This function takes soup from beautiful soup and:
        1. Gets the text
        2. Converts it into a list based on splitlines
        3. Finds all of the lines after 'Browse by Date'
        4. Finds all of the lines that contain dates (baed on having a record version No.)
        5. Removes record version No. and formats dates appropriately

    Parameters
    ----------
    soup : BeautifulSoup object
        Comes from the webpage:
            https://www.congress.gov/congressional-record/117th-congress/browse-by-date

    Returns
    -------
    dates_cleaned : list of date strings
        These are the list of dates that appear on the aforementioned URL

    '''
    # Split text
    split_text = soup.get_text().splitlines()
    
    # Remove blank lines and replace multiple whitepsace charactesr with single spaces
    split_text = [re.sub(r'\s+', ' ', string) for string in split_text if string != '']
    
    # Our dates only appear after the entry 'Browse by Date' string
    date_idx = [idx for idx, string in enumerate(split_text) if string.lower() == 'browse by date']#re.findall('browse by date', string.lower())]
    
    # Pull all the values in our split_text after this index
    date_text = split_text[date_idx[0]:]
    
    
    # It appears that the dates are always succeeded by the version number of the record
    # (i.e. No. 76)
    dates = [text for text in date_text if re.findall('No\. \d', text)]
    
    # Dates are in the format of "January 01, 2021" and need to be converted
    # to proper datetime. We also need to remove the version number of the record
    dates_cleaned = [datetime.strptime(date.split(' -')[0], "%B %d, %Y").date().strftime("%Y-%m-%d") for date in dates]
    
    return dates_cleaned

# print(clean_date_text(soup))