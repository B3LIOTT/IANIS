from modules.pdf import *
from modules.analyzer import *
import os

#DIR = "tests"
DIR = "/home/debian/Documents/Wavestone/NIS2-RESA/IANIS-tests"

def main(input_text):
    # input_text = "Des outils de sauvegrade doivent etre mis en place pour restituer les données"
    # input_text = "L'accès à distance au réseau interne doit se faire via une méthode sécurisée"
    # input_text = "Le développement de logiciels doit prendre en compte la minimisation de vulénrabilités en se basant sur des vulnérabilités connues"

    paths = os.listdir(DIR)

    # find most relevant files
    mode = 1
    relevant_files = search(input_text, [path[:-4] for path in paths], mode)

    Es = {}
    Rs = {}
    for pdf_path in relevant_files:
        structure = extract_pdf(f"{DIR}/{pdf_path}.pdf")

        # premier test en mappant tous les énnoncés
        E = []
        for es in structure.values():
            for e in es:
                E.append(f"{e['id']} {e['text']}")

        Es[pdf_path] = E

        # find relevant statements
        print(pdf_path, ":")
        Rs[pdf_path] = search(input_text, E, mode)

    return Rs


def search(input_text, E, mode):
    ct = compare_texts if mode==1 else compare_texts2
    textes_similaires, scores, indexes = ct(input_text, E)
    
    for text in textes_similaires:
        print(text)
    print(f"Score de similarité : {scores}")
    print("_"*30, '\n')

    return textes_similaires
