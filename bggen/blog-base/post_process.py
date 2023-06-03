import markdown
import re
import subprocess
import glob
import click

def not_equal_any(strings_in, any_strings):
    out = True
    for s_i in strings_in:
        for a_s in any_strings:
            out = out and s_i != a_s
    return out

def gen_open_bootstrap(width):
    assert width > 3 and width <= 12
    line = '<div class="'
    for col in ['lg', 'md', 'sm', 'xs']:
        line += f'col-{col}-{width} '
    line += 'thumb blogcontent">'
    return line

# for every line containing the special Figure start block !Fig!N!, encapsulate the next lines 
# (containing an image and caption) inside a special bit of code that breaks the div its inside
# to make it bigger if requested
FIGURE_START = re.compile("<p>!Fig!.*!$")
""" Find all three-line figure blocks and pre-proc them into self-contained HTML """
def figure_postprocess(lines):
    figure_starts = []
    for i, line in enumerate(lines):
        if FIGURE_START.match(line) is not None:
            # we will pre-proc this line along with the next two
            figure_starts.append(i)
    for j, i in enumerate(figure_starts):
        print(f"Generating figure {j+1}")
        # check that the caption and image aren't blank
        assert not_equal_any(lines[i+1:i+3], ["", "\n"])
        width = int(lines[i].split("!")[2])
        assert width > 3 and width <= 12
        lines[i] = "<hr>\n</div>\n" + gen_open_bootstrap(width) + "\n"
        # image from line 2
        lines[i+1] = lines[i+1].strip().strip(">") + ' class="img-fluid">\n'
        caption = lines[i+2].strip().strip("</p>")
        print(f"Caption: {caption}")
        lines[i+2] = f"<br><br></div>" + gen_open_bootstrap(8)
        lines[i+2] += f"<p><b>Figure {j+1}</b>&mdash;<em>{caption}</em></p>\n<hr><br>\n"
    return lines

IGNORE_FILES = ["archives.html", "authors.html", "categories.html", "index.html", "tags.html"]


@click.command()
@click.option('--dir', default="/Users/mssaxon/Documents/github/michaelsaxon.github.io/blog")
def main(dir):
    files = glob.glob(f"{dir}/*.html")
    print("Backing up all blogpost files...")
    for file in files:
        if file in IGNORE_FILES:
            continue
        print(f"Processing file {file}")
        with open(file, "r") as f:
            lines = f.readlines()
        lines = figure_postprocess(lines)
        with open(file, "w") as f:
            f.writelines(lines)

if __name__ == '__main__':
    main()