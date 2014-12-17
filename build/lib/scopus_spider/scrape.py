""" 
.. module:: scrape
    :synopsis: tools to scrape journals

"""

from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
import os 
import requests
import re 
import data_tools
import itertools
import dir_creation
from progressbar import ProgressBar
import parsing

def make_urls(ids, search_type):
    if search_type == "pmid":
        for id in ids:
            url = "http://api.elsevier.com/content/search/index:SCOPUS?query=" + search_type + "(" + id + ")&field=doi,eid"
            yield url

            
def get_xml(api_key, urls):    
    headers = {'X-ELS-APIKey': api_key}
    urls = list(urls)
    print len(urls)
    with ProgressBar(maxval=len(urls), redirect_stdout=True) as p:
        for i, url in enumerate(urls):
            print url
            web = requests.get(url, headers=headers)
            try:
                scopus_eid = web.json()['search-results']['entry'][0]['eid']
            except:
                print("no eid in scopus database!\n")
                print url
                next
            try:
                scopus_abstract = web.json()['search-results']['entry'][0]['prism:url']
                web_scopus = requests.get(scopus_abstract, headers=headers)
            except:
                print("no scopus abstract for pmid!\n")
                print url
                next
            xml_text = web_scopus.text
            output = {"scopus_eid":scopus_eid, 'scopus_abstract': scopus_abstract, 'xml_text':xml_text}
            yield output
            p.update(i)

            
def save_xml(xml_text, search_type, search_option):
    if search_option == "meta":
        for xml_file in xml_text:
            # print xml_file["xml_text"].encode('utf8')
            xml_out = data_tools.request_to_file(xml_file["xml_text"], xml_file["scopus_eid"], dir_creation.dir_raw_xml)
            print xml_out
            yield xml_out

            
def get_data(xml_files, search_option):
    for file in xml_files:
        parser = parsing.parse_xml(file)
        data = {}
        if search_option == "meta":
            data["meta_articles"] = parser.get_meta()
            data["meta_references"] = parser.get_references()
            data["meta_authors"] = parser.get_authors()
            yield data

def save_data(data, search_option):
    
    if search_option == "meta":
        # define headers
        meta_articles_header = ["eid", "pubmed-id", "doi",
                                "source_type", "pub_name", "issn",
                                "title", "abstract", "cited_by_url"]
        meta_authors_header = ["eid", "pubmed_id", "author_id",
                               "author_seq", "author_name",
                               "author_surname", "author_given",
                               "author_aff_id"]
        meta_references_header = ["eid", "pubmed_id", "ref_id", "ref_title",
                                  "ref_authors_cnt"]
        # test that files exists else create them
        data_tools.test_csv_exist(dir_creation.dir_citations,
                                  "meta_articles",
                                  meta_articles_header)
        data_tools.test_csv_exist(dir_creation.dir_citations,
                                  "meta_authors",
                                  meta_authors_header)
        data_tools.test_csv_exist(dir_creation.dir_citations,
                                  "meta_references",
                                  meta_references_header)
        for datum in data:
            # print("datum: ", datum)
            data_tools.append_csv(dir_creation.dir_citations,
                                  "meta_articles",
                                  datum["meta_articles"], meta_articles_header)
            data_tools.append_csv(dir_creation.dir_citations,
                                  "meta_references",
                                  datum["meta_references"],
                                  meta_references_header)
            data_tools.append_csv(dir_creation.dir_citations,
                                  "meta_authors",
                                  datum["meta_authors"], meta_authors_header)
            
        
def get_scopus_url(api_key,url):
    headers = {'X-ELS-APIKey':api_key,"Accept":"application/xml"}
    print url
    web = requests.get(url, headers=headers)
    return(web)


def get_pmid_xml(api_key,idtype,searchid):
    """ Gets xml for a PMID
    Note: This needs to be updated to be able to accept titles since
    scopus has some titles that are not linked to PMIDs. 
    Note: You can have a URL abstract with no DOI. 
    Args:
    api_key (str): Contains scopus api key
    pmid (str): The ID of pubmed ids

    """
    headers = {'X-ELS-APIKey':api_key}
    url = "http://api.elsevier.com/content/search/index:SCOPUS?query=" + idtype + "(" + searchid + ")&field=doi"
        #url = 'http://api.elsevier.com/content/abstract/scopus_id:' + str(pmid)
    print url
    web = requests.get(url, headers=headers)
    try:
        doi = web.json()['search-results']['entry'][0]['prism:doi']
    except: 
        print web.json()
        doi = False
    
    try: 
        scopus_abstract = web.json()['search-results']['entry'][0]['prism:url']
        web_scopus = requests.get(scopus_abstract, headers=headers)
        xml_text =  web_scopus.text
    except: 
        scopus_abstract = False
        xml_text = False

    output = {'doi':doi, 'scopus_abstract':scopus_abstract, 'xml_text':xml_text}
    return(output) 

