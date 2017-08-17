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
    
    

def process_file(path, dir = None):
    """ Pass the given path to function map_citations() to generate citation dictionary,
    generate input and output file handles and calls the function replace_withIdentsithIdents()
    """
    print("Processing", path)
    citMaps = map_citations(path)
    outfilename = "{0}.withIdents".format(os.path.splitext(os.path.basename(path))[0])
    outfile = open("{}/".format(dir or os.getcwd()) + outfilename, 'w')
    infile = open(path, 'r')
    replace_withIdents(infile, citMaps, outfile)
    
    
def map_citations(path):
    """ Extracts citations of the document specified by the "path", parses the
    xml output, makes an identifier for each citation and returns a tuple of 3 
    dictionaries for citations
    """
    #extracts citations by ParsCit and parses the xml output in a root element
    process = subprocess.Popen([PARSCIT_EXEC, path],
                               stdout=subprocess.PIPE)
    xml = process.stdout.read()
    root = ET.fromstring(xml)

    # dictionary with {marker:identifier} items
    markerMap = {}
    # dictionary with {citString:identifier} items
    citeStrMap = defaultdict(set)
    # dictionary with {rawString:identifier} items
    rawStringMap = {}
        
    # FIXME properly extract: FIXED
    # build the identifier for each citation
    for citation in root.iter("citation"):
       # FIXME gives error when other markers: FIXED
       
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
          
          #get the marker of the current citation 
          marker = citation.find('marker').text
          
          #set the marker:identifer item for the current citation in the corresponding dictionary
          markerMap[marker] = identifier 
          
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
          
          #get the rawString (reference string in the reference section of the given text file) 
          rawString = citation.find('rawString').text
          #set the rawString:identifer item for the current citation in the corresponding dictionary
          rawStringMap[rawString] = identifier
              
    #make a tuple of the three dictionaries to return       
    citeMaps = (markerMap, citeStrMap, rawStringMap)
    #print(sorted(citeStrMap))
    return citeMaps

def replace_withIdents(infile, citeMaps, outfile):
    """ receives the text file object and the corresponding three dictionaries for citations 
    as input arguments and replaces the citations with identifers and write the text in the given
    outfile object       
    """
    # filehandles: infile, outfile
    text = infile.read()
    
    #get the three dictionaries from the given tuple
    markerMap = citeMaps[0]
    citeStrMap = citeMaps[1]
    rawStringMap = citeMaps[2]
    
    
    #do the replacements based on {marker}s; this suffices for the whole replacmet work 
    #when {marker} and {citString} are the same in the parsed XML, 
    #e.g. when references are cited with numbers   
        
    #do the replacements based on {citString}s; replaces the citatios within the body of the text     
    for citeStr, identifiers in citeStrMap.items():
    	# warning: identifiers is now a set 
        text = text.replace(citeStr, ' '.join(list(identifiers)))

    # for the reference list
#    for marker, identifier in markerMap.items():
#        text = text.replace(marker, identifier)
        
    #do the replacements based on {rawString}s; adds the identifiers in the reference section of the text        
#    for rawString, identifier in rawStringMap.items():
#        searchString = rawString[0:min(40, len(rawString))]
#        text = text.replace(searchString, "{0}. {1}".format(identifier, searchString))
#        
    #remove duplications of identifiers in text
    # for identifier in rawStringMap.values():
    #     dupIdentifier = "{0} {0}".format(identifier)
    #     while text.find(dupIdentifier) > -1: 
    #        text = text.replace(dupIdentifier, identifier)       
   
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

    # invoke actual parsing of command line arguments
    args = parser.parse_args()
    outDir = args.outDirectory
    try:
        if not os.path.isdir(outDir):
            os.mkdir(outDir)
    except TypeError:
        pass
            
           
    for path in args.paths:                  # Loop over all provided paths...
        if os.path.isdir(path):              # loop over files if the current path is a file folder
            for filename in os.listdir(path):
                pathName = os.path.realpath(os.path.join(path, filename))    #generate path name for each file 
                process_file(pathName, outDir)       # ...and process each file.
        else:
            process_file(path, outDir)      # if the current path specifies a file
            

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    main()
