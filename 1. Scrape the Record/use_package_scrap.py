# example of how to use the new cr_scraper_parse_cr "pkg"
# make sure that you are in the root directory of the repo
import cr_scraper.parse_cr as crp

parsedDict = crp.getCR('2021-02-25', returnAsJSON = False)

# test a particular part of the file
print(parsedDict[10]['title'])
print(parsedDict[10]['speakers'][0])