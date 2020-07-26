import markdown2

DEFAULT_NAVBAR = [("About","index.html"),
				("Projects","projects.html"),
				("Research","research.html"),
				("CV","doc/cv_saxon.pdf")]

PAGEBASE = open("base.html", "r").read()

def gen_navbar(current = None, elems = DEFAULT_NAVBAR):
	out_string = '<ul class="menu">\n'
	for name, url in elems:
		out_string += '<li><a '
		if current == url:
			out_string += 'class = "active">'
		else:
			out_string += ' href = "' + url +'">'
		out_string += name + '</a></li>\n'
	out_string += '</ul>\n'

def test_and_sub(sub_tag, pagebase, sub_content):
	if f":::{sub_tag}:::" in pagebase:
		split_base = pagebase.split(f":::{sub_tag}:::\n")
		out_string = split_base[0] + sub_content + split_base[1]
	else:
		out_string = pagebase

if 


def gen_page(url, pagebase = PAGEBASE):
	out_string = test_and_sub("NAVBAR", pagebase, gen_navbar(current = url))
	out_string = test_and_sub("CONTENT", out_string, content)
