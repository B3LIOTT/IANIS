from transformers.utils import TRANSFORMERS_CACHE
import shutil
import os

# Chemin du cache pour le modèle BGE
model_name = "BAAI/bge-base-en-v1.5"
model_cache_dir = os.path.join(TRANSFORMERS_CACHE, "models--" + model_name.replace("/", "--"))

# Supprimer le dossier du modèle si existant
if os.path.exists(model_cache_dir):
    shutil.rmtree(model_cache_dir)
    print(f"Modèle {model_name} supprimé du cache")
else:
    print(f"Modèle {model_name} non trouvé dans le cache")