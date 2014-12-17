#from scrape import start_selenium
#from scrape import scrape_pdf
#from scrape import get_pmid_xml

## WORKFLOW
# Import CSV or something of PMID codes 
# Search scopus for each pmid
# Save xml 
# Parse xml for doi, if exist, 
# Parse xml for citations, if exists, save to CSV? DB? 
# Scape doi link for PDF
# Parse PDF for text

import scrape
import data_tools

## define api_key
## this must be requested from scopus
api_key = "007c9e3c95c43a49341b251534dac2ae"



## define data directories
## create them if necessary

dir_input = "input/" # put csv file with eid or pmid or something else. For inital search  
dir_citations = "output/citations/" # to save csv files
dir_pdf_ocr = "output/pdf_ocr/" # to save ocr'd files
dir_pdf = "output/pdfs/" # to save pdf files
dir_raw_xml = "output/raw_xml/" # to save raw xml from initial search 
dir_raw_xml_refs = "output/raw_xml_refs/" # save xml to extract references
dir_raw_xml_cited_by = "output/raw_xml_cited_by/" # save xml files to extract stuff
dir_raw_xml_cited_by_refs = "output/raw_xml_cited_by_refs/" #
dir_raw_xml_coauthors = "output/raw_xml_coauthors/" #
dir_raw_xml_coauthors_pubs = "output/raw_xml_coauthors_pubs/" #


ls_dir = list([dir_pdf, dir_raw_xml, dir_citations, dir_pdf_ocr,
               dir_raw_xml_cited_by,dir_input,
               dir_raw_xml_cited_by_refs, dir_raw_xml_refs, dir_raw_xml_coauthors,
               dir_raw_xml_coauthors_pubs])

data_tools.test_data_dirs(ls_dir)
 
reload(data_tools)
reload(scrape)

## import pdb

## Import CSV of PMID
#file = "pmid.csv"
file = dir_input + "diederik_stapel.csv"
ls_pmid = data_tools.csv_to_list(file,"EID")

len(ls_pmid)

## need to use proper subsetting [0:1] else for loop messed up
test = ls_pmid
prob = ("2-s2.0-79959828286",)

for pmid in ls_pmid:
    print(pmid)


for pmid in ls_pmid:
    print(pmid)
    # get xml or json from scopus for pmid code
    xml_pmid = scrape.get_pmid_xml(api_key,"eid",pmid)

    if xml_pmid['doi'] is False and xml_pmid['xml_text'] is False:
        next

    if xml_pmid['xml_text'] is False:
        print "no citation/abstract data for this pmid"
    else:
        data_tools.request_to_file(xml_pmid['xml_text'], pmid, dir_raw_xml)



## After all PDFs and XML files are downloaded, there needs to be post processing
## XML files need to parse into CSV files or something
## PDF files need to be converted to txt files for analysis

import os 
import re
import parsing

## list of xml files to process
ls_xml = os.listdir(dir_raw_xml)
#ls_xml = [re.sub('^[.][#].*',"",x) for x in ls_xml]
## filter for files that are open by emacs or other programs. 
ls_xml = [x for x in ls_xml if not re.match('^[.][#].*',x)]
# filter(bool,ls_xml)
# map(bool, [re.match('^[.][#].*',x) for x in ls_xml])


reload(parsing)
reload(data_tools)
reload(scrape)

## create csv files
meta_header = ["eid","pubmed-id","doi","source_type","pub_name","issn","title", 
               "abstract", "cited_by_url"]
data_tools.test_csv_exist(dir_citations,"metadata", meta_header)

authors_header = ["eid", "pubmed_id", "author_id", "author_seq", "author_name", 
                  "author_surname", "author_given", "author_aff_id"]
data_tools.test_csv_exist(dir_citations, "authors" , authors_header)
refs_header = ["eid","pubmed_id", "ref_id","ref_title","ref_authors_cnt"]
data_tools.test_csv_exist(dir_citations, "references" , refs_header)

for file in ls_xml:
    file = dir_raw_xml + file
    print "The file is " + file 
    meta = parsing.parse_xml(file).get_meta()
    authors = parsing.parse_xml(file).get_authors()
    refs = parsing.parse_xml(file).get_references()
    #print authors
    try:
        data_tools.append_csv(dir_citations, "metadata", meta, meta_header)
        data_tools.append_csv(dir_citations, "authors", authors, authors_header)
        data_tools.append_csv(dir_citations, "references", refs, refs_header)
    except:
        print "Either error writing to csv or csv not found"

