Title: Michael's TeXronomicon (LaTeX tips, tricks, and hacks)
Date: 2025-04-10 19:00
Category: Tips
Tags: latex
Authors: Michael Saxon
Summary: Various snippets, tricks, and lessons I've developed and learned from messing around in LaTeX and scrutinizing source files on arXiv.
Image: images/latex-tips.jpg
remove_footnote_section: true

Between my mild presentational OCD and a desire to understand how various cool figures, tables, and styles have been implemented in other groups' papers, I have accumulated quite a few LaTeX snippets that I pass around with my friends. I figured I should put them all in one place along with some explanations, so (if you're interested) you can learn to make your own.

You should probably check out the TOC to decide which parts you want to read.
There will probably be parts you already know; I am covering basics here so I can give this to a new author.
To briefly explain the structure, I will discuss:

1. How commands work, how to make them, and **the right way to do comment commands**.
2. *Text* styling, including coloring, highlighting, citation styles, exotic symbols, non-Latin alphabets, and inline graphics/icons.
3. *Table* styling and formatting, which packages you should use, special symbols to make tables more readable, and making text compact.
<!-- 4. *Figure* making and styling, including composite figures, table-based figures, the various subfigure packages, and how to *generate* good, readable figures from matplotlib easily.
5. How to set up *Overleaf with VSCode*, a gamechanger I was recently shown. -->
4. **The dark arts**, how you can break free from the bounds of conference `.sty` files.

I might write more about within-document compound figure making and best-practices for generating readable plots in a follow-up post if there's interest.

[TOC]

# 1. Making commands 

**You should probably be making more commands than you currently are**. At their simplest, commands can let you reuse text or formatting easily, but they can do much more. First, a little bit about how to make them:

The two main command-making macros are `\newcommand` and `\renewcommand`. 
If a command already exists, and you want to override its behavior, use `\renewcommand`. For example, I used `\renewcommand` to fix a critical flaw in the COLM format.

In the COLM format, this snippet:

```latex
Inertia is a property of matter \cite{nye1995science}.
```

would wrongly render as:

> Inertia is a property of matter Nye et al. (1995).

Instead of correctly rendering as:

> Inertia is a property of matter (Nye et al., 1995).


In other words, the COLM format was treating `\cite{}` as `\citet{}` rather than `\citep{}`, as it is in all other conference formats.

With `\renewcommand` it's a one line fix:

```latex
\renewcommand{\cite}{\citep}
```

## Comment commands

The command definition you have almost certainly used before is **comment commands**.
But have you made them hideable? Modular? Here's how I built up a more powerful comment command that I always drop in. 

A typical, simple comment command is something like:

```latex
\newcommand{\mycomment}[1]{\textcolor{red}{michael: #1}}
```

This is nice and easy, but it has two issues. First, with more collaborators you have to define it over and over again, which looks gross.

```latex
\newcommand{\mycomment}[1]{\textcolor{red}{MS: #1}}
\newcommand{\george}[1]{\textcolor{yellow}{GC: #1}}
\newcommand{\jerry}[1]{\textcolor{red}{JS: #1}}
\newcommand{\kramer}[1]{\textcolor{green}{CK: #1}}
\newcommand{\elaine}[1]{\textcolor{blue}{EB: #1}}
```

Ew. 

But the more annoying issue is that *inline comments mess up your text length and spacing*. How are you gonna know how many pages you've written, and how well-aligned and spaced your figures and tables are, on the night before the deadline, if your paper is full of comments?

I fix both of these issues by implementing *a base comment command* that I build the other ones on top of, and **adding a variable-based off switch that hides the comments.**
 
```latex
%%%%%%% COMMENT DEFINITION SECTION %%%%%%%
\newif\ifcommentsoff
% uncomment this line to hide inline comments
% \commentsofftrue
\newcommand{\mycomment}[3]{
    \ifcommentsoff\else{
        {\textcolor{#1}{\textit{\textbf{#2:} #3}}\xspace
    }\fi}
}
\newcommand{\george}[1]{\mycomment{red}{GC}{#1}}
\newcommand{\jerry}[1]{\mycomment{magenta}{JS}{#1}}
\newcommand{\kramer}[1]{\mycomment{blue}{CK}{#1}}
\newcommand{\elaine}[1]{\mycomment{green}{EB}{#1}}
```

`\newif\ifmyvariable` defines a boolean variable, which is actually named `myvariable`.
You can control it with `\myvariabletrue` or `\myvariablefalse`. This is weird and Knuth-y.


Now, all I have to do to periodically check how the spacing and length of the paper is with a bunch of inline comments present is to make `\commentsofftrue`.

## Fixing infuriating spacing issues

Often you want to define a command as a simple macro for some name you're using throughout the paper, say, for a contrived backronym method name. Something like:

