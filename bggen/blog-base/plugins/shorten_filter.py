from pelican import signals

def shorten_text(text, length=15):
    text = text.split(" ")
    if len(text) > length:
        text = text[:length]
        return " ".join(text) + "..."
    return " ".join(text)

def register():
    signals.generator_init.connect(add_shorten_filter)

def add_shorten_filter(generator):
    generator.env.filters['shorten'] = shorten_text 