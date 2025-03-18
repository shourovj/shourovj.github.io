from pelican import signals
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)

INFOBOX_TYPES = {
    'NOTE': 'infobox-note',
    'WARNING': 'infobox-warning',
    'TIP': 'infobox-tip'
}

def process_infoboxes(content):
    if not hasattr(content, '_content'):
        return

    soup = BeautifulSoup(content._content, 'html.parser')
    blockquotes = soup.find_all('blockquote')
    
    for blockquote in blockquotes:
        # Get the first paragraph or text content
        first_line = blockquote.get_text().strip().split('\n')[0]
        
        # Check for GitHub-style admonition syntax
        match = re.match(r'\[!(\w+)\]', first_line)
        if match:
            type_id = match.group(1).upper()
            if type_id in INFOBOX_TYPES:
                logger.info(f"Found {type_id} infobox")
                
                # Add the infobox class
                blockquote['class'] = blockquote.get('class', []) + ['infobox', INFOBOX_TYPES[type_id]]
                
                # Remove the [!TYPE] line
                first_p = blockquote.find('p')
                if first_p:
                    text = first_p.get_text()
                    new_text = re.sub(r'\[!\w+\]\s*\n?', '', text, 1)
                    first_p.string = new_text

    content._content = str(soup)

def register():
    logger.info("Registering infobox plugin")
    signals.content_object_init.connect(process_infoboxes) 