import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
from reportlab.lib.colors import *
import textwrap
from reportlab.lib.units import inch
from PIL import Image

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Lire le fichier JSON
with open('discussion.json', 'r') as file:
    discussion = json.load(file)



# Récupérer la liste unique des auteurs
authors = set(message['sender_name'] for message in discussion['messages'])

# Générer une couleur aléatoire pour chaque auteur
authors_list = list(authors)
author_colors = {authors_list[0]: "#4653c3", authors_list[1]: "#282445"}

# Créer le PDF
pdf = canvas.Canvas("discussion.pdf", pagesize=letter)
width, height = letter

# Enregistrez la police
pdfmetrics.registerFont(TTFont('SegoeUI','Segoe UI Emoji.ttf'))

# Ajouter un titre
pdf.setFont('SegoeUI', 30)  # Définir la taille de la police pour le titre
pdf.drawString(100, height - 70, "Transcript - " + authors.pop() + " and " + authors.pop())

# Utilisez la police
pdf.setFont('SegoeUI', 15)  # Remplacez 12 par la taille de police que vous souhaitez utiliser

# Définir une position de départ
y_position = height - 100

# Largeur maximale pour le texte
max_text_width = int(width - 550) # Ajustez cette valeur en fonction de vos besoins


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

        current_time=timestamp
        current_time = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")

        # Diviser le texte en plusieurs lignes si nécessaire
        wrapped_text = textwrap.wrap(texte, width=max_text_width)

        for line in wrapped_text:
            # Si l'auteur du message a changé, faire un saut de ligne plus grand
            if previous_sender != auteur:
                y_position -= 25  # Ajustez cette valeur en fonction de vos besoins
            elif previous_time and current_time - previous_time > timedelta(hours=1):
                y_position -= 25

            pdf.drawString(100, y_position, line)

            # Mise à jour du temps du dernier message
            previous_time = current_time

            # Mettre à jour la position pour le prochain message
            y_position -= 20

            # Ajouter une nouvelle page si nécessaire
            if y_position < 50:
                pdf.showPage()
                pdf.setFillColor(color)
                pdf.setFont('SegoeUI', 15)
                y_position = height - 50

            # Mettre à jour le nom de l'auteur du message précédent
            previous_sender = auteur

        # Vérifier si le message contient des photos
        photos = message.get('photos', [])
        for photo in photos:
            # Récupérer l'URI de la photo
            photo_uri = photo['uri']

            # Dessiner l'image dans le PDF
            # Remplacez '100' et 'y_position' par les coordonnées où vous souhaitez dessiner l'image
            # Remplacez '1*inch' et '1*inch' par la largeur et la hauteur souhaitées de l'image
            with Image.open(photo_uri) as img:
                img_width, img_height = img.size

            # Convertir les dimensions en points (la bibliothèque PDF utilise des points comme unité de mesure, 1 point = 1/72 pouces)
            width_points = img_width / 72 * 10
            height_points = img_height / 72 * 10

            if y_position < 50 + height_points:
                pdf.showPage()
                pdf.setFillColor(color)
                pdf.setFont('SegoeUI', 15)
                y_position = height - 50

            # Dessiner l'image avec ses dimensions originales
            pdf.drawImage(photo_uri, 100, y_position - height_points, width_points, height_points)

            # Mettre à jour la position pour la prochaine image ou le prochain message
            y_position -= height_points + 35

            # Ajouter une nouvelle page si nécessaire
            if y_position < 50:
                pdf.showPage()
                pdf.setFillColor(color)
                pdf.setFont('SegoeUI', 15)
                y_position = height - 50



# Sauvegarder le PDF
pdf.save()