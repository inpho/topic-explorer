#!/usr/bin/python27
import json
from time import sleep
from urllib2 import urlopen
from urllib import quote_plus

def metadata(id, sleep_time=1):
    solr ="http://chinkapin.pti.indiana.edu:9994/solr/meta/select/?q=id:%s" % id
    solr += "&wt=json" ## retrieve JSON results
    # TODO: exception handling
    if sleep_time:
        sleep(sleep_time) ## JUST TO MAKE SURE WE ARE THROTTLED
    try:
        data = json.load(urlopen(solr))
        print id
        return data['response']['docs'][0]
    except ValueError :
        print "No result found for " + id 
        return dict()

def get_metadata(folder):
    ids = os.listdir(folder)
    data = [(id.strip(), metadata(id.strip())) for id in ids]
    data = dict(data)
    with open(os.path.join(folder, '../metadata.json'),'wb') as outfile:
        json.dump(data, outfile)
    

def is_valid_filepath(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parsers = parser.add_subparsers(help="select a command")
    
    parser_getmd = parsers.add_parser('get-md', 
        help="Get metadata for a folder of HathiTrust volumes")
    parser_getmd.add_argument("folder", nargs="?", 
        type=lambda x: is_valid_filepath(parser_init, x),
        help="Path to Config [optional]")
    parser_getmd.set_defaults(func='getmd')

    args = parser.parse_args()

    if args.func == 'getmd':
        get_metadata(args.folder)

if __name__ == '__main__':
    main()
