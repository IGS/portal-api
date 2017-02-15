import urllib2
from flask import jsonify
from py2neo import Graph # Using py2neo v3 not v2
from models import build_basic_query
import re

#print(build_query("node_type", "project", False))

#response = urllib2.urlopen('http://localhost:5000/ac_schema?query=%7Bpagination%7Bcount%7D%7D')
#r = response.read()
#r.replace('"pagination"','"no"')
#print ('%s, "warnings": {}}' % r[8:])
graph = Graph("http://localhost:7474/db/data/")

regex_for_http_urls = '\,\su(http.*)\,'

def get_urls(sample_id):
    idl, formatDocl, studyl, formatl, seqTypel, sizel, subtypel, commentl, computedFroml = ([] for i in range(9))
    cquery = "MATCH (b:Sample)<-[:PREPARED_FROM]-(p)<-[:SEQUENCED_FROM]-(s)<-[:COMPUTED_FROM]-(c) WHERE b._id=\"%s\" RETURN s, c" % (sample_id)
    res = graph.data(cquery)
    for x in range(0,len(res)):
        for key in res[0].keys(): # iterate over all node paths traversed
            print res[0][key]['subtype']

def extract_url_info(urls_node):
    regex_for_http_urls = '(http.*data/(\S+))[,\]]'
    res = []
    fn,fi = ("" for i in range(2))
    if re.match('.*http.*', urls_node):
        name_and_url = re.search(regex_for_http_urls, urls_node)
        fn = name_and_url.group(2).replace("/",".") # making the file name and some of its path pretty
        fi = name_and_url.group(1) # File ID can just be our URL
    else:
        fn = "none"
        fi = "none"
    res.append(fn)
    res.append(fi)
    return res

def get_files(sample_id):
    fl = []
    dt, fn, df, ac, fi = ("" for i in range(5))
    fs = 0
    regex_for_http_urls = '\,\su(http.*data/(.*))\,'
    
    cquery = "MATCH (b:Sample)<-[:PREPARED_FROM]-(p)<-[:SEQUENCED_FROM]-(s)<-[:COMPUTED_FROM]-(c) WHERE b._id=\"%s\" RETURN s, c" % (sample_id)
    res = graph.data(cquery)

    for x in range(0,len(res)): # iterate over each unique path
        for key in res[0].keys(): # iterate over each unique node in the path
            dt = res[0][key]['subtype']
            df = res[0][key]['format']
            ac = "open" # again, default to accommodate current GDC format
            fs = res[0][key]['size']
            data = extract_url_info(res[0][key]['urls'])
            print(data[0])


def get_proj_data(sample_id):
    cquery = "MATCH (p:Project)<-[:PART_OF]-(Study)<-[:PARTICIPATES_IN]-(SUBJECT)<-[:BY]-(VISIT)<-[:COLLECTED_DURING]-(Sample) WHERE Sample._id=\"%s\" RETURN p" % (sample_id)
    res = graph.data(cquery)
    print res[0]['p']['subtype']
    #return Project(name=res[0]['p']['name'],projectId=res[0]['p']['subtype'])

#get_files("3674d95cd0d27e1de94ddf4d2e60d16d")

def get_total_file_size():
    cquery = "MATCH (Project)<-[:PART_OF]-(Study)<-[:PARTICIPATES_IN]-(Subject)<-[:BY]-(Visit)<-[:COLLECTED_DURING]-(Sample)<-[:PREPARED_FROM]-(p)<-[:SEQUENCED_FROM]-(s)<-[:COMPUTED_FROM]-(c) RETURN (SUM(toInt(s.size))+SUM(toInt(c.size))) as tot"
    res = graph.data(cquery)
    print res[0]['tot']
    return res[0]['tot']

def get_file_data(file_id):
    cquery = "MATCH (n) WHERE n._id=\"%s\" RETURN n.node_type AS type" % (file_id)
    res = graph.data(cquery)
    node = res[0]['type']
    print node

z = ', contact:"Randall Schwager <schwager@hsph.harvard.edu>" , ns:"ihmp" , id:"6788b769d0b62444378462474d1299a3" , description:"A new three-year "multi-omic" study investigating the roles played by microbes and their interactions with the human body."'
z = re.sub(r"\s\"(.*)\"\s",r" '\1' ",z)
print z