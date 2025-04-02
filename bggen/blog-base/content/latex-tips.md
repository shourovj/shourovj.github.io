Status: draft
Title: Michael's TeXronomicon (LaTeX tips, tricks, and hacks)
Date: 2025-04-02 15:32
Category: Tips
Tags: latex
Authors: Michael Saxon
Summary: Various tricks and lessons I've learned from messing around in LaTex. Adapted and extended from a gist by [me](https://gist.github.com/michaelsaxon).
Image: https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.proceso.com.mx%2Fu%2Ffotografias%2Ffotosnoticias%2F2022%2F10%2F9%2F162629.jpg&f=1&nofb=1&ipt=c4ac0da6ced33fff2f955f0c231b98522dd003d3b00215f38f4e1b73fcae4b91&ipo=images
remove_footnote_section: true

[TOC]

The keys to understanding LaTeX are mastering Knuth-isms and managing your sanity.

# 1. Making commands 

You should make commands. At their simplest, they let you reuse text or formatting easily. But they can do much more. First, a little bit about how to make them:

I know two ways to make commands, `\newcommand` and `\renewcommand`. 
If the command already exists, `\renewcommand` will overwrite it (sometimes very useful). For example, I used `\renewcommand` to fix a critical flaw in the COLM format.

Consider this snippet:

```latex
Inertia is a property of matter \cite{nye1995science}.
```

It renders as:

> Inertia is a property of matter Nye et al. (1995).

Instead of correctly rendering as:

> Inertia is a property of matter (Nye et al., 1995).


In other words, the COLM format was treating `\cite{}` as `\citet{}` rather than `\citep{}`, as it is in all other conference formats.

With `\renewcommand` it's a one line fix:

```latex
\renewcommand{\cite}{\citep}
```

Probably the most common use case I see for writing commands is to make named comments in collaborative docs.


## Comment commands

The typical way we implement comment commands is something simple like: 

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

## Fixing infuriating spacing issues

Often you want to define a command as a simple macro for some name you're using throughout the paper. Something like

```latex
\newcommand{\method}{\textsc{BiG-BiRd}}
```

This has the benefit of letting you change it if you aren't sure what your method is. Also if you want to do obnoxious extra formatting like a weird font or color[^1], it's easy to reuse.

[^1]: As I often do...

But as I'm sure you know, this method has an infuriating spacing behavior, where if you add a space *in* the command it's always there, even before a period. If you don't add a space it will *ignore* spaces behind the command, so "`\method is great`" renders as "BiG-BiRdis great". Unless you do some hack every time you want a space like "`\method~ is great`".

I recently was shown the `\xspace` package, my savior. Just add:

```latex
% in preamble
\usepackage{xspace}

\newcommand{\method}{\textsc{BiG-BiRd}\xspace}
```

And your problems are solved.


# 2. Doing text right



## citations

- resizing text
- defining and setting special text colors
- highlighting and colored background for text

- cite, citet, citep

## colored boxese

- `\vig` and making a nice colored box

gets you something like 

> [!NOTE]
> lorem ipsum 

> [!IMPORTANT]
> cool stuff

```latex
\usepackage[skins,breakable]{tcolorbox}

\newtcolorbox{boxred}{enhanced,colback=orange!5!white,colframe=orange!75!black,breakable=true}
\newtcolorbox{boxblue}{enhanced,colback=blue!5!white,colframe=blue!75!black,breakable=true}

\newcommand{\vig}[2]{
\begin{boxblue}
\textit{\color{blue!50!black}\textbf{#1}}

\vspace{6pt}#2
\end{boxblue}
}

\newcommand{\case}[2]{
\begin{boxblue}
\textit{\color{blue!50!black}\textbf{Case study}: #1}\\

#2
\end{boxblue}
}
```

## Annoying fancy colored text
cursor gave me this atrocity
`\newcommand{\methodfancy}{\textbf{\textsc{\textcolor[rgb]{0,0,0}{T}\textcolor[rgb]{0.2,0,0}{h}\textcolor[rgb]{0.4,0,0}{o}\textcolor[rgb]{0.5,0,0}{u}\textcolor[rgb]{0.6,0,0}{g}\textcolor[rgb]{0.7,0,0}{h}\textcolor[rgb]{0.8,0,0}{t}\textcolor[rgb]{0.85,0,0}{T}\textcolor[rgb]{0.9,0,0}{e}\textcolor[rgb]{0.95,0,0}{r}\textcolor[rgb]{1,0,0}{m}\textcolor[rgb]{1,0,0}{i}\textcolor[rgb]{1,0,0}{n}\textcolor[rgb]{1,0,0}{a}\textcolor[rgb]{1,0,0}{t}\textcolor[rgb]{1,0,0}{o}\textcolor[rgb]{1,0,0}{r}}}\xspace}`

```latex
\newcommand{\resourcename}{\texttt{\textbf{\gradientRGB{T2IScoreScore}{68,67,147}{61,130,217}}}}
\newcommand{\tscolor}{\texttt{\textbf{\gradientRGB{TS2}{68,67,147}{61,130,217}}}}
\newcommand{\rncolor}{\includegraphics[trim=0 0.2ex 0 -1.5ex,height=1.8ex]{module/T2IScoreScore.pdf}}
```

