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
cr_json_filepath = 'json_ouput/'+dateString+'/cr.json'
cr_json_file = open(cr_json_filepath, "r")
cr_json = cr_json_file.read()

cr_loaded_list = json.loads(cr_json)

#%%
# do something with the cr_loaded_list

print(cr_loaded_list[25]['raw_text'])