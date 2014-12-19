import os
import data_tools
import scrape
import dir_creation
import parsing


def get_meta(api_key, file_input, search_type):
    # get ids (eid or pmid or auth-id) and search type
    # return iterator of ids
    ids = data_tools.csv_to_ilist(file_input, search_type)

    # get urls need for scopus qu w
    urls = scrape.make_urls(ids, search_type)

    # download data from scopus and get text
    xml_text = scrape.get_xml(api_key, urls)

    # save text to file (useful for caching, though not implemented)
    xml_files = scrape.save_xml(xml_text, search_type, "meta")

    # Now parse xml
    data = scrape.get_data(xml_files, "meta")
    
    # # save data to csv or db?
    scrape.save_data(data, "meta")
    
    # print type(xml_text)
    # print data_tools.take(1, xml_file)
    # print(list(xml_text))
    # print(dir_creation.dir_raw_xml)
    
    return(ids)


def get_coauthors_2ndlevel(api_key, file_input, search_type, search_option):
    # check to see that we have first level coauthors
    # For single author? Or for all authors?
    file_auid = "output/citations/meta_authors.csv"
    if not os.path.isfile(file_auid):
        get_meta(api_key, file_input, search_type)  

    # extract author ids
    ids = data_tools.csv_to_ilist(file_auid, "author_id")

    # get unique ids so that we don't get duplicates
    ids = list(set(ids))[0:5]

    # for each id, construct urls to author pubs
    urls = scrape.make_urls(ids, "auid")
 
    # get text from scopus
    xml_text = scrape.get_xml(api_key, urls, "auid")

    # save author xml files to dir_raw_xml_coauthors
    xml_files = scrape.save_xml(xml_text,
                                search_type,
                                search_option)

    # get auids
    data = scrape.get_data(xml_files, "auid")

    # # save data to csv or db?
    # scrape.save_data(data, "meta")
    
    # debugging
    # print list(ids)[0:10]
    # print list(urls)[1:10]
    # print list(xml_text)[0:1]
    # print list(xml_files)
    print list(data)[0:5]
    
# def get_reference_authors():
#     # this will need reference eid from get_meta()

# def get_cited_by():
#     # this will need pmid

# def get_cited_by_authors():
#     #

# def get_pdfs:
#     # this will need meta data eids

# def ocr_pds:
#     # this will need pdfs

    