```latex
\newcommand{\methodname}{\textsc{BiG-BiRd}}
```

This has the benefit of letting you change it if you aren't sure what your final method is.
Also if you want to do obnoxious extra formatting like a weird font or color[^1], it's easier to reuse this way.

[^1]: As I often do...

Unfortunately, text in LaTeX commands have infuriating spacing behavior. If you put the command as is, it will *ignore* following spaces,  so "`\methodname is great`" renders as "BiG-BiRdis great".

The `\xspace` package makes spacing work right:

```latex
% in preamble
\usepackage{xspace}

\newcommand{\methodname}{\textsc{BiG-BiRd}\xspace}
```


# 2. Doing text right

With our new understanding of commands, we can turn to discussing best practices for working with existing commands and creating new commands to make your text look beautiful.

Additionally, we will talk about how navigate the various quirky "Knuth-isms"[^3] that pervade LaTeX to make your text look right.

[^3]: My term for the peculiar ways some commands in TeX are written, which I believe come from the particularly detail-obsessed mind of its creator Don Knuth (pictured in the thumbnail)

## Citations

Two different styles of inline citation are invoked with `\citet`, and `\citep`.
In parenthetical citation styles (such as \*ACL or COLM) these mean *text-inline* (`\citet` for *t*ext) and *inside the parentheses* (`\citep`).

>  Saxon et al. (2024) vs (Saxon et al. 2024)

One is used just as a source for a claim, the other is to write a sentence that the authors say X or authors do X.

Usually, `\cite` and `\citep` do the same thing. If they don't, I usually newcommand or renewcommand `\cite` to get this behavior.

## `ref`, `autoref`, and `cleveref`

When you want to reference a figure or table by number you can use `\ref{fig:figurename}` to generate the figure number in a link like:

```latex
In figure \ref{fig:figurename} we learn X.
```

generates

> In figure [1]() we learn X.

But what if you want the "figure" text to be part of the link? And what if you're sick of typing "figure" or "table" each time? There are two solutions, `autoref` and `cleveref`.

`\autoref` is the simpler command.

```latex
\usepackage{autoref}

In \autoref{fig:figurename} we learn X. \autoref{fig:otherfigure} shows Y.
```

> In [figure 1]() we learn X. [Figure 2]() shows Y

Autoref works for figures, tables, sections, subsections, subsubsections, etc.

> In subsubsection 2.3.1... Section 3 shows... See table 2...

Note that the first "figure" isn't capitalized, while the second is. "subsubsection" isn't capitalized but "Section" is. `autoref` automates all of this based on position in a sentence.

What if you want a more compact style of these automatic citations? What if you want to change this behavior? That's where `cleveref` can come in handy.

```latex
\usepackage{cleveref}
\crefformat{section}{\S#2#1#3}
\crefformat{subsection}{\S#2#1#3}
\crefformat{subsubsection}{\S#2#1#3}

The turbo encabulator (\cref{subsec:encabulator}) also leverages inverse reactive current in unilateral phase detractors
```
> The turbo encabulator (§2.3.1) also leverages inverse reactive current in unilateral phase detractors
 
Within those definitions you can define whatever behavior you want. You can make it say "Section 2.3.1" instead of "subsubsection 2.3.1", enforce capitalization in all places, etc.

## Quotation marks

One of the most infuriating Knuthisms in LaTeX is the way quotation marks are handled. 

The characters `'` and `"`, in most fonts, **specifically refer to backwards marks**. So

```latex
In the turbo encabulator power is generated by "capacitive diractance" and 'magneto reluctance.'
```

> In the turbo encabulator power is generated by ”capacitive diractance” and ’magneto reluctance.’

Note the opening quotation marks are backwards. (This looks worse in the serif fonts most LaTeX documents use than it looks here.)
To fix this, **you need to use the tick mark `, not the apostrophe ', to open quotes.**

```latex
In the turbo encabulator power is generated by ``capacitive diractance'' and `magneto reluctance.'
```

> In the turbo encabulator power is generated by “capacitive diractance” and ‘magneto reluctance.’



## Resizing and transforming text

There are various useful reasons you may want to resize text.
Maybe to shrink an equation so it fits on a line, or to do some customization inside a figure or to shrink text in a table cell.

Text sizing is a site of many hilarious Knuthisms.
First, to size a line of text, you use these (in ascending order of size)

- `\tiny`
- `\scriptsize`
- `\footnotesize`
- `\small`
- `\normalsize`
- `\large`
- `\Large`
- `\LARGE`
- `\huge`
- `\Huge`

If you're just mad, you should say `{\large I am mad}` but if you're REALLY angry you can give a `{\LARGE I AM FURIOUS}`.

