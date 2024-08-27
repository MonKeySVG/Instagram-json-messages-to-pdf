import json
import textwrap
from datetime import datetime, timedelta
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import *
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Demande à l'utilisateur le type de PDF souhaité
choice = input("Voulez-vous un PDF avec une page continue (tapez 'c') ou un système de pages normales (tapez 'n') ? ")

# Variables de mise en forme
line_spacing = 20
big_line_spacing = 25
margin_top = 100
y_position = margin_top
max_text_width = 0  # Sera défini plus tard

# Chargement des données JSON
with open('discussion.json', 'r') as file:
    discussion = json.load(file)

if choice == 'c':
    # Calculer la hauteur totale nécessaire pour une page continue
    total_height = margin_top
    for message in discussion['messages']:
        contenu = message.get('content', '[Aucun texte]').encode('latin1').decode('utf8')
        lignes = contenu.split('\n')
        for ligne in lignes:
            wrapped_text = textwrap.wrap(ligne, width=85)
            total_height += line_spacing
        total_height += big_line_spacing

        photos = message.get('photos', [])
        for photo in photos:
            with Image.open(photo['uri']) as img:
                img_width, img_height = img.size
            total_height += (img_height / 72 * 10) + 35

    # Configuration du PDF pour une page continue
    pdf = canvas.Canvas("discussion_continuous.pdf", pagesize=(612, total_height))
    width = 612
    height = total_height
    y_position = height - 100
    max_text_width = int(width - 550)

else:
    # Configuration du PDF pour des pages normales
    pdf = canvas.Canvas("discussion_paged.pdf", pagesize=letter)
    width, height = letter
    y_position = height - 100
    max_text_width = int(width - 550)

# Enregistrement de la police
pdfmetrics.registerFont(TTFont('SegoeUI', 'Segoe UI Emoji.ttf'))

# Création de la liste des auteurs et des couleurs associées
authors = set(message['sender_name'] for message in discussion['messages'])
authors_list = list(authors)
author_colors = {authors_list[0]: "#4653c3", authors_list[1]: "#282445"}

# Fonction pour convertir les timestamps en dates lisibles
def timestamp_to_date(timestamp_ms):
    return datetime.fromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d %H:%M:%S')

# Configuration du titre du PDF
pdf.setFont('SegoeUI', 30)
pdf.drawString(100, height - 70, "Transcript - " + authors.pop() + " and " + authors.pop())
pdf.setFont('SegoeUI', 15)

# Inverser les messages pour commencer par le plus ancien
discussion['messages'].reverse()

previous_sender = None
previous_time = None

# Parcourir chaque message dans la discussion
for message in discussion['messages']:
    auteur = message['sender_name']
    timestamp = timestamp_to_date(message['timestamp_ms'])
    color = author_colors.get(auteur, black)
    pdf.setFillColor(color)

    contenu = message.get('content', '[Aucun texte]')

    # Remplacer les liens par une mention générique
    if contenu.startswith("http"):
        contenu = "[lien]"

    # Encodage du contenu en UTF-8 pour éviter les erreurs
    contenu = contenu.encode('latin1').decode('utf8')

    # Gérer les lignes de texte
    lignes = contenu.split('\n')
    for ligne in lignes:
        texte = f"[{timestamp}] {auteur} : {ligne}"
        current_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        wrapped_text = textwrap.wrap(texte, width=max_text_width)

        for line in wrapped_text:
            if previous_sender != auteur or (previous_time and current_time - previous_time > timedelta(hours=1)):
                y_position -= big_line_spacing

            pdf.drawString(100, y_position, line)
            y_position -= line_spacing

            # Créer une nouvelle page si l'espace est insuffisant (pour le mode normal)
            if y_position < 50 and choice != 'c':
                pdf.showPage()
                pdf.setFillColor(color)
                pdf.setFont('SegoeUI', 15)
                y_position = height - 50

            previous_sender = auteur
            previous_time = current_time

    # Gérer les photos attachées au message
    photos = message.get('photos', [])
    for photo in photos:
        photo_uri = photo['uri']

        with Image.open(photo_uri) as img:
            img_width, img_height = img.size

        # Convertir la taille de l'image en points
        width_points = img_width / 72 * 10
        height_points = img_height / 72 * 10

        if y_position < 50 + height_points and choice != 'c':
            pdf.showPage()
            pdf.setFillColor(color)
            pdf.setFont('SegoeUI', 15)
            y_position = height - 50

        pdf.drawImage(photo_uri, 100, y_position - height_points, width_points, height_points)
        y_position -= height_points + 35

        if y_position < 50 and choice != 'c':
            pdf.showPage()
            pdf.setFillColor(color)
            pdf.setFont('SegoeUI', 15)
            y_position = height - 50

# Sauvegarder le PDF
pdf.save()
