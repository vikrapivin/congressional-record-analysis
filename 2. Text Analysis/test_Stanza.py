"""
Test processing of the CR text with Stanza.
Run other file first
also run "!pip install stanza"
"""

#%%
# process the raw data from the CR pdf in some more ways
def remove_hyphens(input_raw_text):
    inputTemp = input_raw_text.replace('´', '')
    inputTemp = inputTemp.replace('-\n', '')
    inputTemp = inputTemp.replace('  ', ' ')
    inputTemp = inputTemp.replace('\n\n', '\hFE') # quick hack to not replace \n\n below.
    inputTemp = inputTemp.replace('\n', '')
    inputTemp = inputTemp.replace('\hFE','\n\n')
    return inputTemp


slightly_processed_text_2 = remove_hyphens(pdf_text)

#%%

import stanza
stanza.download('en') 
nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos')
doc = nlp(slightly_processed_text_2)
# uncomment below if you want to get a raw view of the results of this nlp
# print(*[f'word: {word.text}\tupos: {word.upos}\txpos: {word.xpos}\tfeats: {word.feats if word.feats else "_"}' for sent in doc.sentences for word in sent.words], sep='\n')

#%%
# look at nep models

# stanza.download('en', processors='tokenize,mwt,pos,ner') 
nlp_ner = stanza.Pipeline(lang='en', processors='tokenize,ner')
# looks like the ner processing has some trouble processing this raw text, probably due to the newlines. You can still pass it later
doc_ner = nlp_ner(slightly_processed_text_2)

#%%
# example of printing out sentences with the speaker or person referenced.
ii = 0
for sentence in doc.sentences:
    for word in sentence.words:
        if 'Mr.' == word.text or 'Ms.' == word.text:
            # if 'PROPN' in word.upos:
            if 'PROPN' in sentence.words[len(sentence.words) - 2].upos:  # is the sentence of the form Mr. name name name... .
                test = sentence
                # print(sentence)
                print(sentence.text)
                print(ii)
    if ii > 2000:
        break
    ii = ii + 1

#%%
nlp_test = stanza.Pipeline(lang='en', processors='tokenize,ner')
doc_test = nlp_test("The Chair recognizes the gentlewoman from North Carolina (Ms. FOXX) for 5 minutes.")
print(*[f'token: {token.text}\tner: {token.ner}' for sent in doc_test.sentences for token in sent.tokens], sep='\n')


#%%
def getTextFromWords(wordList):
    compString = ""
    skipSpace = True
    for word in wordList:
        if skipSpace == True:
            compString += word.text
            skipSpace = False
        elif word.text == "(":
            compString += " " + word.text
            skipSpace = True
        elif word.upos == "PUNCT":
            compString +=  word.text
        else:
            compString += " " + word.text
    return compString
# example of printing out sentences with the speaker or person who took an action.
first_scan_partition_text = []
ii = 0
areWeInOrder = False
for sentence in doc.sentences:
    jj = 0
    # add Speaker, President pro tempore, and President of the Senate, The PRESIDING OFFICER below
    # also add when a speaker is changed ie. "The SPEKAER pro tempre (Mr. Levin of Michigan),"
    if sentence.text =='The SPEAKER pro tempore.' or sentence.text == 'The ACTING PRESIDENT pro tempore.':
        print(sentence.text)
        first_scan_partition_text.append(ii)
        print(ii)
    if "called to order" in sentence.text:
        areWeInOrder = True
    if "stands adjourned" in sentence.text:
        areWeInOrder = False
    if areWeInOrder == False:
        ii = ii + 1
        continue
    for word in sentence.words:
        if 'Mr.' == word.text or 'Ms.' == word.text or 'Mrs.' == word.text:
            if jj != 0:
                if getTextFromWords(sentence.words[0:jj]).isupper() == False: # start of sections included with person who is speaking first
                    break
                if sentence.text.count('Mr.') + sentence.text.count('Ms.') + sentence.text.count('Mrs.') > 1:
                    break
                if 'submitted the following resolution' in doc.sentences[ii+1].text:
                    break
            thisIsAnotherMember = False
            try:
                if 'PROPN' in sentence.words[len(sentence.words) - 2].upos and sentence.words[jj+1].text.isupper() == True:# is the sentence of the form Mr. name name name... proper noun.
                    thisIsAnotherMember = True
                    # proper noun above can also be a state name
                # elif sentence.words[jj+1].text.isupper() == True: # an exception when a member is referenced by that member did not talk
                #     thisIsAnotherMember = True
                #     # in this case here we get a bug with saying which vote a member changed their vote to, but not what they changed it to 
                #     # this is a pdf read bug
                # elif 'tempore' in sentence.words[len(sentence.words) - 2].text:  
                #     thisIsAnotherMember = True
            except IndexError:
                pass
            if thisIsAnotherMember == True:
                # test = sentence
                # print(sentence)
                # print(sentence.text)
                # if sentence.words[jj+2].text != '.' and sentence.words[jj+2].text != 'of' :
                #     continue
                try:
                    if sentence.words[jj+2].text ==',':
                        continue
                except IndexError:
                    pass
                print(sentence.text)
                first_scan_partition_text.append(ii)
                print(ii)    
                # nlp_temp = stanza.Pipeline(lang='en', processors='tokenize,ner')
                # ner_process = nlp_temp(getTextFromWords(doc.sentences[ii-1].words) + " " + getTextFromWords(sentence.words))
                # print(getTextFromWords(doc.sentences[ii-1].words) + " " + getTextFromWords(sentence.words))
                # print(ner_process.sentences[1].tokens[jj+1].ner)
            break
        jj = jj + 1
    # if ii > 2000:
    #     break
    ii = ii + 1

# quick breaking speakers into sections above, everything between an ii and the next ii


#%%
compString = ""
skipSpace = True
for word in doc.sentences[1826].words:
    if skipSpace == True:
        compString += word.text
        skipSpace = False
    elif word.text == "(":
        compString += " " + word.text
        skipSpace = True
    elif word.upos == "PUNCT":
        compString +=  word.text
    else:
        compString += " " + word.text
print(compString)