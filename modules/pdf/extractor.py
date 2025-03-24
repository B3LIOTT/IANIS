import re
import fitz  # PyMuPDF
from collections import defaultdict


class PDFStructureAnalyzer:
    """
    Classe pour extraire et analyser la structure d'un document PDF.
    Permet de détecter les parties, sections, sous-sections et énoncés.
    """
    
    def __init__(self, pdf_path):
        """Initialise l'analyseur avec le chemin du fichier PDF."""
        self.pdf_path = pdf_path
        self.text_content = ""
        self.pages_content = []
        self.structure = {}
        self.sections = []
        self.section_levels = {}
        self.font_stats = defaultdict(list)
        self.statements = []
    
    def extract_with_pymupdf(self):
        """
        Extrait le texte avec PyMuPDF (fitz) qui préserve mieux la mise en forme
        et fournit des informations sur les styles.
        """
        self.pages_content = []
        self.font_sizes = []
        
        doc = fitz.open(self.pdf_path)
        
        for page_num, page in enumerate(doc):
            # Extraire le texte de la page
            text = page.get_text()
            self.pages_content.append(text)
            
            # Collecter des informations sur les polices pour l'analyse structurelle
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            font_size = span["size"]
                            font_name = span["font"]
                            text = span["text"]
                            if text.strip():  # Ignorer le texte vide
                                self.font_stats[(font_name, font_size)].append(text)
        
        self.text_content = '\n'.join(self.pages_content)
        return self.text_content
    
    def identify_titles_by_font(self):
        """
        Identifie les titres potentiels en fonction des caractéristiques des polices.
        Les titres ont généralement des tailles de police distinctes et plus grandes.
        """
        # Calculer la fréquence et les statistiques de chaque combinaison de police/taille
        font_info = {}
        for (font_name, size), texts in self.font_stats.items():
            total_length = sum(len(text) for text in texts)
            avg_length = total_length / len(texts) if texts else 0
            font_info[(font_name, size)] = {
                'count': len(texts),
                'avg_length': avg_length,
                'examples': texts[:3]  # Quelques exemples pour l'inspection
            }
        
        # Trier par taille de police (décroissante)
        sorted_fonts = sorted(font_info.items(), key=lambda x: x[0][1], reverse=True)
        
        # Identifier les niveaux de titre probables
        title_levels = {}
        for i, ((font_name, size), info) in enumerate(sorted_fonts[:5]):  # Considérer les 5 plus grandes tailles
            if info['avg_length'] < 100:  # Les titres sont généralement courts
                title_levels[(font_name, size)] = i + 1  # Niveau 1, 2, 3, etc.
        
        return title_levels, font_info
    
    def detect_sections_by_regex(self):
        """
        Détecte les sections en utilisant des expressions régulières pour identifier
        les modèles de numérotation courants dans les documents.
        """
        # Différents modèles de titres de section
        patterns = [
            # Format: "1. Titre de section"
            (r'^\s*(\d+)\.\s+([A-Z][\w\s\-\',:]+)$', 1),
            # Format: "1.1 Titre de sous-section"
            (r'^\s*(\d+\.\d+)\s+([A-Z][\w\s\-\',:]+)$', 2),
            # Format: "1.1.1 Titre de sous-sous-section"
            (r'^\s*(\d+\.\d+\.\d+)\s+([A-Z][\w\s\-\',:]+)$', 3),
            # Format: "I. Titre de section (chiffres romains)"
            (r'^\s*(I{1,3}|IV|V|VI{1,3}|IX|X)\.\s+([A-Z][\w\s\-\',:]+)$', 1),
            # Format: "A. Titre de section (lettres)"
            (r'^\s*([A-Z])\.\s+([A-Z][\w\s\-\',:]+)$', 1),
        ]
        
        sections = []
        section_levels = {}
        
        # Parcourir chaque ligne du document
        for line_num, line in enumerate(self.text_content.split('\n')):
            line = line.strip()
            if not line:
                continue
                
            # Vérifier si la ligne correspond à un modèle de titre
            for pattern, level in patterns:
                match = re.match(pattern, line)
                if match:
                    section_id = match.group(1)
                    section_title = match.group(2).strip()
                    sections.append({
                        'id': section_id,
                        'title': section_title,
                        'level': level,
                        'line': line_num
                    })
                    self.structure[section_title] = []
                    break

        self.sections = sections

    def detect_statements(self):
        """
        Détecte les énoncés dans le document en recherchant des motifs courants
        comme "E1:", "VULN-1:", etc.
        """
        # Différents modèles possibles d'énoncés
        statement_patterns = [
            r'^\s*([A-Z0-9][\w\-]+)\s*[:. ]\s*(.*?)$',
            #r'^\s*([A-Z0-9][\w\-]+)\s*:\s*(.*?)$',
        ]
        
        statements = []
        
        # Parcourir chaque ligne pour trouver des énoncés
        lines = self.text_content.split('\n')
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Vérifier si la ligne correspond à un format d'énoncé
            for pattern in statement_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                print(match)
                if match:
                    statement_id = match.group(1)
                    statement_text_start = match.group(2)
                    
                    # Initialiser le texte de l'énoncé avec la première ligne
                    full_statement_text = statement_text_start
                    
                    # Chercher si l'énoncé continue sur les lignes suivantes
                    current_line = line_num + 1
                    while current_line < len(lines):
                        next_line = lines[current_line].strip()
                        
                        # Arrêter si on trouve un autre énoncé ou une section
                        is_new_statement = any(re.match(p, next_line, re.IGNORECASE) for p in statement_patterns)
                        is_section = any(re.match(p[0], next_line) for p in self.section_patterns) if hasattr(self, 'section_patterns') else False
                        
                        if is_new_statement or is_section or not next_line:
                            break
                            
                        # Ajouter la ligne au texte de l'énoncé
                        full_statement_text += "\n" + next_line
                        current_line += 1
                    
                    # Déterminer à quelle section appartient cet énoncé
                    section_id = None
                    section_title = None
                    for i, section in enumerate(self.sections):
                        if line_num >= section['line']:
                            if i == len(self.sections) - 1 or line_num < self.sections[i+1]['line']:
                                section_id = section['id']
                                section_title = section['title']
                                break
                    
                    # hotfix
                    if section_title == None: 
                        section_title = 'None'
                        if section_title not in self.structure: self.structure[section_title] = []

                    self.structure[section_title].append({
                        'id': statement_id,
                        'text': full_statement_text.strip(),
                        'line': line_num,
                    })
                    
                    break  # Sortir de la boucle des patterns après avoir trouvé une correspondance
    
    def extract_sections_content(self):
        """
        Extrait le contenu de chaque section identifiée.
        """
        if not self.sections:
            self.detect_sections_by_regex()
            
        sections_content = {}
        lines = self.text_content.split('\n')
        
        # Parcourir les sections identifiées
        for i, section in enumerate(self.sections):
            start_line = section['line']
            # Déterminer la ligne de fin (soit la prochaine section, soit la fin du document)
            end_line = self.sections[i+1]['line'] if i < len(self.sections) - 1 else len(lines)
            
            # Extraire le contenu de la section
            content = '\n'.join(lines[start_line+1:end_line])
            sections_content[section['id']] = {
                'title': section['title'],
                'content': content,
                'level': section['level']
            }
            
        return sections_content
    
    def analyze_pdf_structure(self):
        """
        Méthode principale qui exécute l'analyse complète du PDF.
        """
        # Data extraction
        self.extract_with_pymupdf()
        
        # Titles info
        title_levels, font_info = self.identify_titles_by_font()
        
        # Detect sections
        self.detect_sections_by_regex()

        # Detect statements
        self.detect_statements()
        
        return self.structure


def extract_pdf(pdf_path):
    """Fonction pour traiter un PDF et afficher sa structure avec les énoncés."""
    analyzer = PDFStructureAnalyzer(pdf_path)
    structure = analyzer.analyze_pdf_structure()
    
    print(structure)
    return structure

