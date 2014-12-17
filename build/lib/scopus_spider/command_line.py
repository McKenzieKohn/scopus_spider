import parsing
import dir_creation
import scrape
import sys
import argparse
from pprint import pprint as p
import get


def main(args=sys.argv):
    """
    """
    parser = argparse.ArgumentParser(description="scopus_spider")

    # dir options
    dirs = parser.add_argument_group()
    dirs.add_argument("-D", dest="input_dir", action="store",
                      help="Directory for config and outputing data",
                      default=args[0])
    dirs.add_argument("-O", dest="output_dir", action="store",
                      help="Alternative output directory")

    # query type options
    query = parser.add_mutually_exclusive_group(required=True)
    query.add_argument("-A", dest="author_search_auid", action="store",
                       help="Search for authors by Scopus au-id")
    query.add_argument("-I", dest="pub_search_pmid", action="store",
                       help="Search for publications using pubmed pmid")
    query.add_argument("-P", dest="pub_search_eid", action="store",
                       help="Search for publications using scopus eid")

    # options for query types
    options = parser.add_argument_group()
    options.add_argument("-m", dest="metadata", action="store_true",
                         help="default, metadata")
    # options.add_argument("-c", dest="coauthors", action="store_true",
    #                      help="coauthors")
    options.add_argument("-d", dest="2nd_coauthors", action="store_true",
                         help="2nd level coauthors")
    options.add_argument("-r", dest="references", action="store_true",
                         help="get references")
    # options.add_argument("-s", dest="reference_authors", action="store_true",
    #                      help="reference authors")
    options.add_argument("-a", dest="cited_by_meta", action="store_true",
                         help="get meta data for cited by")
    options.add_argument("-p", dest="pdfs", action="store_true",
                         help="get pdfs for meta data")
    options.add_argument("-o", dest="pdf_ocr", action="store_true",
                         help="ocr retrieved pdfs")
    # options.add_argument("-T", dest="all_options", action="store_true",
    #                      help="equivalent to -mcdrsapo")

    # Test
    parser.add_argument("-t", dest="test", action="store",
                        help="test")

    opts = vars(parser.parse_args())
    p(opts)

    # tests whether output folders exist and prompt user to delete or reuse
    dir_creation.create_output_dirs()
    
    # debugging purposes
    # if opts['test'] == '1':
    #    print "joke2:\n" + joke2()
    #    p(sys.path)
    #    print "joke3:\n" + jokes.joke3()

    # define api_key
    # this must be requested from scopus
    api_key = "007c9e3c95c43a49341b251534dac2ae"
        
    if opts['pub_search_pmid'] is not None:
        file_input = opts['pub_search_pmid']
        search_type = "pmid"
        
    if opts['metadata']:
        print("extracting metadata")
        output = get.get_meta(api_key, file_input, search_type)
    if opts['2nd_coauthors']:
        print(opts['auth_id_search'])
        print("extracting 2nd Level coauthors")
    if opts['references']:
        print(opts['auth_id_search'])
        print("extracting references")
    if opts['cited_by_meta']:
        print(opts['auth_id_search'])
        print("extracting cited_by")
    if opts['pdfs']:
        print(opts['auth_id_search'])
        print("extracting PDFs")
    if opts['pdf_ocr']:
        print(opts['auth_id_search'])
        print("extracting test from PDFs")

    return(output)
        
if __name__ == "__main__":
    main()
