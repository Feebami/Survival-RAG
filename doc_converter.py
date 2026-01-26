import os

from docling.document_converter import DocumentConverter

converter = DocumentConverter()

# Get sources from corpus
for file in os.listdir('corpus'):
    if file.endswith('.pdf'):
        source = os.path.join('corpus', file)
        output = source.replace('.pdf', '.md')

        doc = converter.convert(source).document

        # Save to Markdown
        with open(output, 'w', encoding='utf-8') as f:
            f.write(doc.export_to_markdown())