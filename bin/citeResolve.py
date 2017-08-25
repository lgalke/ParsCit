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
from collections import defaultdict

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
    
    

def process_file(path, dir = None, outTableFile = None):
    """ Pass the given path to function map_citations() to generate citation dictionary,
    generate input and output file handles and calls the function replace_withIdentsithIdents()
    """
    print("Processing", path)
    
#    if identsTable:    #when identsTable is set (optional in the main function), generate an output file for it
#        identsTableFile = open("{}/corpus".format(dir or os.getcwd()), 'a') # tableFile would be contained by the outDirectory (if given)
#    if outTableFile:
#        identsTableFile =   
    citMaps = map_citations(path, outTableFile)
    
    # generate the outFile in which the output text (in which citations are replaced by identifiers) will be written
    outfilename = "{0}.withIdents".format(os.path.splitext(os.path.basename(path))[0])   
    outfile = open("{}/".format(dir or os.getcwd()) + outfilename, 'w') # output text will be contained by the outDirectory (if given)
    
    infile = open(path, 'r')
    
    replace_withIdents(infile, citMaps, outfile)
    
    
def map_citations(path, identsTablefile):
    """ Extracts citations of the document specified by the "path", parses the
    xml output, makes an identifier for each citation and returns a tuple of 3 
    dictionaries for citations. prints the citation identifiers in the given TableFile 
    if the optinal parameter -t is given in the main function
    """
    #extracts citations by ParsCit and parses the xml output in a root element
    process = subprocess.Popen([PARSCIT_EXEC, path],
                               stdout=subprocess.PIPE)
    xml = process.stdout.read()
    root = ET.fromstring(xml)

    # dictionary with {citString:identifier} items
    citeStrMap = defaultdict(set)

    # list of identifiers
    citation_ids = []    
    # build the identifier for each citation
    for citation in root.iter("citation"):
       
       #skip the citation when it's attribute valid == 'false', since it does not provide enough data for identification
       if citation.get('valid') == "true":
       
          #get the first author of current citation for identifier
          author = citation.find('authors').find('author').text

          # get the title or booktitle or journal(special case) of the current citation as the title for identifier
          try:
              title = citation.find('title').text if citation.find('title') is not None else citation.find('booktitle').text
          except AttributeError:
              title = citation.find('journal').text    
          
          #get the date of the current citation for identifier
          date = citation.find('date').text
          
          #make the identifier for the current citation
          identifier = identify(author, date, title)
          #add the current identifier to the idslist
          citation_ids.append(identifier)
          
          
          #get the contexts (where the current citation are cited) and citStrings (citation string) 
          #for the current citation in the body of the given text file 
          try:
              contexts = citation.find('contexts')
              for context in contexts.findall('context'):
                 citeStr = context.get('citStr')
                 #set the citeString:identifer item for the current citation in the corresponding dictionary
                 citeStrMap[citeStr].add(identifier)
          
          #pass if no context exists (might occur since ParsCit extarcts the citation 
          #based on the rawreference string in the reference section of the given text file       
          except AttributeError: 
              pass
          
    
    if identsTablefile:       # when the table file is not None means that the optional argument identiferTable in the main is sepecified
        in_document = os.path.splitext(os.path.basename(path))[0]    # get the input path file name    
        print(in_document, *citation_ids, file=identsTablefile)       #print the citation_ids in a line in the provided tableFile       
    
    #print(sorted(citeStrMap))
    return citeStrMap

def replace_withIdents(infile, citeStrMap, outfile):
    """ receives the text file object and the corresponding dictionary for citations 
    as input arguments and replaces the citations with identifers and write the text in the given
    outfile object       
    """
    # filehandles: infile, outfile
    text = infile.read()
    text = text.replace("\n", " ")
    
        
    #do the replacements based on {citString}s; replaces the citatios within the body of the text     
    for citeStr, identifiers in citeStrMap.items():
    	# warning: identifiers is now a set 
        text = text.replace(citeStr, ' '.join(list(identifiers)))

   
    outfile.write(text)

        
    
def main():
    print("[citex] Hello world")

    # argument parser setup
    parser = argparse.ArgumentParser()
    parser.add_argument('paths',    # the identifier
                        nargs='+',  # at least one but arbirary amount of files
                        help='Specify the files to extract citations from.')
    parser.add_argument('-o', '--outDirectory',
                         help = 'specify the output destination folder.')
    parser.add_argument('-t', '--identifersTable', 
                         help = 'specify the file for identifier table.')                                         

    # invoke actual parsing of command line arguments
    args = parser.parse_args()
    outDir = args.outDirectory
    try:
        if not os.path.isdir(outDir):
            os.mkdir(outDir)
    except TypeError:
        pass
    
    try:
        outTableFile = open(os.path.abspath(args.identifersTable), 'w')    
    except AttributeError:
        outTableFile = None
        
    
           
    for path in args.paths:                  # Loop over all provided paths...
        if os.path.isdir(path):              # loop over files if the current path is a file folder
            for filename in os.listdir(path):
                pathName = os.path.realpath(os.path.join(path, filename))    #generate path name for each file 
                process_file(pathName, outDir, outTableFile)       # ...and process each file.
        else:
            process_file(path, outDir, outTableFile)      # if the current path specifies a file
            

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    main()
