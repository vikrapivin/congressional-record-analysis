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
number_of_lines = 1500
print(pdf_text[0:number_of_lines])


def count_speakers(text):
    '''
    This functions creates a dictionary of the speakers in a session and the number
    number of times they speak. As of now, this function just finds the number
    of times the congressperson is mentioned in the text
    
    Parameters
    ----------
    text : string

    Returns
    -------
    speaker_dict : dictionary(key = speaker, value = # of times speaking)
    
    '''
    # Import packages
    import re
    
    # Use regex to find all of the male Congresspeopele (always referred to as
    # 'Mr.'  or 'Ms.' followed by undetermined whitespace followed by their name)
    mr_pattern = r'(Mr.)\s*([A-Za-z]*)'
    mr_matches = re.findall(mr_pattern, text)
    
    return mr_matches

print(count_speakers(pdf_text[0:number_of_lines]))
