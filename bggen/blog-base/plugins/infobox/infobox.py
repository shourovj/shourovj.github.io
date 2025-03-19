from pelican import signals
from pelican.readers import BaseReader, MarkdownReader
from pelican.utils import pelican_open
from markdown import Markdown
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)

INFOBOX_TYPES = {
    'NOTE': 'infobox-note',
    'WARNING': 'infobox-warning',
    'TIP': 'infobox-tip'
}

class MarkdownCustomInfoboxReader(MarkdownReader):
    enabled = True
    file_extensions = ['md', 'markdown', 'mkd', 'mdown']

    def read(self, source_path):
        """Parse content and metadata of markdown files"""
        with pelican_open(source_path) as text:
            # Pre-process the markdown to split blockquotes
            lines = text.split('\n')
            new_lines = []
            in_quote = False
            
            for line in lines:
                if line.startswith('>'):
                    if not in_quote:
                        in_quote = True
                    new_lines.append(line)
                    # If this is an admonition line, add an empty quote line after it
                    if '[!' in line:
                        new_lines.append('>')
                elif not line.strip() and in_quote:
                    in_quote = False
                    new_lines.append('\n&&SPLIT&&')
                    new_lines.append(line)
                else:
                    new_lines.append(line)
                    if line.strip():  # If line has content
                        in_quote = False
            
            text = '\n'.join(new_lines)

            # Convert markdown to HTML
            md = Markdown(extensions=self.settings['MARKDOWN']['extensions'],
                         extension_configs=self.settings['MARKDOWN']['extension_configs'])
            content = md.convert(text)

            # Post-process the HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove dummy split paragraphs
            for p in soup.find_all('p'):
                if p.string == '&&SPLIT&&':
                    p.decompose()
            
            # Process blockquotes for infobox styling
            blockquotes = soup.find_all('blockquote')
            for blockquote in blockquotes:
                first_line = blockquote.get_text().strip().split('\n')[0]
                match = re.match(r'\[!(\w+)\]', first_line)
                if match:
                    type_id = match.group(1).upper()
                    if type_id in INFOBOX_TYPES:
                        logger.info(f"Found {type_id} infobox")
                        blockquote['class'] = blockquote.get('class', []) + ['infobox', INFOBOX_TYPES[type_id]]
                        first_p = blockquote.find('p')
                        if first_p:
                            text = first_p.get_text()
                            new_text = re.sub(r'\[!\w+\]\s*\n?', '', text, 1)
                            first_p.string = new_text
                    # remove the single empty p we inserted at the beginning (check if empty)
                    if blockquote.find('p').string == '':
                        blockquote.find('p').decompose()

            content = str(soup)

            # Get metadata
            metadata = {}
            for name, value in md.Meta.items():
                name = name.lower()
                meta = self.process_metadata(name, value[0])
                metadata[name] = meta

        return content, metadata

def add_reader(readers):
    readers.reader_classes['md'] = MarkdownCustomInfoboxReader

def register():
    logger.info("Registering custom markdown reader")
    signals.readers_init.connect(add_reader)