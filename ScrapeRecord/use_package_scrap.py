#%%
# example of how to use the new cr_scraper_parse_cr "pkg"
# make sure that you are in the root directory of the repo
import cr_scraper.parse_cr as crp
from tqdm import tqdm
import time
from ScrapeRecord import get_dates_script

#%%
# Get our soup from the Congressional Record Site
url = 'https://www.congress.gov/congressional-record/117th-congress/browse-by-date' 


results = requests.get(url).text
soup = BeautifulSoup(results, 'html.parser')

# Pull dates using our custom function
dates = get_dates_script.clean_date_text(soup)


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
