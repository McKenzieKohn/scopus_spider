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
