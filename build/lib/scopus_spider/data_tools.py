import csv
import os
import shutil
import itertools

def delete_dirs(ls_dir):
    for dirs in ls_dir:
        print("removing " + dirs)
        shutil.rmtree(dirs, ignore_errors=True)
        
        
def test_data_dirs(ls_dir):
    for dir in ls_dir:
        if not os.path.exists(dir):
            os.makedirs(dir)
            print "Wrote Directory: " + dir
            

def csv_to_ilist(file, field):
    csvfile = open(file, "rU")
    reader = csv.DictReader(csvfile)

    for row in reader:
        pmid = row[field]
        yield pmid

    
def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(itertools.islice(iterable, n))

def csv_to_dict(file, keys):
    csvfile = open(file, "rU")
    data = list(csv.DictReader(csvfile))
    new_data = [dict((k, d[k]) for k in keys) for d in data]

    return(new_data)

def request_to_file(text, pmid, dir):
    """ Save text to xml file using pmid
    """
    file_xml = dir + pmid + ".xml"
    f = open(file_xml, 'w')
    f.write(text.encode('utf8'))
    f.close()
    return(file_xml)

def test_csv_exist(dir, file, header):
    """ check to see if a file exists. If not, write header.
    """ 
    filename = dir + file + ".csv"
    print filename
    if os.path.isfile(filename):
        print "File exists, no need to write headers"
    else:
        print "File does not, exist, creating headers"
        outcsv = open(filename, "w+")
        writer = csv.writer(outcsv, quoting=csv.QUOTE_ALL)
        print os.getcwd()
        writer.writerow(header) 
        outcsv.close()


def append_csv(dir, file, data, header):
    filename = dir + file + ".csv"
    out = open(filename, "a") 
    # reader = csv.reader(out)
    writer = csv.DictWriter(out, fieldnames=header, quoting=csv.QUOTE_ALL)
    for row in data:
        # print row
        writer.writerow(row)
    out.close()

