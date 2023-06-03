# blog-generator
Pelican-based blog generator for the UCSB Website

This package contains all the necessary components to generate a static blog for nlp.cs.ucsb.edu/blog.

## Requirements
- pelican (static site generator for python)
- nodejs
- pelican-katex (latex generator)

## Usage
1. Clone this repo to folder neighboring clone of `website`
2. Run `pip install -r requirements.txt` in Python 3.5+
3. Place any markdown or resturctured text blog posts in `blog-base/content`, images and other static files for posts go in `blog-base/content/images`, see `blog-base/content/sample.md` for an example.
4. If author doesn't have an author page and wants one, create one in `uscb-theme/templates/authorbios`.
5. cd to `blog-base` and run `pelican content -t ../uscb-theme -o ../../website/blog`
6. Verify that generated blog is correctly placed in blog folder in the website repo, publish using usual process.

## To-do
- [ ] Verify that generator works from fresh install on new machine
- [ ] Verify that the RSS feeds work correctly when published online
- [ ] Verify that the relative/absolute pathing is working correctly