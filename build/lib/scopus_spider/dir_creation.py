import os
import data_tools
import parsing

dir_input = "input/"   # put csv file with eid or pmid or something
dir_output = "output/"
dir_citations = "output/citations/"   # to save csv files
dir_pdf_ocr = "output/pdf_ocr/"   # to save ocr'd files
dir_pdf = "output/pdfs/"   # to save pdf files
dir_raw_xml = "output/raw_xml/"   # to save raw xml from initial search
dir_raw_xml_refs = "output/raw_xml_refs/"   # save xml to extract references
dir_raw_xml_cited_by = "output/raw_xml_cited_by/"   # save xml files
dir_raw_xml_cited_by_refs = "output/raw_xml_cited_by_refs/"
dir_raw_xml_coauthors = "output/raw_xml_coauthors/"
dir_raw_xml_coauthors_pubs = "output/raw_xml_coauthors_pubs/"

ls_dir = list([dir_output, dir_pdf, dir_raw_xml, dir_citations, dir_pdf_ocr,
               dir_raw_xml_cited_by, dir_input,
               dir_raw_xml_cited_by_refs, dir_raw_xml_refs,
               dir_raw_xml_coauthors,
               dir_raw_xml_coauthors_pubs])


def create_output_dirs():
    dir_test = os.path.exists("output/")
    if not dir_test:
        print("\nYou have no output dir, creating one now\n")
        data_tools.test_data_dirs(ls_dir)
    else:
        print("The output folder exists. ")
        delete_resp = raw_input("Do you wish to delete existing project \
        and start over?! Type Yes. Else, will try to reuse existing work")
        if delete_resp in ("y", "yes", "YES", "Yes"):
            data_tools.delete_dirs(ls_dir)
        else:
            print("\n Note: I will attempt to reuse and restart where left \
off before")



    
