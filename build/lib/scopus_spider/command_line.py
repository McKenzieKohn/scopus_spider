from parsing import joke2
from scopus_spider.scraping import jokes

import sys
import optparse
from pprint import pprint as p

def main(args=sys.argv[1:]):
    usage = "usage: %prog [options] arg1 arg2"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        "-t", "--test",type=int, help="testing options"
    )
    opts, args = parser.parse_args(args)

    if opts.test==0:
        print "joke2:\n" + joke2()
        #p(sys.path)
        print "joke3:\n" + jokes.joke3() 

# if __name__ == "__main__":
#     main()
