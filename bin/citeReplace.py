#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Parsing of command-line arguments
# https://docs.python.org/3/howto/argparse.html
import argparse

# Subprocess management, such as invoking ParsCit
# https://docs.python.org/3/library/subprocess.html
import subprocess
import io
import os
import re
import xml.etree.ElementTree as ET
import sys
import fileinput

"""
Example usage:
python3 citex.py -h
python3 citex.py file1.txt file2.txt file3.txt

"""
WORDS_RE = re.compile(r'\w\w\w\w+')
AUTHOR_RE = re.compile(r'\w\w+')
YEAR_RE = re.compile(r'\d\d\d\d')

PARSCIT_EXEC = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            'citeExtract.pl')

def identify(author, year, title):
    """ Transforms meta-data into unique identifier
    >>> identify("Galke, L., Scherp, A.", "17 Sept 2017", "Evaluating the Impact of Word Embeddings on Similarity Scoring in Practical          Information Retrieval")
    '@galke2017evaluating'
    >>> identify("Sadaati, Hamidreza", 2016, "Inspecting some things")
    '@sadaati2016inspecting'
    """
    try:
        year = str(int(year))
    except ValueError:
        m = YEAR_RE.search(year)
        year = m.group(0) if m else ""
    # Find first word with more than 3 characters
    m = WORDS_RE.search(title)
    word = m.group(0).lower() if m else ""
    # We try to find first author, even if multiple authors are given
    m = AUTHOR_RE.search(author)
    author = m.group(0).lower() if m else ""
    return "@{}{}{}".format(author, year, word)
    
    

def process_file(path):
    """ Extracts citations of the document specified by the "path", parses the
    xml output, makes an identifier for each citation and prints them
    in one line in the file object specified by the "fileOut"
    """
    print("Processing", path)
    citation_dict = map_citations(path)
    outfilename = "{0}.withIdents".format(os.path.splitext(os.path.basename(path))[0])
    outfile = open(outfilename, 'w')
    infile = open(path, 'r')
    replace_markers(infile, citation_dict, outfile)
    
def map_citations(path):
    """ Extracts citations of the document specified by the "path", parses the
    xml output, makes an identifier for each citation and returns a dictionary 
    with "marker: identifier" items
    """

    process = subprocess.Popen([PARSCIT_EXEC, path],
                               stdout=subprocess.PIPE)
    xml = process.stdout.read()
    root = ET.fromstring(xml)

    citation_dict = {}
    
    # FIXME properly extract: FIXED
    # build the identifier for each citation
    for citation in root.iter("citation"):
       # FIXME gives error when other markers: FIXED
       
       #skip the citation when it's attribute valid == 'false', since it does not provide enough data for identification
       if citation.get('valid') == "true":
          
          author = citation.find('authors').find('author').text

          # get the title or booktitle or journal(special case) as the title for identifier
          try:
            title = citation.find('title').text if citation.find('title') is not None else citation.find('booktitle').text
          except AttributeError:
            title = citation.find('journal').text    
          
          date = citation.find('date').text
          
          marker = citation.find('marker').text
          
          citation_dict[marker] = identify(author, date, title)

    print(citation_dict)
    return citation_dict
    

def replace_markers(infile, citation_dict, outfile):
    # filehandles: infile, outfile
    text = infile.read()
    for marker, identifier in citation_dict.items():
        text = text.replace(marker, "{}".format(identifier))

    outfile.write(text)

    # for line in infile:
    #     for marker in citation_dict:
    #         identifier = citation_dict[marker]
            
    #         if marker in line:
    #             line = line.replace(marker, "[{0}]".format(identifier))
    #     print(line, file = outfile)
    
    
def main():
    print("[citex] Hello world")

    # argument parser setup
    parser = argparse.ArgumentParser()
    parser.add_argument('paths',    # the identifier
                        nargs='+',  # at least one but arbirary amount of files
                        help='Specify the files to extract citations from.')

    # invoke actual parsing of command line arguments
    args = parser.parse_args()

    
    for path in args.paths:          # Loop over all provided paths...
        process_file(path)       # ...and process each file.


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    main()
