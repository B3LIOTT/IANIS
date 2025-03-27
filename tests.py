from modules.pdf import *
from modules.analyzer import *
import os
import PyPDF2
import re


DIR = "/home/b3liott/Documents/Wavestone/Nis2RESA/IANIS-tests/"
pdf_path = DIR+"POL-SEC-Gestion des vulnérabilités 2.0.pdf"

from langchain.document_loaders import PyPDFLoader

# Charger le PDF
loader = PyPDFLoader(pdf_path)
pages = loader.load()

text = ""
for page in pages:
    text += page.page_content

L = text.strip().split("\n")

patterns = [
    r'^\s*(\d+)\.?\s+([\w \']+)([\s\-\',:.]{0,4})$',         # 1. Titre de section
    r'^\s*(\d+\.\d+)\.?\s+([\w \']+)([\s\-\',:.]{0,4})$',      # 1.1. Titre de sous-section
    r'^\s*(\d+\.\d+\.\d+)\.?\s+([\w \']+)([\s\-\',:.]{0,1})$', # 1.1.1. Titre de sous-sous-section
    r'^\s*(I{1,3}|IV|V|VI{1,3}|IX|X)\.?\s+([\w \']+)([\s\-\',:.]{0,1})$', # I. Titre en chiffres romains
    r'^\s*([A-Z])\.?\s+([\w \']+)([\s\-\',:.]{0,1})$',       # A. Titre en lettres
]

for line in L:
    for pattern in patterns:
        match = re.match(pattern, line)
        if match:
            print(f"Match found: {match.group(0)}")

