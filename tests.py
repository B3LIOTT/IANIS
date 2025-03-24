from modules.pdf import *
from modules.analyzer import *
import os

DIR = "/home/b3liott/Documents/Wavestone/Nis2RESA/IANIS-tests"
pdf_path = "POL-SEC-Gestion des vulnérabilités 2.0"
#pdf_path = "Politique de sécurité applicable aux tiers"

# structure = extract_pdf(f"{DIR}/{pdf_path}.pdf")

import PyPDF2
import re

def pdf_to_text(pdf_path, output_txt):
    # Open the PDF file in read-binary mode
    with open(pdf_path, 'rb') as pdf_file:
        # Create a PdfReader object instead of PdfFileReader
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Initialize an empty string to store the text
        text = ''

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()

    STATEMENT_NAME = "VULN"
    pattern = rf'^\s*({STATEMENT_NAME}-?[0-9]+)\s*[:. ]\s*(.*?)$' 
    
    print(text.split('\n'))



pdf_to_text(DIR + '/' + pdf_path + '.pdf', 'tests/ok.txt')