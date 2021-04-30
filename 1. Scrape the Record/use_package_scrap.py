#%%
# example of how to use the new cr_scraper_parse_cr "pkg"
# make sure that you are in the root directory of the repo
import cr_scraper.parse_cr as crp
from tqdm import tqdm
import time

dates = [
'2021-04-12',
'2021-04-13',
'2021-04-14',
'2021-04-15',
'2021-04-16',
'2021-04-19',
'2021-04-20',
'2021-04-21',
'2021-04-22',
'2021-04-26',
'2021-04-27',
'2021-04-28'
]

#%% Parse the Congressional Records for all dates in our list

# Record our start time
begin_time = time.time()

# Initialize an empty list to hold our results
parsedDicts = []

# Loop through all of our dates, parse each one, and append to list. Track
# progress using tqdm()
for date in tqdm(dates):
    # Print nothing so we get the progress report from each iteration
    # print(f"\nParsing code for {date}...")
    # print(f"Retrieving Congressional record for {date}...")
    parsedDict = crp.getCR('2021-02-25', returnAsJSON = False)
    parsedDicts.append(parsedDict)

    # test a particular part of the file
    print(f"\nCongressional Record {date}:")
    print(f"Title: {parsedDict[10]['title']}")
    print(f"Speaker: {parsedDict[10]['speakers'][0]}")
    print("\n")

print(f"\nFinished running code in {round(time.time() - begin_time, 0)} seconds.")