## Save Coauthor networks


file_coauth = dir_citations + "authors.csv"
ls_coauth = data_tools.csv_to_list(file_coauth,"author_id")
ls_coauth = filter(lambda x: x!="7006053052",ls_coauth) #remove stapel id stuff


reload(scrape)

for url in ls_coauth:
    au_id = url
    url = "http://api.elsevier.com/content/search/index:SCOPUS?query=" + "au-id" + "(" + au_id + ")" + "&count=200" + "&view(complete)" + "&field=author,eid,pubmed_id,afid"
    xml_pmid = scrape.get_scopus_url(api_key,url)
  
    if xml_pmid.text is False:
        print "no citation/abstract data for this pmid"
    else:
        data_tools.request_to_file(xml_pmid.text, au_id, dir_raw_xml_coauthors)

## Parse 2nd level co-author data
primary_authid = "7006053052" # for stapel

ls_xml_auths2 = os.listdir(dir_raw_xml_coauthors)
ls_xml_auths2 = [x for x in ls_xml_auths2 if not re.match('^[.][#].*',x)]

authors2_header = ["primary_authid","secondary_authid", "eid", "pubmed_id", "author_id",  "author_name", 
                  "author_surname", "author_given", "author_aff_id"]

data_tools.test_csv_exist(dir_citations, "authors2" , authors2_header)

for file in ls_xml_auths2:
    secondary_authid = file[:-3]
    file = dir_raw_xml_coauthors + file
    print "The file is " + file 
    authors2 = parsing.parse_xml(file).get_authors2(primary_authid, secondary_authid)
    try:
        data_tools.append_csv(dir_citations, "authors2", authors2, authors2_header)
    except:
        print "Either error writing to csv or csv not found"
 

reload(parsing)
authors2 = parsing.parse_xml(file).get_authors2(prime_authid)
print authors2[0:3]

test = {"test":None, "test2":None}
print type(test)
print test
 
## Extract Reference XML and

file_refs = dir_citations + "references.csv"
keys = ["eid","ref_id"]
ls_refs = data_tools.csv_to_dict(file_refs,keys)

for url in ls_refs:
    eid = url["ref_id"]
    xml_pmid = scrape.get_pmid_xml(api_key,"eid",eid)

    if xml_pmid['xml_text'] is False:
        print "no citation/abstract data for this pmid"
    else:
        data_tools.request_to_file(xml_pmid['xml_text'], eid, dir_raw_xml_refs)

### now parse xml files for reference authors 

ls_xml_refs = os.listdir(dir_raw_xml_refs)
ls_xml_refs = [x for x in ls_xml_refs if not re.match('^[.][#].*',x)]

authors_header = ["eid", "pubmed_id", "author_id", "author_seq", "author_name", 
                  "author_surname", "author_given", "author_aff_id"]
data_tools.test_csv_exist(dir_citations, "reference_authors" , authors_header)

for file in ls_xml_refs:
    file = dir_raw_xml_refs + file
    print "The file is " + file 
    authors = parsing.parse_xml(file).get_authors()
    try:
        data_tools.append_csv(dir_citations, "reference_authors", authors, authors_header)
    except:
        print "Either error writing to csv or csv not found"

        
## Extract Forward cites 

file_cited_by = dir_citations + "metadata.csv"
keys = ["eid","cited_by_url"]
ls_cited_by = data_tools.csv_to_dict(file_cited_by,keys)

web = scrape.get_scopus_url(api_key,ls_cited_by[0])

for url in ls_cited_by:
    eid = url["eid"]
    cited_by_url = url["cited_by_url"] + "&count=200"
    web = scrape.get_scopus_url(api_key,cited_by_url)
    xml_text = web.text 
    data_tools.request_to_file(xml_text, eid, dir_raw_xml_cited_by)

## parse back cites 
ls_xml_cited = os.listdir(dir_raw_xml_cited_by)
ls_xml_cited = [x for x in ls_xml if not re.match('^[.][#].*',x)]

