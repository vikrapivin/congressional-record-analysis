#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  6 20:51:46 2021

@author: Owner
"""

#%% Import Packages
import requests
import urllib
from bs4 import BeautifulSoup
import json

#%%
###### This script aims to find the list of available dates
# on the Congressional Record Site.
url = 'https://www.congress.gov/congressional-record/117th-congress/browse-by-date' 

results = requests.get(url).text
soup = BeautifulSoup(results, 'html.parser')

print(soup.prettify())

#%%
# Turns out the dates are saved in one of the scripts. Let's figure out which one
scripts = soup.find_all('script')

for i, text in enumerate(scripts):
    print("\n\n\n")
    print(f"Script {i}:\n {text.string}")

#%%
# Looks like the dates are stored in Script 17
# TODO: Confirm it's script 17 for other sessions
dates = scripts[17].string.splitlines()[2]

# Remove superflous text
# cleaned_dates =...
print(dates)
