#%%
# load previously generated json file for a particular CR date 
import json
import os
import errno
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import nltk
import re

#%%
dateString = 'CREC-2021-02-24'
cr_json_filepath = 'json_output/' + dateString + '/cr.json'

with open('json_output/CREC-2021-02-24/cr.json', "r") as file:
    cr_json = file.read()

cr_loaded_list = json.loads(cr_json)

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
    
    

# Strip whitespace and turn our text into a normal string
test = cr_loaded_list[35]['raw_text']

print(clean_section(test))


#%% Determine title
def determine_title(section):
    '''

    Parameters
    ----------
    section : long string
        string of text representing a section in the congressional crecord

    Returns
    -------
    split_text[0]: string
        the title of the text, which is also the first line in the text

    '''
    
    # Find the first phrase before the new line
    split_text = section.splitlines()
    
    # It'll be the first item in the list
    return split_text[0]


print(determine_title(clean_section(test)))
    
    




#%%
# Let's see how it looks if we load the data in as a pandas dataframe
df = pd.read_json(cr_json_filepath)

# Put the date as a column in our dataframe
split_date = dateString.split('.')[0].split('-')
df['session'] = split_date[1] + '-' + split_date[2] + '-' + split_date[3]

# Note: We'll have to 'explode' the speakers column to unlist the values
df = df.explode('speakers')

print(df.head())
print("\n==================================\n")
print(df.iloc[25, 2])


#%%
# Let's do some basic EDA just to get a sense of what's possible.
speaker_counts = df \
    .groupby(['speakers']) \
    .size() \
    .reset_index(name = 'count') \
    .sort_values('count', ascending = False) \
    .reset_index(drop = True)
    
print(speaker_counts.head(10))



#%% Tokenization
# Let's tokenize our raw_text column to get a better sense of which words are
# most common. First we'll break each sentence into a list of words, and then
# "explode" that list to pivot our dataframe longer.
df_pivoted = df.copy()

# Replace non-words
df_pivoted['raw_text'] = df_pivoted['raw_text'].str.replace('[\W\s\d]', ' ').str.lower()

# Tokenize
df_pivoted['tokenized_text'] = df_pivoted.apply(lambda row: nltk.word_tokenize(row['raw_text']), axis=1)

# Remove stop words using nltk's english stop words corpus. Let's also remove
# words that are only 1 character (not sure why these are coming in).
from nltk.corpus import stopwords
stop = stopwords.words('english')
df_pivoted['tokenized_text'] = df_pivoted['tokenized_text'].apply(lambda row: [word for word in row if word not in stop and len(word) > 1])


# Explode our dataframe to a longer format so we can perform analytics
df_pivoted = df_pivoted.explode('tokenized_text')



#%% Lemmatization
# Because a lot of the words are similar, but not exactly (like state and states), 
# we'll use a lemmatization method to find the canonical version of each.
lemmatizer = nltk.stem.WordNetLemmatizer()

# Initialize two dataframes:
    # 1. Error DataFrame | This will keep track of any words that have issues in
    #                       the lemmatizer
    # 2. Lemmatized DataFrame | This will be a copy of our original dataframe
error_df = pd.DataFrame(columns = ['idx', 'word', 'line', 'essay'])

lemmatized_df = df_pivoted.copy().reset_index(drop = True)
lemmatized_df['lemmatized_text'] = lemmatized_df['tokenized_text'].reset_index(drop = True)

for idx, word in lemmatized_df.iterrows():
    print(f"\nRunning code on Word #{idx}:")
    
    # Try lemmatizing.
    # TODO: NLTK's lemmatizer let's you tag the part of speech. If we could bring
    # this into the dataframe, that would be HUGE.
    try:
        lemmatized_df['lemmatized_text'][idx] = lemmatizer.lemmatize(word['tokenized_text'])
    # For some words, the lemmatizer isn't working. Let's log these and revisit
    # them later
    except:
        # In the meantime, let's just keep the word as is
        lemmatized_df['lemmatized_text'][idx] = word['tokenized_text']
        
        # Log our errors
        to_append = [idx, word['tokenized_text'], word['Lines'], word['Essay']]
        a_series = pd.Series(to_append, index = error_df.columns)
        error_df = error_df.append(a_series, ignore_index=True)
    print(f"{word['tokenized_text']} --> {word['lemmatized_text']}")




#%% Text Analytics
# Now that our dataframe is in a better structure, we can do analytics on the
# text more easily. Example:
    
# Find our most common words
word_counts = df_pivoted \
    .groupby(['tokenized_text']) \
    .size() \
    .reset_index(name = 'count') \
    .sort_values('count', ascending = False) \
    .reset_index(drop = True)
    
print(f"Our top words are:\n\n{word_counts.head(25)}")
