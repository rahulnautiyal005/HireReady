import logging
import os
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

logger = logging.getLogger(__name__)

def create_pdf_from_text(text, output_path):
    """
    Create a PDF document from text.
    
    Args:
        text (str): Text to convert to PDF
        output_path (str): Path where the PDF will be saved
        
    Returns:
        str: Path to the created PDF file
    """
    try:
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            title="Improved Resume"
        )
        
        # Set up styles
        styles = getSampleStyleSheet()
        normal_style = styles['Normal']
        
        # Create story (content)
        story = []
        
        # Split text by lines
        lines = text.split('\n')
        
        # Process each line
        for line in lines:
            # Skip empty lines
            if line.strip():
                # Add paragraph
                p = Paragraph(line.replace('&', '&amp;'), normal_style)
                story.append(p)
                story.append(Spacer(1, 6))  # Add some space between paragraphs
        
        # Build the PDF
        doc.build(story)
        
        logger.debug(f"Successfully created PDF from text at {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating PDF: {str(e)}")
        raise Exception(f"Failed to create PDF: {str(e)}")