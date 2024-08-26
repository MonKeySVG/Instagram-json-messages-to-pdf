import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from reportlab.lib.colors import *
import textwrap

# Lire le fichier JSON
with open('discussion.json', 'r') as file:
    discussion = json.load(file)

# Récupérer la liste unique des auteurs
authors = set(message['sender_name'] for message in discussion['messages'])

# Générer une couleur aléatoire pour chaque auteur
author_colors = {authors.pop(): "#4653c3", authors.pop(): "#282445"}

# Créer le PDF
pdf = canvas.Canvas("discussion.pdf", pagesize=letter)
width, height = letter

# Définir une position de départ
y_position = height - 50

# Largeur maximale pour le texte
max_text_width = int(width - 530) # Ajustez cette valeur en fonction de vos besoins


# Fonction pour convertir le timestamp en date lisible
def timestamp_to_date(timestamp_ms):
    return datetime.fromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d %H:%M:%S')


# Ajouter chaque message dans le PDF
previous_sender = None  # Variable pour stocker le nom de l'auteur du message précédent

discussion['messages'].reverse()


for message in discussion['messages']:
    auteur = message['sender_name']
    timestamp = timestamp_to_date(message['timestamp_ms'])

    # Changer la couleur du texte en fonction de l'auteur
    color = author_colors.get(auteur, black)
    pdf.setFillColor(color)

    # Vérifier si le message a du contenu textuel
    contenu = message.get('content', '[Aucun texte]')  # Texte par défaut si 'content' n'existe pas

    # Remplacer le contenu par "[lien]" s'il commence par "http"
    if contenu.startswith("http"):
        contenu = "[lien]"

    # Décoder le contenu UTF-8
    contenu = contenu.encode('latin1').decode('utf8')

    # Diviser le contenu en lignes si "\n" est présent
    lignes = contenu.split('\n')

    # Ajouter le texte formaté pour chaque ligne
    for ligne in lignes:
        texte = f"[{timestamp}] {auteur} : {ligne}"

        # Diviser le texte en plusieurs lignes si nécessaire
        wrapped_text = textwrap.wrap(texte, width=max_text_width)

        for line in wrapped_text:
            # Si l'auteur du message a changé, faire un saut de ligne plus grand
            if previous_sender != auteur:
                y_position -= 25  # Ajustez cette valeur en fonction de vos besoins

            pdf.drawString(100, y_position, line)

            # Mettre à jour la position pour le prochain message
            y_position -= 20

            # Ajouter une nouvelle page si nécessaire
            if y_position < 50:
                pdf.showPage()
                pdf.setFillColor(color)
                y_position = height - 50

            # Mettre à jour le nom de l'auteur du message précédent
            previous_sender = auteur

# Sauvegarder le PDF
pdf.save()