See more in [Overleaf's docs](https://www.overleaf.com/learn/latex/Font_sizes%2C_families%2C_and_styles)


## Defining colors and coloring text

By default, LaTeX has colors like "red", "green", "blue", and "magenta" (as I used above in my comment commands).

However, the `xcolor` package is pretty much a must-use even with those colors defined.
I'm pretty sure it is what gives the `\color{green}` macro its power, even if the color green already exists.

To color a bit of text, you wrap all the text you want *inside brackets, with the color macro*.

```latex
This text is black and {\color{green} this text is green}.
```

Additionally, it gives access to more elaborate colors depending on how you import. For example, `\usepackage[dvipsnames]{xcolor}` gives you access to more colors like "aquamarine," "skyblue", "navyblue", etc.

![The how boys see colors vs how girls see colors meme except for base latex vs dvips colors]({attach}images/xcolor-meme.jpg)

Additionally, we can use xcolor to define our own colors.
The precise way is with an RGB code.
For example, `\definecolor{tifablue}{RGB}{226, 232, 248}` defines the exact color we used in Table 2 of our [TS2 paper](https://arxiv.org/pdf/2404.04251) to define the highlight color of TIFA-related runs. Once defined, one of these colors can be invoked with `\color{tifablue}`.

If you just need a one-off hacky new color though, getting RGB may be too much.
Here you can use this fractional combination-based technique I don't fully understand. 
`\color{blue!50!black}` is the mix of 50% pure blue (`#0000FF`) and 100% pure black (`#000000`). The practical use of this color notation is that it can be directly used inline, inside the `color` command, rather than requiring a color definition.

Other color models you can use include cmyk, HTML, and wavelength of the color in nanometers. 
More explanation of colors with the predefined names are given [here](https://latex-tutorial.com/color-latex/).

### Custom-colored highlighting

The `soul` package provides useful macros for custom highlighting and background coloring for text.

```latex
\usepackage{soul}

\sethlcolor{green}
This is \hl{cool} stuff!
```

> This is <span style="background-color: #0F0;">cool</span> stuff!

The purpose of this `soul`-based solution for coloring text rather than `colorbox` is that soul properly breaks lines, while colorbox doesn't.

## Size units for spacing: em, ex, pt, etc

When we want to define the size or spacing of an object, we have a few choices of unit which have different uses in different settings.

You probably already know `pt`, or typographical point. I usually use this to size inline components (see **Inline icons** below). Depending on the document, 10, 11, or 12 pt will usually give you an element equal in size to the height of a tall letter in the main text.

`em` and `ex` come from CSS, and are **useful size units defined relative to the font size.**
`1em` is equivalent to the current font size. `1ex` is equivalent to the height of the letter "x" in the current font size, roughly 50% of `1em`.

These units are very useful for quickly iterating on heights and widths that are large relative to the whole document (for example, setting negative vspace in the **Dark arts** section)

Finally, if you wish, you can use `cm`, `mm`, and `in` for sizing. Self-explanatory, they are relative to the current document. I prefer not to use them.

## Annoying extra formatting (which I sometimes use)

If you really want to go the extra mile to make your paper pop, you can do things like making your method name colorful every time it shows up, or use exotic symbols for author affiliation marks rather than numbers, playing card suits, or crosses.

Also, you can decorate quotations with big colored boxes!

### Big colored text boxes

In our COLM paper from last year, we wanted to insert cute little vignettes from the real sciences relating to our position on AI science.

To do this I wrote a `\vig` command to make a nice colored box, something like the warning boxes I implemented for this website!

> [!NOTE]
> ***Example colorbox!***
> 
> Text of the box!

We did this using the `tcolorbox` package.

```latex
\usepackage[skins,breakable]{tcolorbox}

\newtcolorbox{boxblue}{enhanced,colback=blue!5!white,colframe=blue!75!black,breakable=true}

\newcommand{\vig}[2]{
\begin{boxblue}
\textit{\color{blue!50!black}\textbf{#1}}

\vspace{6pt}#2
\end{boxblue}
}

\vig{Example colorbox!}{Text of the box!}
```

Here you can see I used the fractional color models discussed above. The options `skins` enables a subpackage which provides a LOT of different options for themeing colorboxes beyond the simple one we used (full documentation [here](https://texdoc.org/serve/tcolorbox.pdf/)). This allowed us to set the frame color and background color.
The `breakable` option allows us to let the colorbox break across pages rather than being forced to the top of a following page and adding a bunch of whitespace like a forced inline figure would.

### Fancy colored gradients inline

If a single xcolor isn't enough to make your methodname look good (it wasn't enough in [TS2](https://arxiv.org/pdf/2404.04251)) you can use the `gradient-text` package to achieve this.

```latex
\usepackage[dvipsnames]{xcolor}
\usepackage{gradient-text}

\newcommand{\resourcename}{\texttt{\textbf{\gradientRGB{T2IScoreScore}{68,67,147}{61,130,217}}}}
```

`\gradientRGB` colors all *n* letters in the first argument text with *n* intermediate colors it calculates which interpolate between the colors in arguments 2 and 3.

### Inline icons

Say you want to put a cute image or icon in the title of your paper, like the [Stochastic Parrots](https://upload.wikimedia.org/wikipedia/commons/f/f2/On_the_Dangers_of_Stochastic_Parrots_Can_Language_Models_Be_Too_Big.pdf) paper did.

You can just[^4] put `\includegraphics` macros inline with text.

[^4]: do things

For example, I put a logo for an upcoming preprint in our title like this:

```latex
\vspace{-3pt}\raisebox{-3pt}{\includegraphics[width=20pt]{pics/logo.png}}
```

Basically, here's what's going on here. The icon image itself is very big, much bigger than a line of text. If you just put `\includegraphics` inline without anything around it, the image will scale to its natural size.

To counteract this, I have to both manipulate its sizing and positioning.
Through manual experimentation I found that setting the width to 20pt roughly sized it according to my desires. However, the spacing was off. The image was too far above the line and making the line itself taller. To fix this, I had to use negative `\vspace{}` to keep the line positioning in subsequent lines from being impacted by the symbol, and negative `\raisebox{}` to slightly push the bottom of the image under the line.

### Exotic symbols (eg., as author affiliation marks)

I used to really dislike the trend of quirky affiliation marks in author lists, and was basically doing them ironically[^5] until I came to love them. Here are some ways I got them.

[^5]: I know, I'm obnoxious

In my [NAACL paper](https://arxiv.org/abs/2403.11092) last year I used Egyptian hieroglyphs as affiliation marks.

```latex

\usepackage{hieroglf}

I love Egypt! \textpmhg{eFR\Hibl}
```

> I love Egypt! 𓁹𓆛𓅃𓅠

In our TS2 paper, I wanted to have PlayStation button symbols as author affiliation marks. I drew these using custom tikz:

```latex
\usepackage{xcolor}
\usepackage{tikz}

\newcommand{\pssymb}[2]{
\resizebox{#1}{!}{\begin{tikzpicture}#2\end{tikzpicture}}
}

\newcommand{\pscirc}{
\pssymb{6pt}{
    \draw (0,0) circle [radius=1.5];
    \draw[line width=5pt, red] (0,0) circle [radius=0.8];
}}

\newcommand{\psx}{
\pssymb{6pt}{
    \draw (0,0) circle [radius=1.5];
    \draw[line width=5pt, blue] (-0.8,-0.8) -- (0.8,0.8);
    \draw[line width=5pt, blue] (0.8,-0.8) -- (-0.8,0.8);
}}

...

\author{Michael Saxon$^{\psx\pscirc}$...}
```
> Michael Saxon<sup><img style="width:12pt;border:0;" src="https://t2iscorescore.github.io/static/images/psx.svg"/><img style="width:12pt;border:0;" src="https://t2iscorescore.github.io/static/images/psc.svg"/></sup>

Providing a tikz tutorial is out of scope here. Look it up yourself ;)

## Non-Latin (CJK) alphabets on arXiv

XeLaTeX is the best way to do this, with native unicode support, and a much more comprehensive distribution of multilingual fonts and modules. 
But arXiv (as of writing) doesn't support it 😭😭😭😭😭

So we need to figure out how to do it with pdfLaTeX.

We have to hack it in using various packages depending on language. In my multilingual paper, I *wanted* to include CJK and Hebrew characters, but I just could not figure out Hebrew without XeLaTeX at least for CJK you can use the CJK packages.

I was able to get this working on arXiv:

```latex
%%% preamble
\usepackage[utf8]{inputenc}
\usepackage{CJKutf8}

%%% set the font for each language
% mincho font for Japanese
\newcommand{\inlinejp}[1]{\begin{CJK}{UTF8}{min}{#1}\end{CJK}}
% gbsn font for Chinese
\newcommand{\inlinezh}[1]{\begin{CJK}{UTF8}{gbsn}{#1}\end{CJK}}

%%% in document
\inlinejp{お前はもう死んでいる}
\inlinezh{迈克不喜欢卷}
```

# 3. Turning the Tables

Default LaTeX tables aren't very appealing. Use `booktabs.`

## Basic table hygiene with `booktabs`

Within the `tabular` environment, `booktabs` gives you macros like `\toprule`, `\bottomrule`, and `\midrule`, which give you lines of different thickness, width, and spacing which look nicer than the default table lines.

When you define the columns of your table in the `tabular` environment, (`|`) puts a pipe between lines. The cells can be defined with left, center, or right alignment with `l`, `c`, and `r`. For example:

```latex
\usepackage{booktabs}

\begin{table}\centering
\begin{tabular}{l|cr}
\toprule
Thing 1 & Thing 2 & Thing 3 \\
\midrule
A & B & C \\
\bottomrule
\end{tabular}
\end{table}
```

> <table style="border-top: 2px solid black; border-bottom: 2px solid black; padding: 1px;"><tr><td style="border-bottom: 1px solid black; margin:0; width: 100pt; border-right: 1px solid black;">Thing 1</td><td style="border-bottom: 1px solid black; margin:0; padding-right 5pt; width: 100pt; text-align:center;">Thing 2</td><td style="border-bottom: 1px solid black; margin:0; width: 100pt;text-align:right;">Thing 3</td></tr><tr style="border:0;"><td style="border-right: 1px solid black;">A</td><td style="text-align:center;">B</td><td style="text-align:right;">C</td></tr></table>

Please use `|` tastefully. Resist the impulse to do `\tabular{|c|c|c|}`, because this is harder to scan over and read:

> [!WARNING]
> <table style="border-top: 2px solid black; border-bottom: 2px solid black; padding: 1px;"><tr><td style="border-bottom: 1px solid black; margin:0; width: 100pt; border-right: 1px solid black; text-align:center;border-left: 1px solid black; ">Thing 1</td><td style="border-bottom: 1px solid black; margin:0; padding-right 5pt; width: 100pt; text-align:center; border-right: 1px solid black; ">Thing 2</td><td style="border-bottom: 1px solid black; margin:0; width: 100pt;text-align:center;border-right: 1px solid black; ">Thing 3</td></tr><tr style="border:0;"><td style="border-right: 1px solid black; border-left: 1px solid black; text-align:center;">A</td><td style="border-right: 1px solid black; text-align:center;">B</td><td style="border-right: 1px solid black; text-align:center;">C</td></tr></table>


## `multirow` and `multicolumn`

You can define multi-row and multi-column cells using these environments.

```latex
\multirow{NUM_ROWS}{ALIGNMENT}{Text}
\multicolumn{NUM_COLUMNS}{ALIGNMENT}{Text}
```

`NUM_ROWS` and `NUM_COLUMNS` should be self-explanatory. For `ALIGNMENT` you can use `l`, `r`, `c` as in tabular for multicolumn. For multirow, you should usually use `*` for vertical centering.

## `cmidrule` to partially underline a row

Sometimes you want to only underline some of the cells in a row (for example, you want to underline a multicolumn cell in the row above.) `cmidrule` does this with arguments for edges to thin and cell numbers.
For example, 

```latex
\usepackage{booktabs}

\begin{table}\centering
\begin{tabular}{l|cr}
\toprule
Thing 1 & Thing 2 & Thing 3 \\
\cmidrule{2-3}
A & B & C \\
\bottomrule
\end{tabular}
\end{table}
```

> <table style="border-top: 2px solid black; border-bottom: 2px solid black; padding: 1px;"><tr><td style="margin:0; width: 100pt; border-right: 1px solid black;">Thing 1</td><td style="border-bottom: 1px solid black; margin:0; padding-right 5pt; width: 100pt; text-align:center;">Thing 2</td><td style="border-bottom: 1px solid black; margin:0; width: 100pt;text-align:right;">Thing 3</td></tr><tr style="border:0;"><td style="border-right: 1px solid black;">A</td><td style="text-align:center;">B</td><td style="text-align:right;">C</td></tr></table>

Usually, if you have multiple `cmidrule` side-by-side, you want to "chop off" parts on the left and right sides so they don't connect, providing some visually pleasing separation. To do this, you can include `(lr)` like:

```latex
\cmidrule(lr){2-3}\cmidrule(lr){4-5}
```

To provide multiple partial midrules that are adjacent but not connected.

## Fancy stuff

Now for some more advanced beautification techniques for your tables.

### Coloring table cells

The `colortbl` package provides a simple interface to coloring cells, using colors we defined above. `\cellcolor{COLOR}` will color the background of the cell it's in.


### Special table symbols

For my CoCo-CroLa paper I wanted an efficient way to mark equivalence between cells in a column, rather than repeat the same value several times.
I wanted something very easy to skim with minimum visual noise, and came up with:

![Vertical line through duplicate cells]({attach}images/cccltable.png)

I called this "same line" command `\samel`, defined with:

```latex
\newcommand{\samel}[0]{\multicolumn{1}{l}{\space\hspace{0.5em}\vline}}
```

Inside of a environment of a single multicolumn we can use a `\vline` (equivalent to putting `|` in the tabular environment definition), which would normally be to the far left side of the cell. We then push it rightward by `0.5em`, or half the vertical height of the text.

### Rotating the text inside a cell

Often, plots can make axis labels more compact by rotating their text.
I wanted to replicate this in a table I made last year and was able to pretty easily using the `rotating` package.

```latex
\usepackage{rotating}

\newcommand{\myrotcell}[1]{\begin{turn}{75}#1\end{turn}}
```

`\myrotcel` basically behaves exactly as I wanted inside of a table, turning the rotated text into an element with the proper width and height for positioning elements around it without overlapping or other weird clipping behavior.

## Putting it together

Using all of the above components we've discussed, including the `booktabs` line rules and `cmidrule`, the text cell rotation command `\myrotcel` we made, cell coloring and rotated `multicolumn`, we can generate this table from the TS2 paper:

![Table from the TS2 paper using all of these tricks.]({attach}images/ts2table.png)

```latex
\newcommand{\ty}[0]{\cellcolor{otheryellow}}
\newcommand{\tr}[0]{\cellcolor{dsgred}}
\newcommand{\tb}[0]{\cellcolor{tifablue}}
\newcommand{\tg}[0]{\cellcolor{llmgreen}}


\begin{table*}[t!]
\centering
\begin{tabular}{llb{15pt}b{15pt}b{15pt}b{15pt}b{15pt}b{15pt}b{15pt}b{15pt}b{15pt}b{15pt}b{15pt}b{15pt}b{15pt}b{15pt}b{15pt}b{15pt}b{15pt}b{15pt}b{15pt}}
\toprule
& & \myrotcell{\textbf{CLIPScore}} & \myrotcell{\textbf{ALIGNScore}} & \myrotcell{\textbf{mPLUG}} & \myrotcell{\textbf{LLaVA 1.5}} & \myrotcell{\textbf{LLaVA 1.5 (alt)}} & \myrotcell{\textbf{InstructBLIP}} & \myrotcell{\textbf{BLIP1}} & \myrotcell{\textbf{Fuyu}} & \myrotcell{\textbf{GPT4-V}} & \myrotcell{\textbf{mPLUG}} & \myrotcell{\textbf{LLaVA 1.5}} & \myrotcell{\textbf{LLaVA 1.5 (alt)}} & \myrotcell{\textbf{InstructBLIP}} & \myrotcell{\textbf{BLIP1}} & \myrotcell{\textbf{Fuyu}} & \myrotcell{\textbf{GPT4-V}} & \myrotcell{\textbf{LLMScore EC}} & \myrotcell{\textbf{LLMScore Over}} & \myrotcell{\textbf{VIEScore}} \\
\cmidrule(l{5pt}r{5pt}){3-4} \cmidrule(l{5pt}r{5pt}){5-11} \cmidrule(l{5pt}r{5pt}){12-18} \cmidrule(l{5pt}r{5pt}){19-21} 
& & \multicolumn{2}{c}{ \footnotesize \textbf{Emb-based}}& \multicolumn{7}{c}{ \textbf{TIFA}} & \multicolumn{7}{c}{\textbf{DSG}} &  \multicolumn{3}{c}{\footnotesize \textbf{Caption-based}}  \\
\midrule
\multirow{4}{*}{\rotninety{$\mathtt{rank}_m$}} & \textbf{Avg} &  71.4 & 73.9 & 71.0 & 74.5 & 74.4 & \tb 76.5 & 73.8 & 38.7 & \tb 77.9 & 70.4 & 76.2 & 75.0 & \tr \textul{79.0} & 76.6 & 29.5 & \tr \textbf{79.6} & 48.8 & 57.7 & 37.8 \\
& \textbf{Synth} & 75.0 & 77.6 & 72.6 & 79.2 & 79.2 & 80.2 & 78.8 & 44.5 & \tb 83.6 & 74.6 & 80.1 & \tr 81.6 & \tr \textbf{85.1} & 81.6 & 35.4 & \tr 82.6 & 50.2 & 61.6 & 42.5 \\
& \textbf{Nat} & 58.0 & \ty 70.2 & 66.9 & 62.8 & 64.0 & 65.1 & 62.2 & 23.5 & 61.6 & 65.3 & 65.9 & 68.8 & \tr \textul{70.7} & \tr \textul{71.6} & 20.5 & \tr \textbf{73.7} & 36.2 & 44.4 & 22.4 \\
& \textbf{Real} & \ty 69.3 & 62.6 & \tb 68.2 & 66.7 & 64.5 & 71.6 & 64.0 & 29.7 & \tb 69.5 & 58.4 & 70.0 & 54.2 & 62.0 & 61.2 & 14.2 & \tr \textbf{73.0} & 54.4 & 54.1 & 33.2 \\
\midrule
\multirow{4}{*}{\rotninety{$\mathtt{sep}_m$}} & \textbf{Avg} &  \ty 90.7 & \ty \textbf{92.8} & 80.6 & 82.5 & 81.9 & \tb 85.0 & 81.8 & 67.2 & 83.2 & 78.4 & 83.1 & 80.3 & 84.2 & 80.8 & 63.6 & \tr 84.2 & 73.6 & 73.5 & 51.8 \\
& \textbf{Synth} & \ty 90.5 & \ty\textbf{94.1} & 80.6 & 85.5 & 85.2 & \tb 86.7 & 84.1 & 67.3 & 86.2 & 80.9 & 85.7 & 83.9 & \tr 87.8 & 84.9 & 65.8 & \tr 86.6 & 71.1 & 72.8 & 53.7 \\
& \textbf{Nat} & \ty 91.5 & \ty \textbf{92.6} & 84.2 & 75.1 & 75.6 & 82.8 & 77.9 & 75.7 & 80.5 & 71.2 & 80.9 & 76.7 & 81.8 & 73.3 & 68.6 & 81.7 & 80.5 & 76.7 & 44.5 \\
& \textbf{Real} & \ty \textbf{90.3} & \ty 87.9 & \tb 77.4 & 76.8 & 74.4 & 80.5 & 76.4 & 59.3 & 73.7 & 75.1 & 74.5 & 69.4 & 71.9 & 70.8 & 50.3 & 76.6 & \tg 77.3 & 73.6 & 50.7 \\
\midrule
\multirow{4}{*}{\rotninety{$\mathtt{delta}_m$}} & \textbf{Avg}  & 89.7 & 95.6 & 92.4 & 97.5 & 97.1 & 99.8 & 94.0 & 43.9 & 92.3 & 94.2 & \tr 104.7 &  102.0 & \tr\textbf{110.6} & \tr 103.7 & 37.7 & \tr 110.2 & 66.9 & 56.3 & 45.9 \\
& \textbf{Synth} & 89.9 & 95.6 & 92.5 & 97.6 & 97.3 & 99.9 & 93.9 & 44.6 & 92.5 & 94.4 & \tr 104.7 &  102.1 & \tr \textbf{110.7} & \tr 103.6 & 37.8 & \tr 110.1 & 67.2 & 56.7 & 46.7 \\
& \textbf{Nat} & 92.5 & 98.6 & 94.4 & 98.7 & 98.8 & 101.1 & 95.5 & 46.1 & 93.9 & 96.0 & \tr 105.5 & 103.0 & \tr \textbf{111.6} & \tr 104.6 & 39.3 & \tr 111.5 & 66.2 & 56.4 & 46.6 \\
& \textbf{Real} & 95.1 & 100.8 & 96.0 & 100.5 & 100.4 & 102.6 & 96.9 & 46.9 & 95.9 & 97.3 & \tr 106.8 & 104.2 & \tr \textbf{113.0} & \tr 105.9 & 39.4 & \tr \textbf{113.0} & 65.0 & 56.0 & 46.3 \\
\midrule
\multicolumn{2}{c}{\textbf{FLOP/run}} & \ty \textbf{604M} & \ty 688M & 224T & 224T & 224T & 224T & 224T & 224T & 1.66P & 140T & 140T & 140T & 140T & 140T & 140T & 860T & \tg 7.01T & \tg 7.01T & \tg 2.6T  \\
\bottomrule
\end{tabular}
}
\end{table*}

```


<!-- # 4. Figures

## TODO Combining multiple images into one image

I wanted to make a grid of adjacent images in a table.
I'm gonna be honest, I do not remember how I made this. But it works

```latex
\newcommand{\timg}[1]{\includegraphics[width=0.25\linewidth]{img/storyprop/#1}}

\newcommand{\specialcell}[1]{%
  \begin{tabular}[c]{@{}c@{}}#1\end{tabular}}

\newcommand{\imgf}[4]{\specialcell{\timg{#1}\timg{#2}\vspace{-3pt}\\\timg{#3}\timg{#4}}\hspace{-5pt}}

```



## making subfigures with/without captions

### subfig

### subcaption

### minipage

## How to do pyplot and make it readable

Generating your figure to be readable in pyplot
MAKE THE FIGURE SMALL IN GENERATION AS AN SVG THEN IT WILL BE BIG


## Colors etc

- blue!50!black
- rgb
- named colors (link) -->

<!-- # 5. TODO: Overleaf in VSCode

- use latex workshop
- use overleaf workshop

https://github.com/iamhyc/Overleaf-Workshop

Install instructions -->

# 4. The Dark Arts (Advanced)

> [!WARNING]
> These incantations will give you dark powers and break you free from the shackles of conference style files. Use wisely.

## Switching between conference formats

Some conference submission formats are disgusting, like ECCV.
I wrote a setup that gives me a flag to swap between that sickening abomination and the NeurIPS format.

First, you need both sty files in your project. For me it was `eccv.sty` and `neurips_2024.sty`.

```latex
% set this flag to 0 to use ECCV format, 1 to use neurips format
\def\useformat{1}
\if\useformat0
    \documentclass[runningheads]{llncs}
    %%%%%% START ECCV HEADER
    \usepackage[review,year=2024,ID=11071]{eccv}
    % final submission, options
    %\usepackage{eccv}
    %\usepackage[mobile]{eccv}
    \usepackage{eccvabbrv}
    %%%%%% END ECCV HEADER
\else
    %%%%%% NEURIPS HEADER
    \documentclass{article}
    % if you need to pass options to natbib, use, e.g.:
    % before loading neurips_2023
    \usepackage[final,nonatbib]{neurips_2024}
    \usepackage[sort&compress,numbers]{natbib}
    %     \usepackage{neurips_2023} % submission anonymized
    %     \usepackage[final]{neurips_2023}
    %%%%% END NEURIPS HEADER
    %%%%%%%%%% MORE ACL STUFF
    % For proper rendering and hyphenation of words containing Latin characters (including in bib files)
    \usepackage[utf8]{inputenc}
    \usepackage[T1]{fontenc}
    \usepackage{microtype}
    \usepackage{inconsolata}
    %%%%% OPTIONS FOR NICER FONTS (MUST COMMENT OUT FOR NEURIPS FINAL VERSION)
    \usepackage{times}
    \usepackage{subcaption}
    \usepackage{adjustbox}
\fi
```

Then throughout the document for select other commands that I wanted to only use with one I would have to add that flag into them. `\useformat0` or `1` would switch between either ECCV or NeurIPS.


## Making a centered figure wider than `\pagewidth`

- dark art: making a figure oversized relative to the text
*there are legitimate reasons to do this, for example if your figure has whitespace baked in but you want the filled part to be 100%*

```latex
\usepackage{graphicx}
\usepackage{adjustbox}

\newcommand{\bigln}[2]{
    \begin{adjustbox}{center}
        \resizebox{#1\linewidth}{!}{
            \centering
            #2
        }
    \end{adjustbox}
}
```

You wrap the `\includegraphics` inside of the `\bigln`

## Teaser figures in the *ACL format

Suppose you want to put a full-width figure at the top of your ACL paper, as seen in this example.


![Top of Michael's ACL 2023 paper with a big teaser figure](https://gist.github.com/michaelsaxon/21ab96429ffb86fb7691945dfe3f657a/raw/6ec0322422b20f70264faf1211e53138d5409021/0_z_cccl_example.png)


The `\figure*{}` macro does not work to insert a full-width figure above the abstract in the ACL template for some reason. Thus, we need to hack together a command that does it for us.

This command does a few things:
- Breaks out of the document rendering defined by the ACL template with `strip`
- Manually implements a hacked Figure macro with manually-written "Figure 1:", manual font size setting, etc.
- Manually sets the figure count variable to not duplicate "Figure 1"

```latex
%%%%%%%%% in preamble %%%%%%%%%

% to make \strip work
\usepackage{cuted}
\usepackage{hyperref}

% hack commands to create a centered `\incudegraphics`-like macro that 
% doesn't cause weird errors
\newcommand{\adjustimg}{% Horizontal adjustment of image
  \hspace*{\dimexpr\evensidemargin-\oddsidemargin}%
}
\newcommand{\centerimg}[2][width=\textwidth]{% Center an image
  \makebox[\textwidth]{\adjustimg\includegraphics[#1]{#2}}%
}
```

Once we have defined our figure commands in the preamble and imported relevant packages, we insert the figure at the top of our document, before `\begin{abstract}` is written.

```latex
%%%%%%%%% in document %%%%%%%%%

%%% before abstract %%%

\begin{strip}
  % set this to something that looks good.
  \vspace{-58pt}

  % we use the centerimg macro here instead of \includegraphics to make the text 
  % on the rest of this fake figure macro correctly render
    \noindent\centerimg[width=\linewidth]{TEASER_FIG}

  % Note: we need to manually write the text "Figure 1:" here as we aren't actually 
  % using the "figure" macro.
  \fontsize{10pt}{12pt}\selectfont
    Figure 1: TEASER CAPTION HERE
  \label{fig:teaser}

\end{strip}

% because we manually made a figure without the macro, we need to increment the 
% figure counter so that the next one is Figure 2
\setcounter{figure}{1}

%%% start abstract %%%
```

Because we didn't produce this inside of the `figure` macro, using `\ref{}`, `\cref{}`, and `\autorref` won't work! Instead, we have to use this hack:

```latex
% replacing ref
...in Figure \hyperref[fig:teaser]{1}...

% replacing autorref
...in \hyperref[fig:teaser]{Figure 1}...

etc
```