## annoying inline icons
`\vspace{-3pt}\raisebox{-3pt}{\includegraphics[width=20pt]{pics/terminator_logo.png}}`
you can just directly use the `\includegraphics` command inside of text

## exotic symbols

Egyptian hieroglyphs!

How I did the playstation icons
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

\newcommand{\pssqu}{
\pssymb{6pt}{
    \draw (0,0) circle [radius=1.5];
    \draw[line width=5pt, magenta] (-0.8,0.8) -- (0.8,0.8);
    \draw[line width=5pt, magenta] (-0.8,0.8) -- (-0.8,-0.8);
    \draw[line width=5pt, magenta] (0.8,-0.8) -- (0.8,0.8);
    \draw[line width=5pt, magenta] (0.8,-0.8) -- (-0.8,-0.8);
}}

\newcommand{\pstri}{
\pssymb{6pt}{
    \draw (0,0) circle [radius=1.5];
    \draw[line width=5pt, teal] (0.8,-0.6) -- (-0.8,-0.6);
    \draw[line width=5pt, teal] (0.8,-0.6) -- (0,0.8);
    \draw[line width=5pt, teal] (0,0.8) -- (-0.8,-0.6);
}}
... in title

$^\pscirc$, $^\psx$, $^\pssqu$, $^\pstri$
```
This produces something roughly like:
Michael Saxon<sup><img width="15pt" src="https://t2iscorescore.github.io/static/images/psx.svg"/><img width="15pt" src="https://t2iscorescore.github.io/static/images/psc.svg"/></sup>

## Non-Latin alphabets on arXiv

XeLaTeX is the best way to do this. But arXiv (as of writing) doesn't support it 😭😭😭😭😭

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
```

This makes things like `\inlinejp{お前はもう死んでいる}` or `\inlinezh{迈克不喜欢卷}` to render properly.

## Learn the weird Knuth-isms

Don Knuth, the creator of TeX (pictured in thumbnail), is a bit of a strange guy.
If you're experienced with LaTeX you're used to remembering a lot of weird names for things, like `\ell` for the fancy curly "L", `\sim` for the tilde. 
For most of the things you need, you're gonna have to just look them up yourself, but here's a fun little rant about the most perplexing one to me.
*The LaTeX commands for sizing things are hilarious.*

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

Ok, I can wrap my head around that setup. Of course "large" is bigger than "small." Why can't you make text `\big`?

Well, `\big` is a command, but it means something completely different from `\large`. It controls symbols...

The purpose of big is to make something like `(\sum_{i=0}^n i)` not look like garbage[^2].

[^2]: This post has been edited to remove foul language.

will look like shit, because the parentheses are too small. 
The correct way to fix this is to use the `\left` and `\right` commands to automatically size the brackets based on their contents.

```latex
\left(\sum_{i=0}^n i\right)
```

But if you want a fun window into more Knuth-isms, here's how you manually control bracket size (in ascending order):

- `\big`
- `\Big`
- `\bigg`
- `\Bigg`



See here in [Overleaf's docs](https://www.overleaf.com/learn/latex/Font_sizes%2C_families%2C_and_styles)


# 3. Tables

- colortbl
### basic booktabs hygiene


### coloring the inside of your table
`\rowcolor{}`

In TS2 we also had colored cells
```latex
\usepackage{rotating}

%...

\newcommand{\ty}[0]{\cellcolor{otheryellow}}
\newcommand{\tr}[0]{\cellcolor{dsgred}}
\newcommand{\tb}[0]{\cellcolor{tifablue}}
\newcommand{\tg}[0]{\cellcolor{llmgreen}}
```

### special table symbols
lil commands like
- samel to more cleanly cross out a bunch of rows with the same value
`\newcommand{\samel}[0]{\multicolumn{1}{l}{\space\hspace{0.5em}\vline}}`

### rotating text for compactness
- rotating text
```latex
\newcommand{\myrotcell}[1]{\begin{turn}{75}
#1
\end{turn}
}
\newcommand{\rotninety}[1]{\begin{turn}{90}
#1
\end{turn}
}
```


# 4. Figures

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
- named colors (link)

# TODO: Overleaf in VSCode

- use latex workshop
- use overleaf workshop

https://github.com/iamhyc/Overleaf-Workshop

Install instructions

# 5. The Dark Arts (Advanced)

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


## breaking a figure out of the text width

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

#### Credit

I worked out how to do most of this hack myself just consulting stackoverflow and documentation of the commands. The one exception was figuring out the `\adjustimg` and `\centerimg` commands could be used to replace `\centering`, which was necessary to avoid this super annoying bug where the text placement doesn't "see" the image and instead they superimpose on each other.

I found the exact code I needed for this in an answer provided by
["Werner" on StackOverflow](https://tex.stackexchange.com/a/39148).
Thank you Werner, you absolute chad.

