# ----------------------------------------------------------------------------
#                                Purpose
# ----------------------------------------------------------------------------
# The purpose of this script is to analyze the text of each issue within the 
# Congresssional Record and pull both the speakers in each section and their 
# various activities


#%% Load Data and import packages
import os


def pdf_to_text(path):
    '''
    This function takes in the path for a given pdf and converts it to a string
    
    Parameters
    ----------
    path : string

    Returns
    -------
    text : long string output
    
    '''
    from io import StringIO
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfdocument import PDFDocument
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfparser import PDFParser
    
    output_string = StringIO()
    with open(path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
            
    return output_string.getvalue()

# Open the pdf
path = os.getcwd() + '/2. Text Analysis/'
pdf_name = os.listdir(path)[2]

# Run the function above using our path
pdf_text = pdf_to_text(path + pdf_name)


#%%
number_of_lines = len(pdf_text)
# print(pdf_text[0:number_of_lines])


def count_speakers(text):
    '''
    This functions creates a dictionary of the speakers in a session and the number
    number of times they speak. As of now, this function just finds the number
    of times the congressperson is mentioned in the text. More will need to be added
    to figure out what they're talking about.
    
    Parameters
    ----------
    text : string

    Returns
    -------
    sorted_speakers : dictionary(key = speaker, value = # of times speaking)
    
    '''
    # Import packages
    import re
    import collections
    
    # Use regex to find all of the male Congresspeopele (always referred to as
    # 'Mr.'  or 'Ms.' followed by undetermined whitespace followed by their name)
    speaker_pattern = re.compile(r"""
                            (?:Mr.|Ms.) # It starts either with 'Mr.' or 'Ms.'
                            \s*   # Followed by undeteremined whitespace
                            ([A-Za-z]*) # Then any one-word text. Note: This screws us if a Congress person has a double last name (i.e. Watson Coleman)
                            """,
                            re.VERBOSE
                            )
                            
    # Find all of our matches. Because of the way we structured this,
    # it will return a list.
    #   Ex: ['COSTA', 'BLUMENAUER']
    speaker_matches = re.findall(speaker_pattern, text)
    
    # Our names are ALL CAPS so let's convert them to_title and remove '' 
    # from the list of speakers
    speaker_matches = [x.title() for x in speaker_matches if x != '']
    
    # Let's count the occurrences of each speaker and put this into a dictionary
    speaker_counts = collections.defaultdict()
    speaker_counts = {speaker: speaker_matches.count(speaker) for speaker in speaker_matches}
    
    # Let's sort our dictionary so it's easier to parse through
    sorted_speakers = dict(sorted(speaker_counts.items(), key = lambda kv: kv[1]))

    return sorted_speakers   


# Run our function
speaker_counts = count_speakers(pdf_text[0:number_of_lines])

print(speaker_counts)
