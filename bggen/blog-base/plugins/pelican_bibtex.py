"""
Publications page from BiBTeX
==============

Adapted from Vlad Niculae's pelican_bibtex plugin.
"""

import logging
logger = logging.getLogger(__name__)

from pelican import signals

import re
from urllib.parse import urlparse

__version__ = '0.2.1'

ME = "Michael Saxon"

def determine_badge_info(pubdict):
    """
    Determines the text and CSS class for the official link badge.
    Returns a tuple: (badge_text, badge_class) or (None, None)
    """
    url = pubdict.get('url_official')
    if not url:
        return None, None

    if 'arxiv.org' in url:
        # Extract arXiv ID from URL
        # Handle both old and new style URLs:
        # https://arxiv.org/abs/2406.16851
        # https://arxiv.org/pdf/2406.16851.pdf
        arxiv_id = re.search(r'arxiv.org/(?:abs|pdf)/([0-9.]+)', url)
        if arxiv_id:
            return f'arXiv:{arxiv_id.group(1)}', 'arxiv-badge'
        return 'arXiv', 'arxiv-badge'  # Fallback if ID not found
    elif 'aclanthology.org' in url:
        return 'ACL Anthology', 'acl-badge'
    elif 'openreview.net' in url:
        # Try to determine conference from booktitle
        conf_label = 'OpenReview' # Default
        booktitle = pubdict.get('booktitle', '').lower() # Use .get with default and lowercase for case-insensitivity

        # Add more specific conference checks here (check full names first)
        # Order matters if a booktitle could contain multiple keywords
        # if 'international conference on learning representations' in booktitle or 'iclr' in booktitle:
        #      conf_label = 'ICLR'
        # elif 'conference on language modeling' in booktitle or 'colm' in booktitle:
        #      conf_label = 'COLM'
        # elif 'neural information processing systems' in booktitle or 'neurips' in booktitle:
        #      conf_label = 'NeurIPS'
        # elif 'international conference on machine learning' in booktitle or 'icml' in booktitle:
        #      conf_label = 'ICML'
        # ... add others like EMNLP, ACL, NAACL etc. using similar pattern ...
        # elif 'empirical methods in natural language processing' in booktitle or 'emnlp' in booktitle:
        #      conf_label = 'EMNLP'
        # elif 'association for computational linguistics' in booktitle or ' acl' in booktitle: # Add space before acl to avoid matching 'tacl' etc.
        #      conf_label = 'ACL'

        return conf_label, 'arxiv-badge' # Use specific conf label, generic conf class
    else:
        # Default official link
        return 'Official', 'link-badge'

    # Check for video link
    if 'video_link' in pubdict and pubdict['video_link']:
        video_url = pubdict['video_link']
        parsed_url = urlparse(video_url)
        platform = parsed_url.netloc.split('.')[1]  # Extract platform name
        badge_text = f"Presentation ({platform.capitalize()})"
        return badge_text, 'video-badge'

def determine_venue_badge(pubdict):
    """
    Determines the badge class for venue and additional info.
    Returns a tuple of (venue_badge_class, additional_info_badge_class)
    """
    venue_abbrev = pubdict.get('venue_abbrev', '').lower()
    additional_info = pubdict.get('additional_info', '').lower()
    
    # Determine venue badge class
    venue_badges = {
        'acl': 'acl-badge',
        'naacl': 'acl-badge',
        'eacl': 'acl-badge',
        'aacl': 'acl-badge',
        'iclr': 'iclr-badge',
        'colm': 'colm-badge',
        'neurips': 'neurips-badge',
        'emnlp': 'emnlp-badge'
    }
    
    # Handle arXiv preprints
    if 'arxiv.org' in pubdict.get('url_official', ''):
        venue_badge_class = 'arxiv-badge'
    else:
        # Check if any venue key is contained within venue_abbrev
        venue_badge_class = 'link-badge'  # default
        for venue_key, badge_class in venue_badges.items():
            if venue_key in venue_abbrev:
                venue_badge_class = badge_class
                break
    
    # Determine additional info badge class
    if 'oral' in additional_info:
        info_badge_class = 'oral-badge'
    elif 'spotlight' in additional_info:
        info_badge_class = 'spotlight-badge'
    else:
        info_badge_class = None
        
    return venue_badge_class, info_badge_class

