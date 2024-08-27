# Instagram json export to pdf

This project generates a PDF transcript from a JSON file exported from Instagram. The JSON file should contain a discussion thread with messages and photos.

# Features

- Continuous Page Option: Create a single, long PDF page that includes all messages and images from the discussion.
- Paginated Option: Create a multi-page PDF with proper pagination, ideal for printing.
- Automatic Text Wrapping: Messages are wrapped to fit within the page margins, ensuring the content is easy to read.
- Support for Embedded Images: Photos included in the discussion are automatically inserted into the PDF.

# Requirements

- Python 3.x
- Pillow library for image handling
- reportlab library for PDF generation

You can install the necessary libraries with:


```pip install -r requirements.txt```

# Usage

1) Place your JSON discussion file (called ```message_1.json``` by default by Instagram) in the root directory of the project and name it ```discussion.json```.

2) Run the script:
```python main.py```

3) You will be prompted to choose between a continuous PDF or a paginated PDF:
   - Enter c for a continuous page.
   - Enter n for a paginated document.
4) The generated PDF will be saved in the root directory as either discussion_continuous.pdf or discussion_paged.pdf.
   
# JSON Format

The discussion.json file should be formatted with the following structure (the default structure of the exported json file from Instagram):

```json
{
  "messages": [
    {
      "sender_name": "Author Name",
      "timestamp_ms": 1592436345000,
      "content": "Message content",
      "photos": [
        {
          "uri": "path/to/photo.jpg"
        }
      ]
    },
    ...
  ]
}
```


