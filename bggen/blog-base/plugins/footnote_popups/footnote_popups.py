from pelican import signals
from bs4 import BeautifulSoup
import re
import logging
import os

logger = logging.getLogger(__name__)

def process_footnotes(content):
    if not hasattr(content, '_content') or not content.source_path.endswith('.md'):
        logger.info(f"Skipping non-markdown content: {getattr(content, 'source_path', 'unknown')}")
        return

    logger.info(f"Processing content: {getattr(content, 'source_path', 'unknown')}")
    
    # Add debug logging for metadata
    logger.info(f"Content metadata: {content.metadata}")
    remove_section = content.metadata.get('remove_footnote_section', False)
    logger.info(f"Remove footnote section: {remove_section}")
    
    soup = BeautifulSoup(content._content, 'html.parser')
    
    # Find all footnote references
    footnote_refs = soup.find_all('sup', id=re.compile(r'^fnref:'))
    logger.info(f"Found {len(footnote_refs)} footnote references")
    
    if not footnote_refs:
        logger.info("No footnotes found, skipping processing")
        return  # No footnotes, no processing needed
    
    # Define the SVG plus icon template
    plus_svg = '''
        <svg class="footnote-icon" viewBox="0 0 24 24">
            <g class="icon-group" stroke="currentColor" stroke-width="3" stroke-linecap="round">
                <line x1="7" y1="12" x2="17" y2="12"/>
                <line x1="12" y1="7" x2="12" y2="17"/>
            </g>
        </svg>
    '''

    for i, ref in enumerate(footnote_refs):
        # Get corresponding footnote content
        fn_id = ref['id'].replace('fnref:', 'fn:')
        footnote = soup.find('li', id=fn_id)
        
        if footnote:
            logger.info(f"Processing footnote {i+1}: {fn_id}")
            # Extract footnote text (excluding the backref)
            try:
                footnote_text = ''.join(str(c) for c in footnote.p.contents[:-1]).strip()
                popup = soup.new_tag('span', attrs={'class': 'footnote-popup'})
                popup.string = footnote_text
                
                # If removing footnote section, modify the link behavior and text
                if remove_section:
                    ref.a['class'] = ref.a.get('class', []) + ['footnote-toggle']
                    ref.a['href'] = 'javascript:void(0)'
                    # Replace number with SVG plus icon
                    ref.a.string = ''
                    svg_soup = BeautifulSoup(plus_svg, 'html.parser')
                    ref.a.append(svg_soup.svg)
                
                ref.append(popup)
                logger.info(f"Added popup for footnote {fn_id}")
            except Exception as e:
                logger.error(f"Error processing footnote {fn_id}: {str(e)}")
    
    # Remove the footnote section if requested
    if remove_section:
        footnote_section = soup.find('div', class_='footnote')
        if footnote_section:
            footnote_section.decompose()
            logger.info("Removed footnote section")
    
    content.has_footnotes = True
    content._content = str(soup)
    logger.info("Finished processing footnotes")

def add_script_to_output(path, context):
    """Add script tag to the final HTML output files"""
    if not context.get('article') or not getattr(context['article'], 'has_footnotes', False):
        return
    
    logger.info(f"Adding script to output file: {path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        body = soup.find('body')
        
        if body:
            # Create script tag
            script_tag = soup.new_tag('script')
            script_tag['src'] = '../../../static/js/popups.js'
            
            # Add it before the closing body tag
            body.append(script_tag)
            logger.info("Added script tag to body")
            
            # Write the modified content back
            with open(path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
        else:
            logger.warning(f"Could not find body tag in {path}")
    except Exception as e:
        logger.error(f"Error adding script to {path}: {str(e)}")

def register():
    logger.info("Registering footnote_popups plugin")
    signals.content_object_init.connect(process_footnotes)
    signals.content_written.connect(add_script_to_output) 