def clean_bibtex(bibtex_str, entry_dict):
    """
    Clean the BibTeX string by:
    1. Removing empty fields
    2. Removing specified metadata fields
    3. Selecting best URL from available options
    """
    # Fields to exclude (our custom metadata fields)
    exclude_fields = [
        'url_official',
        'url_pdf',
        'url_arxiv',
        'yindex',
        'venue_abbrev',
        'additional_info',
        'demo',
        'routing',
        'video_link',
        'github',
        'huggingface'
    ]

    # Split into lines for processing
    lines = bibtex_str.split('\n')
    cleaned_lines = []
    url_added = False

    # URL preference order
    url_fields = ['url_official', 'url_pdf', 'url_abstract']
    selected_url = None
    for url_field in url_fields:
        if url_field in entry_dict and entry_dict[url_field]:
            selected_url = entry_dict[url_field]
            break

    # Process each line
    for line in lines:
        # Skip empty lines or lines with empty values
        if '= "",' in line or '= {},' in line:
            continue

        # Skip our metadata fields
        skip_line = False
        for field in exclude_fields:
            if f'{field} =' in line:
                skip_line = True
                break
        if skip_line:
            continue

        # Add the selected URL if we haven't yet and this is the last line before closing brace
        if selected_url and not url_added and '}' in line and line.strip() == '}':
            cleaned_lines.append(f'  url = {{{selected_url}}},')
            url_added = True

        # Keep this line
        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)

