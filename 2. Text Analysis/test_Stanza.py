"""
Test processing of the CR text with Stanza.
Run other file first
also run "!pip install stanza"
"""

#%%
# process the raw data from the CR pdf in some more ways
def remove_hyphens(input_raw_text):
    return input_raw_text.replace('-\n', '')            


slightly_processed_text = remove_hyphens(pdf_text)

#%%

import stanza
stanza.download('en') 
nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos')
doc = nlp(slightly_processed_text)
# uncomment below if you want to get a raw view of the results of this nlp
# print(*[f'word: {word.text}\tupos: {word.upos}\txpos: {word.xpos}\tfeats: {word.feats if word.feats else "_"}' for sent in doc.sentences for word in sent.words], sep='\n')

#%%

# example of printing out sentences with the speaker or person who took an action.
for sentence in doc.sentences:
    for word in sentence.words:
        if 'Mr' in word.text:
            # if 'PROPN' in word.upos:
            if 'PROPN' in sentence.words[len(sentence.words) - 2].upos:  # is the sentence of the form Mr. name name name... .
                test = sentence
                # print(sentence)
                print(sentence.text)