cited_by_header = ["eid","pubmed_id", "citedby_eid","entry_title","entry_journal","entry_lead_author","entry_affiliation", "entry_doi","entry_cited_by_cnt"]
data_tools.test_csv_exist(dir_citations, "cited_by_meta" , cited_by_header)

reload(parsing)

for file in ls_xml_cited:
    eid = file
    file = dir_raw_xml_cited_by + file
    print "The file is " + file 
    cited_by = parsing.parse_xml(file).get_cited_by(eid)
    #print authors
    try:
        data_tools.append_csv(dir_citations, "cited_by_meta", cited_by, cited_by_header)
    except:
         print "Either error writing to csv or csv not found"


## Now download xml for cited_by files 

file_cit_refs = dir_citations + "cited_by_meta.csv"
keys = ["eid","citedby_eid"]
ls_cit_refs = data_tools.csv_to_dict(file_cit_refs,keys)

for url in ls_cit_refs:
    eid = url["citedby_eid"]
    xml_pmid = scrape.get_pmid_xml(api_key,"eid",eid)

    if xml_pmid['xml_text'] is False:
        print "no citation/abstract data for this pmid"
    else:
        data_tools.request_to_file(xml_pmid['xml_text'], eid, dir_raw_xml_cited_by_refs)


## now extract author information from citedby xml files 

ls_xml_citedby_auth = os.listdir(dir_raw_xml_cited_by_refs)
ls_xml_citedby_auth = [x for x in ls_xml_citedby_auth if not re.match('^[.][#].*',x)]

authors_header = ["eid", "pubmed_id", "author_id", "author_seq", "author_name", 
                  "author_surname", "author_given", "author_aff_id"]

data_tools.test_csv_exist(dir_citations, "citedby_authors" , authors_header)

for file in ls_xml_citedby_auth:
    file = dir_raw_xml_cited_by_refs + file
    print "The file is " + file 
    authors = parsing.parse_xml(file).get_authors()
    try:
        data_tools.append_csv(dir_citations, "citedby_authors", authors, authors_header)
    except:
        print "Either error writing to csv or csv not found"



## BEGIN TESTING
cited_by = parsing.parse_xml(file).get_soup()
cited_by = parsing.parse_xml(file).get_cited_by(eid)
data_tools.append_csv(dir_citations, "cited_by_meta", cited_by, cited_by_header)
  
entries = cited_by.find_all('entry')
cited_by.find('error')


for entry in entries:
    print entry
    entry.find('eid').contents[0]

reload(parsing)
reload(data_tools)
test_file = dir_raw_xml + ls_xml[0]
test_file = dir_raw_xml + "2-s2.0-78149372422.xml"

authors = parsing.parse_xml(test_file).get_authors()
data_tools.append_csv(dir_citations, "authors", authors, authors_header)

meta = parsing.parse_xml(test_file).get_meta()
data_tools.append_csv(dir_citations, "metadata", meta, meta_header)
    
soup = parsing.parse_xml(test_file).get_soup()

soup.find('link', {"rel":"cited-by"}).get("href")

for ref in refs:
    #print ref
    print ref.find('itemid').contents[0]

### END OF TESTING


### PDF SCRAPING

## start webbrowser use phantom_js() for non interactive work
driver = scrape.start_selenium().start_firefox()

file_pdf = dir_citations + "metadata.csv"

reload(data_tools)
keys = ["eid","doi"]
ls_pdf = data_tools.csv_to_dict(file_pdf,keys)
ls_pdf = filter(None, ls_pdf)


for pmid in ls_pdf:
    doi = pmid['doi']
    pmid = pmid['eid']
    if doi=="":
        next
    else:
    ## parse doi for pdf and parse xml for citations data
        url_doi = []
        url_doi.append("http://doi.org/" + doi)
        print url_doi
        # get pdf stuff from doi
        try:
            scrape.scrape_pdf(driver, url_doi, pmid).master_url_list()
        except:
            next
            



            
## EXTRACT TEXT FROM PDFs
import pypdfocr
import subprocess # allows calling shell scripts

ls_pdf = os.listdir(dir_pdf)
ls_pdf = [x for x in ls_pdf if not re.match('^[.][#].*|^[.].*',x)]
ls_pdf


file_pdf =  dir_pdf + ls_pdf[0]

script = "pypdfocr " + file_pdf + " -f -c config.yaml"
subprocess.call(script, shell=True)