class start_selenium:
    """This starts selenium and gives options for different kinds of browser. 
    .. note:: 
    Firefox is useful for interactive debugging, but for large scale scraping better 
    to use phantomjsx
    """
    def __init__(self):
        self
        self.download_dir = os.getcwd() + "/output/pdfs"
        print "The download dir is:" + self.download_dir

    def start_firefox(self):
        """ This start firefox instance
        """
        fp = webdriver.firefox.firefox_profile.FirefoxProfile("/Users/robertvesco/Library/Application Support/Firefox/Profiles/j2rjfnw0.default")
        # fp.set_preference("browser.download.folderList",2)
        # fp.set_preference("browser.download.manager.showWhenStarting",False)
        # fp.set_preference("browser.download.dir",self.download_dir)
        # fp.set_preference("browser.helperApps.neverAsk.saveToDisk","application/pdf")
        fp.set_preference("pdfjs.disabled",True)
        #fp.add_extension()
        driver = webdriver.Firefox(firefox_profile=fp)
        return(driver)

    def start_phantomjs(self):
        """ Starts phantomjs browser. Useful for automation.
        """
        driver = webdriver.PhantomJS()
        return(driver)


class scrape_pdf:
    """ This is a class of functions that extract pdfs from scopus 
    """
    def __init__(self, driver, ls_urls, pmid):
        self.driver = driver
        self.ls_urls = ls_urls
        self.pmid = pmid

    def master_url_list(self):
        for url in self.ls_urls:
            print url
            is_good = self.get_check_url(url)
            if not is_good:
                next
            self.driver.get(url)
            # get pdf links on page
            ls_href = self.get_pdf_links(self.driver)
            # Get_test_pdf should NOT be returning a list!
            try:
                found_pdf = self.get_test_pdf(ls_href)
                # print "found_pdf is "
                # print '[%s]' % ', '.join(map(str,found_pdf))
                if not found_pdf:
                    for url2 in ls_href:
                        print "trying alternative url: " + url2
                        self.driver.get(url2)
                        ls_href2 = self.get_pdf_links(self.driver)
                        found_pdf2 = self.get_test_pdf(ls_href2)
                        if found_pdf2:
                            break
            except:
                print "no PDF url or problem - investigate!"
            next
    
    def get_check_url(self,url):
        """ Check to make sure returns valid status
        """
        r = requests.get(url).status_code
        if r==requests.codes.ok:
            return(True)
        else:
            print "something wrong! status_code: " + r
            return(False)

    def get_pdf_links(self, driver):
        """ Checks for links with PDF in title or in link. 

        First, it checks for PDF in links. If it doesn't find it, it
        then searches a frame. If it doesn't find it then, it search
        for an Iframe. It's brittle
        
        :param driver: selenium object
        :returns: list of urls with pdfs
        """
        ls_urls = driver.find_elements_by_xpath("//a[contains(translate(text(),'PDF','pdf'),'pdf')]")
        len_urls = len(ls_urls)
        print "We have " + str(len_urls) + " urls with PDF in title"
        if len_urls != 0:
            ls_href = [url.get_attribute('href') for url in ls_urls]
        elif len_urls == 0: 
            ls_urls = driver.find_elements_by_xpath("//a[contains(@href,'pdf')]")
            len_urls = len(ls_urls)
            print "We have " + str(len_urls) + " urls with pdf in the link"
            ls_href = [url.get_attribute('href') for url in ls_urls]

        len_href = len(ls_href)

        if len_href == 0: 
            #check for frameset
            ls_urls = driver.find_elements_by_xpath("//frame[contains(@src,'pdf')]")
            len_urls = len(ls_urls)
            print "We have " + str(len_urls) + " urls in a frame "
            ls_href = [url.get_attribute('src') for url in ls_urls]
            #print "print one frame link: " + ls_href[0]

        len_href = len(ls_href)

        if len_href == 0:
            #check for iframe
            ls_urls = driver.find_elements_by_xpath("//iframe[contains(@src,'pdf')]")
            len_urls = len(ls_urls)
            print "We have " + str(len_urls) + " in an Iframe"
            ls_href = [url.get_attribute('src') for url in ls_urls]
            #print "print one Iframe link: " + ls_href[0]
            len_href = len(ls_href)

        if len_href == 0:
            return(False)
        else:
            return(ls_href)
    
    def get_test_pdf(self,ls_href):
        """
        Tests each link for pdf. If not PDF, selects. To reduce requests
        It first checks for links ending in .pdf

        :params: ls_href: list of hrefs
        :returns: a single url to test content_type or a list if no
        """
        # test for length 
        for url in ls_href:
            is_pdf = self.test_content_type(url)
            if is_pdf:
                filename = self.download_pdf_url(url)
                print "downloaded file: " + filename
                break 
            else: 
                print url + " is not a pdf and was not downloaded"
                filename = False
                next
        #if filename is False:
        #    filename = ls_href
        #    print "returning filelist of since no identified pdfs"
        return(filename)

    def test_content_type(self,url):
        """if no obvious pdf link, then need to test content_type    
        """
        
        p = re.compile('.*pdf*.')
        cookies = self.get_cookies()
        print "cookies are:\n " + str(cookies)
        content_type = requests.get(url, allow_redirects=True, cookies=cookies).headers.get('content-type')
        is_pdf = p.match(content_type)
        print "content type is pdf: " + str(is_pdf)
        if is_pdf:
            return(True)
        else:
            return(False)
    
    def get_cookies(self):
        all_cookies = self.driver.get_cookies()
        cookies = {}
        for s_cookie in all_cookies:
            cookies[s_cookie["name"]]=s_cookie["value"]
        return(cookies)
    
    def download_pdf_url(self,url):
        filename = "./output/pdfs/" + self.pmid+".pdf"
        cookies = self.get_cookies()
        r = requests.get(url,stream=True, cookies=cookies, allow_redirects=True)
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
        if r.status_code == requests.codes.ok:
            return(filename)
        else: 
            return(False)

    if __name__ == "__main__":
        master_url_list()
