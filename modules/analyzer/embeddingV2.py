import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import torch
from transformers import AutoTokenizer, AutoModel

MODEL = "BAAI/bge-large-en-v1.5"


def load_model(model_name):
    """
    Loads the embedding model and its tokenizer.
    
    The BGE (BAAI General Embedding) model is specifically designed for 
    generating high-quality text embeddings optimized for retrieval tasks.
    
    Args:
        model_name: Name of the model to use (default is BGE English base model)
        
    Returns:
        tokenizer, model: The loaded tokenizer and model
    """
    print(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    return tokenizer, model

def get_embedding(text, tokenizer, model):
    """
    Generates an embedding for a given text using the BGE model.
    
    The BGE model works best with a specific instruction prefix for retrieval tasks.
    This function adds this prefix and processes the text properly.
    
    Args:
        text: The text to transform into an embedding
        tokenizer: The model's tokenizer
        model: The embedding generation model
        
    Returns:
        embedding: Normalized embedding vector
    """
    # BGE models work best with an instruction prefix for retrieval tasks
    instruction = "Represent this sentence for searching relevant passages: "
    
    # Prepend instruction to the text if it's not already included
    if not text.startswith(instruction):
        text = instruction + text
    
    # Tokenize with handling of maximum length
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt", max_length=512)
    
    # Generate embedding
    with torch.no_grad():
        outputs = model(**inputs)
    
    # For BGE models, we should use the [CLS] token embedding (first token)
    # which corresponds to the first position in the last hidden state
    embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
    
    # Normalize the vector (important for cosine similarity)
    embedding = embedding / np.linalg.norm(embedding)
    
    return embedding

def find_most_similar(input_text, text_list, tokenizer, model, top_k=2):
    """
    Finds the most similar texts to an input text using BGE embeddings.
    
    Args:
        input_text: The input text to compare
        text_list: The list of texts to compare against
        tokenizer: The model's tokenizer
        model: The embedding generation model
        top_k: Number of similar results to return
        
    Returns:
        similar_indices, similarities: Indices of the most similar texts and their scores
    """
    # Generate embedding for the input text
    input_embedding = get_embedding(input_text, tokenizer, model)
    
    # Generate embeddings for all texts in the list
    text_embeddings = [get_embedding(text, tokenizer, model) for text in text_list]
    
    # Calculate cosine similarities
    similarities = [cosine_similarity([input_embedding], [text_emb])[0][0] for text_emb in text_embeddings]
    
    # Sort similarities in descending order
    similar_indices = np.argsort(similarities)[::-1][:top_k]
    
    return similar_indices, [similarities[i] for i in similar_indices]

def compare_texts2(input_text, text_list, model_name=MODEL):
    """
    Compares an input text with a list of texts and returns the most similar ones.
    
    This function serves as a high-level interface to the embedding and 
    comparison functionality, handling model loading and returning formatted results.
    
    Args:
        input_text: The input text to compare
        text_list: The list of texts to compare against
        model_name: Name of the model to use (default is BGE English base model)
        
    Returns:
        similar_texts, similarities, similar_indices: The most similar texts, 
        their similarity scores, and their indices in the original list
    """
    # Load the model
    tokenizer, model = load_model(model_name)
    
    # Find the most similar texts
    similar_indices, similarities = find_most_similar(input_text, text_list, tokenizer, model)
    
    # Return the results
    return [text_list[i] for i in similar_indices], similarities, similar_indices