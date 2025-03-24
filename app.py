from flask import Flask, render_template, request, jsonify
from ianis import main


app = Flask(__name__)

# Liste de réponses prédéfinies pour la démonstration
reponses = [
    "Voici la première réponse possible à votre question.",
    "Cette réponse est un peu plus détaillée et contient des informations supplémentaires.",
    "Cette réponse courte est directe et concise.",
]

@app.route('/')
def index():
    """Route principale qui affiche l'interface du chatbot"""
    return render_template('index.html')

@app.route('/requestMapping', methods=['POST'])
def poser_question():
    """Route qui reçoit la question et renvoie des réponses"""
    question = request.form.get('question', '')
    
    responses = main(input_text=question)
    r = []
    for k in responses.keys():
        r.append({
            "doc": str(k),
            "reps": responses[k]
        })

    return jsonify({
        'question': question,
        'reponses': r
    })

if __name__ == '__main__':
    app.run(debug=True)