def add_publications(generator):
    """
    Populates context with a list of BibTeX publications.

    Configuration
    -------------
    generator.settings['PUBLICATIONS_SRC']:
        local path to the BibTeX file to read.

    Output
    ------
    generator.context['publications']:
        List of dictionaries, each representing a publication entry
        with added 'authors', 'bibtex', 'plaintext', 'badge_text',
        and 'badge_class' keys.
    """
    if 'PUBLICATIONS_SRC' not in generator.settings:
        logger.warn('PUBLICATIONS_SRC not set in config. Skipping bibtex processing.')
        return
    try:
        from io import StringIO # Use io.StringIO for Python 3+
    except ImportError:
        # Fallback for very old Python, unlikely needed
        from StringIO import StringIO
    try:
        from pybtex.database.input.bibtex import Parser
        from pybtex.database.output.bibtex import Writer
        from pybtex.database import BibliographyData, PybtexError
        from pybtex.backends import html
        from pybtex.style.formatting import plain
        from pybtex.plugin import find_plugin # For better style/backend finding
    except ImportError:
        logger.warn('`pelican_bibtex` failed to load dependency `pybtex`. Cannot process bib file.')
        return

    refs_file = generator.settings['PUBLICATIONS_SRC']
    try:
        parser = Parser()
        bibdata_all = parser.parse_file(refs_file)
    except PybtexError as e:
        logger.warn('`pelican_bibtex` failed to parse file %s: %s' % (
            refs_file,
            str(e)))
        return
    except FileNotFoundError:
        logger.warn(f'`pelican_bibtex` could not find the file specified by PUBLICATIONS_SRC: {refs_file}')
        return


    publications = []
    workshop_publications = []  # New list for workshop papers

    # Find pybtex plugins reliably
    try:
        plain_style = find_plugin('pybtex.style.formatting', 'plain')()
        html_backend = find_plugin('pybtex.backends', 'html')()
        bibtex_writer = find_plugin('pybtex.database.output', 'bibtex')()
    except Exception as e:
        logger.error(f"`pelican_bibtex` could not find required pybtex plugins: {e}")
        return

    # Format entries using the chosen style and backend
    try:
        formatted_entries = plain_style.format_entries(bibdata_all.entries.values())
    except Exception as e:
        logger.error(f"`pelican_bibtex` error formatting entries with pybtex: {e}")
        return

    for formatted_entry in formatted_entries:
        key = formatted_entry.key
        try:
            entry = bibdata_all.entries[key]
        except KeyError:
            logger.warn(f"Entry with key '{key}' found in formatted entries but not in original bibdata. Skipping.")
            continue

        # Populate basic entry_dict from BibTeX fields
        entry_dict = {'key': key}
        for field in entry.fields.keys():
            # Handle potential byte strings from pybtex if needed
            value = entry.fields.get(field)
            entry_dict[field.lower()] = value.decode('utf-8') if isinstance(value, bytes) else value

        # Render the author list (keeping your 'me' logic)
        authors = []
        try:
            for author in entry.persons['author']:
                # Combine first/middle/last names properly
                author_first = " ".join(author.first_names + author.middle_names)
                author_last = " ".join(author.last_names)
                this_author = f"{author_first} {author_last}".strip()

                if ME in this_author:
                    this_author = f'<span class="me">{this_author}</span>' # Use span for semantics
                    if "*" in this_author: # Check for '*'
                        # For equal contribution, put me first
                        authors.insert(0, this_author)
                    else:
                        authors.append(this_author)
                else:
                    authors.append(this_author)
            entry_dict['authors'] = ", ".join(authors) # Use 'authors' key
            is_first_author = ME in authors[0]
        except KeyError:
            entry_dict['authors'] = entry_dict.get('author', '') # Fallback to raw author field
            is_first_author = False

        # Render the bibtex string for the entry
        try:
            bib_buf = StringIO()
            bibdata_this = BibliographyData(entries={key: entry})
            bibtex_writer.write_stream(bibdata_this, bib_buf)
            raw_bibtex = bib_buf.getvalue().strip()
            # Clean the bibtex before storing
            entry_dict['bibtex'] = clean_bibtex(raw_bibtex, entry_dict)
        except Exception as e:
            logger.warn(f"Failed to generate BibTeX string for entry {key}: {e}")
            entry_dict['bibtex'] = None

        # Add plaintext version from formatted entry
        try:
            text = formatted_entry.text.render(html_backend)
            entry_dict['plaintext'] = text
        except Exception as e:
            logger.warn(f"Failed to render HTML for entry {key}: {e}")
            entry_dict['plaintext'] = None

        # Add badge classes to the entry dict
        venue_badge_class, info_badge_class = determine_venue_badge(entry_dict)
        entry_dict['venue_badge_class'] = venue_badge_class
        entry_dict['info_badge_class'] = info_badge_class

        # Keep any existing badge processing for PDF/arXiv links
        badge_text, badge_class = determine_badge_info(entry_dict)
        if badge_text:
            entry_dict['badge_text'] = badge_text
            entry_dict['badge_class'] = badge_class

        # Check if this is a workshop paper
        is_workshop = entry.fields.get('routing', '').lower() == 'workshop'

        # Add show/hide logic
        entry_dict['is_first_author'] = is_first_author
        venue_category = 'other'
        if any(key in venue_badge_class for key in ['acl', 'naacl', 'eacl', 'aacl', 'emnlp']):
            venue_category = 'acl'
        elif any(key in venue_badge_class for key in ['colm', 'iclr', 'neurips']):
            venue_category = 'topml'
        elif any(key in entry_dict.get('venue_abbrev', '').lower() for key in ['icassp', 'interspeech', 'taslp']):
            venue_category = 'speech'
        elif 'arxiv' in entry_dict.get('url_official', '') or 'arxiv' in venue_badge_class or 'preprint' in venue_badge_class:
            venue_category = 'preprint'
        entry_dict['venue_category'] = venue_category
        
        # Add to appropriate list
        if is_workshop:
            workshop_publications.append(entry_dict)
        else:
            publications.append(entry_dict)

    # Sort both lists
    try:
        for pub_list in [publications, workshop_publications]:
            pub_list.sort(key=lambda x: (
                -int(x.get('year', '0')), 
                -int(x.get('yindex', '999')),
                x.get('author', '')
            ))
    except ValueError:
        logger.warn("Could not sort publications due to non-integer year or yindex.")

    # Add both lists to the context
    generator.context['publications'] = publications
    generator.context['workshop_publications'] = workshop_publications

def register():
    signals.generator_init.connect(add_publications)
