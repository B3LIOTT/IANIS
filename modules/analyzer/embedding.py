import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import torch
from transformers import AutoTokenizer, AutoModel


def load_model(model_name="sentence-transformers/distiluse-base-multilingual-cased-v2"):
    """
    Charge le modèle de génération d'embeddings et son tokenizer.
    
    Args:
        model_name: Nom du modèle à utiliser (par défaut un modèle multilingue)
        
    Returns:
        tokenizer, model: Le tokenizer et le modèle chargés
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    return tokenizer, model


def get_embedding(text, tokenizer, model):
    """
    Génère l'embedding d'un texte donné.
    
    Args:
        text: Le texte à transformer en embedding
        tokenizer: Le tokenizer du modèle
        model: Le modèle de génération d'embeddings
        
    Returns:
        embedding: Vecteur d'embedding normalisé
    """
    # Tokenisation avec gestion de la longueur maximale
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt", max_length=512)
    
    # Génération de l'embedding
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Utilisation des embeddings de la dernière couche cachée
    embeddings = outputs.last_hidden_state
    
    # Moyenne sur tous les tokens pour obtenir un seul vecteur par texte
    # (on peut également utiliser le token [CLS] pour certains modèles)
    embedding = torch.mean(embeddings, dim=1).squeeze().numpy()
    
    # Normalisation du vecteur (important pour la similarité cosinus)
    embedding = embedding / np.linalg.norm(embedding)
    
    return embedding


def find_most_similar(input_text, text_list, tokenizer, model, top_k=2):
    """
    Trouve les textes les plus similaires à un texte d'entrée.
    
    Args:
        input_text: Le texte d'entrée à comparer
        text_list: La liste des textes à comparer
        tokenizer: Le tokenizer du modèle
        model: Le modèle de génération d'embeddings
        top_k: Nombre de résultats similaires à retourner
        
    Returns:
        similar_indices, similarities: Indices des textes les plus similaires et leurs scores
    """
    # Génération de l'embedding du texte d'entrée
    input_embedding = get_embedding(input_text, tokenizer, model)
    
    # Génération des embeddings pour tous les textes de la liste
    text_embeddings = [get_embedding(text, tokenizer, model) for text in text_list]
    
    # Calcul des similarités cosinus
    similarities = [cosine_similarity([input_embedding], [text_emb])[0][0] for text_emb in text_embeddings]
    
    # Tri des similarités par ordre décroissant
    similar_indices = np.argsort(similarities)[::-1][:top_k]
    
    return similar_indices, [similarities[i] for i in similar_indices]


def compare_texts(input_text, text_list, model_name=None):
    """
    Compare un texte d'entrée avec une liste de textes et renvoie le plus similaire.
    
    Args:
        input_text: Le texte d'entrée à comparer
        text_list: La liste des textes à comparer
        model_name: Nom du modèle à utiliser (facultatif)
        
    Returns:
        most_similar_text, similarity: Le texte le plus similaire et son score
    """
    # Chargement du modèle
    tokenizer, model = load_model(model_name) if model_name else load_model()

    # Recherche du texte le plus similaire
    similar_indices, similarities = find_most_similar(input_text, text_list, tokenizer, model)
    
    # Récupération du résultat
    # most_similar_index = similar_indices[0]
    # most_similar_text = text_list[most_similar_index]
    # similarity = similarities[0]
    
    # return most_similar_text, similarity, most_similar_index

    return [text_list[i] for i in similar_indices], similarities, similar_indices
