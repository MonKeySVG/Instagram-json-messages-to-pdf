import json
import textwrap
from datetime import datetime, timedelta
from PIL import Image
from reportlab.lib import pagesizes
from reportlab.lib.colors import *
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Ask the user for the type of PDF they want
choice = input("Do you want a PDF with a continuous page (type 'c') or a normal paginated system (type 'n')? ")

# Formatting variables
line_spacing = 20
big_line_spacing = 25
margin_top = 100
margin_left = 75
y_position = margin_top
max_text_width = 0  # Will be defined later

# Loading JSON data
with open('discussion.json', 'r') as file:
    discussion = json.load(file)

# Create the list of authors and associated colors
authors = set(message['sender_name'] for message in discussion['messages'])
authors_list = list(authors)
author_colors = {authors_list[0]: "#4653c3", authors_list[1]: "#282445"}

if choice == 'c':
    # Calculate the total height needed for a continuous page
    total_height = margin_top
    for message in discussion['messages']:
        content = message.get('content', '[No text]').encode('latin1').decode('utf8')
        lines = content.split('\n')
        for line in lines:
            wrapped_text = textwrap.wrap(line, width=85)
            total_height += line_spacing
        total_height += big_line_spacing

        photos = message.get('photos', [])
        for photo in photos:
            with Image.open(photo['uri']) as img:
                img_width, img_height = img.size
            total_height += (img_height / 72 * 10) + 35

    # PDF configuration for a continuous page
    pdf = canvas.Canvas("discussion_continuous_" + authors_list[0] + "_" + authors_list[1] + ".pdf", pagesize=(612, total_height))
    width = 612
    height = total_height
    y_position = height - 100
    max_text_width = int(width - 540)

else:
    # PDF configuration for normal pages
    pdf = canvas.Canvas("discussion_paged_" + authors_list[0] + "_" + authors_list[1] + ".pdf", pagesize=pagesizes.A4)
    width, height = pagesizes.A4
    y_position = height - 100
    max_text_width = int(width - 530)

# Register the font
pdfmetrics.registerFont(TTFont('SegoeUI', 'Segoe UI Emoji.ttf'))

# Function to convert timestamps to readable dates
def timestamp_to_date(timestamp_ms):
    return datetime.fromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d %H:%M:%S')

# Set up the PDF title
pdf.setFont('SegoeUI', 30)
pdf.drawString(margin_left, height - 70, "Transcript - " + authors_list[0] + " and " + authors_list[1])
pdf.setFont('SegoeUI', 15)

# Reverse the messages to start with the oldest
discussion['messages'].reverse()

previous_sender = None
previous_time = None

# Loop through each message in the discussion
for message in discussion['messages']:
    author = message['sender_name']
    timestamp = timestamp_to_date(message['timestamp_ms'])
    color = author_colors.get(author, black)
    pdf.setFillColor(color)

    content = message.get('content', '[No text]')

    # Replace links with a generic mention
    if content.startswith("http"):
        content = "[link]"

    # Encode content in UTF-8 to avoid errors
    content = content.encode('latin1').decode('utf8')

    # Handle text lines
    lines = content.split('\n')
    for line in lines:
        text = f"[{timestamp}] {author} : {line}"
        current_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        wrapped_text = textwrap.wrap(text, width=max_text_width)

        for line in wrapped_text:
            if previous_sender != author or (previous_time and current_time - previous_time > timedelta(hours=1)):
                y_position -= big_line_spacing

            pdf.drawString(margin_left, y_position, line)
            y_position -= line_spacing

            # Create a new page if space is insufficient (for normal mode)
            if y_position < 50 and choice != 'c':
                pdf.showPage()
                pdf.setFillColor(color)
                pdf.setFont('SegoeUI', 15)
                y_position = height - 50

            previous_sender = author
            previous_time = current_time

    # Handle photos attached to the message
    photos = message.get('photos', [])
    for photo in photos:
        photo_uri = photo['uri']

        with Image.open(photo_uri) as img:
            img_width, img_height = img.size

        # Convert image size to points
        width_points = img_width / 72 * 10
        height_points = img_height / 72 * 10

        if y_position < 50 + height_points and choice != 'c':
            pdf.showPage()
            pdf.setFillColor(color)
            pdf.setFont('SegoeUI', 15)
            y_position = height - 50

        pdf.drawImage(photo_uri, margin_left, y_position - height_points, width_points, height_points)
        y_position -= height_points + 35

        if y_position < 50 and choice != 'c':
            pdf.showPage()
            pdf.setFillColor(color)
            pdf.setFont('SegoeUI', 15)
            y_position = height - 50

# Save the PDF
pdf.save()
