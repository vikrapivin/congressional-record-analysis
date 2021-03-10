#%%
# load previously generated json file for a particular CR date 
import json
import os
import errno
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

#%%
dateString = 'CREC-2021-02-24'
cr_json_filepath = 'json_output/' + dateString + '/cr.json'

with open('/Users/Owner/Documents/Blog/congressional-record-analysis/json_output/CREC-2021-02-24/cr.json', "r") as file:
    cr_json = file.read()

cr_loaded_list = json.loads(cr_json)

#%%
# do something with the cr_loaded_list

print(cr_loaded_list[25]['raw_text'])


#%%
# Let's see how it looks if we load the data in as a pandas dataframe
df = pd.read_json(cr_json_filepath)

# Put the date as a column in our dataframe
split_date = dateString.split('.')[0].split('-')
df['session'] = split_date[1] + '-' + split_date[2] + '-' + split_date[3]

print(df.head())
print("\n==================================\n")
print(df.iloc[25, 2])

