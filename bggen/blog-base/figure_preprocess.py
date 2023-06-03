import markdown
import re
import subprocess
import glob

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
FIGURE_START = re.compile("!Fig!.*!$")
""" Find all three-line figure blocks and pre-proc them into self-contained HTML """
def figure_preprocess(lines):
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
        lines[i] = "<hr></div>" + gen_open_bootstrap(width) + "\n"
        # image from line 2
        img_alt = lines[i+1].split("[")[-1].split("]")[0]
        img_src = lines[i+1].split("(")[-1].split(")")[0]
        lines[i+1] = f'<img alt="{img_alt}" src="{img_src}" class="img-fluid">\n'
        print(f"Img src: {img_src} with alt: {img_alt}")
        print(f"Caption: {lines[i+2]}")
        lines[i+2] = f"</div><p><b>Figure {j+1}</b>&mdash;<em>{lines[i+2].strip()}</em></p>"
        lines[i+2] += gen_open_bootstrap(8) + "<hr><br>\n"
    return lines, figure_starts

def main():
    files = glob.glob("content/*.md")
    print("Backing up all blogpost files...")
    for file in files:
        print(f"Processing file {file}")
        with open(file, "r") as f:
            lines = f.readlines()
        lines, figure_starts = figure_preprocess(lines)
        # markdown to HTML because pelican actually sucks
        if len(figure_starts) == 0:
            print("Skipping, no figures...")
            continue
        for i, line in enumerate(lines):
            if line == "" or line == "\n":
                firstblank = i
                print(firstblank)
                break
        print(figure_starts)
        outlines = lines[0:firstblank]
        outlines.append(markdown.markdown("".join(lines[firstblank:figure_starts[0]]), extensions=['markdown_katex']))
        figure_starts.append(len(lines))
        for i in range(len(figure_starts)-1):
            outlines+=lines[figure_starts[i]:figure_starts[i] + 3]
            contig = "".join(lines[figure_starts[i] + 3:figure_starts[i+1]])
            contig = markdown.markdown(contig, extensions=['markdown_katex'])
            outlines.append(contig)
        with open(file, "w") as f:
            f.writelines(outlines)

if __name__ == '__main__':
    main()