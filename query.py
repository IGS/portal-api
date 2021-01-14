import re, json, requests, hashlib, time, ast, shlex
import ujson, urllib
from collections import OrderedDict
from py2neo import Graph # Using py2neo v3 not v2
from conf import neo4j_ip, neo4j_bolt, neo4j_http, neo4j_un, neo4j_pw

from config_utils import load_config
from flask import current_app

#import metadata mapping
from metadata_mapping import metadata_mapping as METADATA_MAPPING



regexForNotEqual = re.compile(r"<>\s([0-9]*[a-zA-Z_]+[\-a-zA-Z0-9_]*)\b") # only want to add quotes to anything that's not solely numbers
regexForEqual = re.compile(r"=\s([0-9]*[a-zA-Z_]+[\-a-zA-Z0-9_]*)\b")
regexForIn = re.compile(r"(\[[\-_a-zA-Z\'\"\s\,\(\)]+\])") # catch anything that should be in a list

METADATA_FIELDS = list(METADATA_MAPPING.keys())
METADATA_CY_FIELDS = list( METADATA_MAPPING[facet]['cypher_field'] for facet in METADATA_MAPPING.keys())
POTENTIALLY_MALICIOUS_STRINGS = {";"," delete "," create "," detach "," set ",
                                    " merge ", " call ", " import ", " remove ",
                                    " union ", " drop ", " foreach ", " using ", " unwind "}

config = load_config(file_name='config.json')

SUBJECT_EXCLUDE_LIST = config['site-wide']['subject-excluded-fields']
SAMPLE_EXCLUDE_LIST = config['site-wide']['sample-excluded-fields']
FILE_EXCLUDE_LIST = config['site-wide']['file-excluded-fields']

# The match var is the base query to prepend all queries. The idea is to traverse
# the graph entirely and use filters to return a subset of the total traversal.
# PS = Project/Subject
# VSS = Visit/Sample/Study
# F = File
# T = Tag
# D = derived from (contains prep data)

# TODO: mschor: Remove this constant in favor of caps constant once older lower cased version no longer used 
full_traversal = "MATCH (PS:subject)<-[:extracted_from]-(VSS:sample)<-[D:derived_from]-(F:file) "
FULL_TRAVERSAL = "MATCH (subject:subject)<-[:extracted_from]-(sample:sample)<-[D:derived_from]-(file:file) "
SAMPLE_TRAVERSAL = "MATCH (subject:subject)<-[:extracted_from]-(sample:sample) "

tag_traversal = "MATCH (PS:subject)<-[:extracted_from]-(VSS:sample)<-[D:derived_from]-(F:file)-[:has_tag]->(T:tag) "

###############
# NEO4J SETUP #
###############

# Get all these values from the conf
neo4j_bolt = int(neo4j_bolt)
neo4j_http = int(neo4j_http)
cypher_conn = Graph(host=neo4j_ip,bolt_port=neo4j_bolt,http_port=neo4j_http,user=neo4j_un,password=neo4j_pw)

# Sample hits returns sample data for faceted search, advanced search, or default (all samples)
def get_sample_hits(size, order, f, cy, facets=None):

    row_id_node_type = config['search']['cases-table']['api-row-id-node-type']
    row_id_field = config['search']['cases-table']['api-row-id-field']
    recalc_facets = config['search']['recalculate-facets'] if 'recalculate-facets' in config['search'] else True
    
    # Letting it fail if non numeric inputs
    size = int(size)
    f = int(f)
    
    hits = []
    cquery = ""
    
    RETVAL = "RETURN DISTINCT subject,sample " 
    where = None

    # Needed because from=1 means start from result 1 (as far as the api url is concerned), but neo4j skip should == 0    
    if f != 0:
        f = f-1
    
    param_map = {}
    cypher_order = _convert_order(order)
    aggs = None
    
    if cy == "":
        order_by = " " + cypher_order + " SKIP {skip} LIMIT {size}"
        cquery = SAMPLE_TRAVERSAL + " " + RETVAL + order_by
        count_query = "MATCH (sample:sample) RETURN COUNT (sample) as tot"
    elif '"op"' in cy:
        (where, param_map) = _build_where(cy)
        order_by = " " + cypher_order + " SKIP {skip} LIMIT {size}"
        cquery = FULL_TRAVERSAL + " " + where + " " + RETVAL + order_by
        count_query = FULL_TRAVERSAL + where + " RETURN COUNT(DISTINCT(sample)) as tot"
        if recalc_facets:
            aggs = _build_facet_counts_where(facets, where, param_map)
    else:
        # This is used by the advanced query (typing your own query)
        (cquery, param_map) = _build_adv_cypher(cy,cypher_order,f,size,"samples")
        cquery_limited = cquery + " SKIP {skip} LIMIT {size}"
        count_query = cquery[0:cquery.index(" RETURN ")] + " RETURN COUNT(DISTINCT(sample)) as tot"
        cquery = cquery_limited
    
    param_map["skip"] = f
    param_map["size"] = size
    res = execute_safe_query(cquery, **param_map)
    
    count = 0
    for record in res:
        hit = {}
        for key in record.keys():
            hit[key] = dict(record[key])
            # filter facets in db, but not in metadata yaml
            if key == "sample":
                hit[key] = { key:value for (key, value) in hit[str(key)].items() if key not in SAMPLE_EXCLUDE_LIST}
            elif key == "subject":
                hit[key] = { key:value for (key, value) in hit[str(key)].items() if key not in SUBJECT_EXCLUDE_LIST}
            else:
                hit[key] = { key:value for (key, value) in hit[str(key)].items() if key not in FILE_EXCLUDE_LIST}

            if str(key) == row_id_node_type:
                hit["id"] = hit[str(key)][row_id_field]
                
        hits.append(hit)
        count += 1
    
    try:
        res.close()
    except:
        pass
    
    data = {"hits": hits}
    data["pagination"] = {"count" : count}
    if aggs:
        data["aggregations"] = aggs
   
    sample_count_cursor = execute_safe_query(count_query, **param_map)
    try:
        total = sample_count_cursor.evaluate("tot")
        sample_count_cursor.close()
    except:
        total = 0

    # if no "from" provided as param
    if total > 0 and f == 0:
        f = 1
    else:
        # restore from to non-cypher, user-friendly number
        f += 1
    
    pages = _calc_pages(total, size)
    page = _calc_pages(f, size)

    # count = how many results back on the current page (could be less than what the user selected if this is the last page)
    # total = total results in database based on selelcted facets
    # page = current page number
    # pages = total number of pages
    # from = starting result number for page -- came in from client
    # sort = sort string -- came in from client
    # size = what the user selected to see per page
        
    pagination = {
          "count": count, 
          "total": total, 
          "page": page,
          "pages": pages, 
          "from": f, 
          "sort": order, 
          "size": size
        } 
    
    data["pagination"] = pagination
    
    return {"data": data}

    
# Function to return file values to populate the table.
def get_file_hits(size,order,f,cy,facets=None):

    # Letting it fail if non numeric inputs
    size = int(size)
    f = int(f)
    
    hits = []
    cquery = ""

    RETVAL = "RETURN DISTINCT file " 
    where = None
    
    # Needed because from=1 means start from result 1 (as far as the api url is concerned), but neo4j skip should == 0    
    if f != 0:
        f = f-1
    
    param_map = {}
    cypher_order = _convert_order(order)
    aggs = None
    recalc_facets = config['search']['recalculate-facets'] if 'recalculate-facets' in config['search'] else True

    # The following if/elif/else block has 3 parts which are true when:
    # A default query is triggered by the front-end (paging through samples, files)
    # A facet-query is triggered
    # An advanced search query is triggered
    if cy == "":
        order_by = " " + ("" if cypher_order is None else cypher_order) + " SKIP {skip} LIMIT {size}"
        cquery = FULL_TRAVERSAL + " " + RETVAL + order_by
        res = execute_safe_query(cquery, skip=f, size=size)
        count_query = FULL_TRAVERSAL + " RETURN COUNT (file) as tot, COUNT(sample) as sample_tot"
    elif '"op"' in cy:
        (where, param_map) = _build_where(cy)
        order_by = " " + cypher_order + " SKIP {skip} LIMIT {size}"
        cquery = FULL_TRAVERSAL + " " + where + " " + RETVAL + order_by
        param_map["skip"] = f
        param_map["size"] = size
        res = execute_safe_query(cquery, **param_map)
        count_query = FULL_TRAVERSAL + where + " RETURN COUNT(DISTINCT(file)) as tot, COUNT(DISTINCT(sample)) as sample_tot"
        if recalc_facets:
            aggs = _build_facet_counts_where(facets, where, param_map)

    else:
        (cquery, param_map) = _build_adv_cypher(cy,cypher_order,f,size,"files")
        cquery_limited = cquery + " SKIP {skip} LIMIT {size}"
        param_map["skip"] = f
        param_map["size"] = size
        res = execute_safe_query(cquery_limited, **param_map)
        count_query = cquery[0:cquery.index(" RETURN ")] + " RETURN COUNT(DISTINCT(file)) as tot, COUNT(DISTINCT(sample)) as sample_tot"

    sample_count_cursor = execute_safe_query(count_query, **param_map)
    total = 0
    sample_total = 0
    
    for record in sample_count_cursor:
        d_record = dict(record)
        total = record["tot"]
        sample_total = record["sample_tot"]    
    
    try:
        sample_count_cursor.close()
    except:
        pass
    
    row_id_node_type = config['search']['files-table']['api-row-id-node-type']
    row_id_field = config['search']['files-table']['api-row-id-field']
    rename_filename = config['search']['files-table']['rename-filename-absolute-path']
    
    count = 0
    for record in res:
        d_record = dict(record)
        hit = {}
        
        # For file traversals, there's only one node type, 'file', but sticking with allowance for multiple
        for nodetype in record.keys():
            hit[nodetype] = dict(record[nodetype])

            file_url = extract_url(hit[nodetype])
            # filter facets in db, but not in metadata yaml
            #hit[nodetype] = { key:value for (key, value) in hit[nodetype].items() if key in METADATA_FIELDS}
            hit[nodetype] = { key:value for (key, value) in hit[nodetype].items() if key not in FILE_EXCLUDE_LIST}
            if str(nodetype) == row_id_node_type:
                hit["file_id"] = hit[str(nodetype)][row_id_field]

            if rename_filename in [True, "true"]:
                # Changes file_name to the absolute file path url (NeMO uses only filename, no path)
                hit[nodetype]["file_name"] = file_url
            
            #TODO: mschor: This is HMP specific and has been hardcoded since the beginning.
            #Check if data is private 
            if 'private' in file_url.lower():
                hit['access'] = 'controlled'
            else:
                hit['access'] = 'open'
        
        hits.append(hit)
        count += 1
        
    try:
        res.close()
    except:
        pass
        
    data = {"hits": hits}
    if aggs:
        data["aggregations"] = aggs
    
    # if no "from" provided as param
    if total > 0 and f == 0:
        f = 1
    else:
        # restore from to non-cypher, user-friendly number
        f += 1
    
    pages = _calc_pages(total, size)
    page = _calc_pages(f, size)

    # count = how many results back on the current page (could be less than what the user selected if this is the last page)
    # total = total results in database based on selelcted facets
    # page = current page number
    # pages = total number of pages
    # from = starting result number for page -- came in from client
    # sort = sort string -- came in from client
    # size = what the user selected to see per page
            
    pagination = {
          "count": count, 
          "total": total, 
          "page": page, 
          "pages": pages, 
          "from": f, 
          "sort": order, 
          "size": size,
          "sample_total": sample_total
        } 
    
    data["pagination"] = pagination
    
    return {"data": data}


# Retrieve all files associated with a given Sample ID.
def get_files(sample_id):
    
    row_id_node_type = config['search']['files-table']['api-row-id-node-type']
    row_id_field = config['search']['files-table']['api-row-id-field']
    sample_id_property = config['search']['sample-node-id']

    sample_file_traversal = "MATCH (sample:sample)<-[D:derived_from]-(file:file) "
    cquery = sample_file_traversal + " WHERE " + sample_id_property + "={id} RETURN file"
    res = execute_safe_query(cquery, id=sample_id)
    
    hits = []   
    count = 0
    for record in res:
        d_record = dict(record)
        hit = {}
        for nodetype in d_record:
            # Assign the dictionary as a value in this hit with the key being the node type
            hit[nodetype] = d_record[nodetype]
            if nodetype == row_id_node_type:
                # The front-end will need a non-nested ID field to uniquely be able to iterate over the results
                hit["id"] = hit[nodetype][row_id_field]
                hit["file_id"] = hit[nodetype][row_id_field]
        hits.append(hit)
        count += 1

    try:
        res.close()
    except:
        pass
    
    data = {"files": hits, "case_id": sample_id }
    
    return data


def get_subject_sample(sample_id):
    sample_id_property = config['search']['sample-node-id']
    cquery = "MATCH (subject:subject)<-[:extracted_from]-(sample:sample) WHERE " + sample_id_property + "= {id} RETURN subject, sample"
    res = execute_safe_query(cquery, id=sample_id)

    hit = {}
    # There should only be one result here. Sample IDs should be unique. If more than one is returned, it's a data error.
    count = 0    
    for record in res:
        count += 1
        if count > 1:
            #TODO: mschor: add logging module. We should log an error here
            print("Found multiple samples with the same ID: " + sample_id + ". This is a data error!")
            break
        d_record = dict(record)
        
        for nodetype in d_record:
            # Assign the dictionary as a value in this hit with the key being the node type
            hit[nodetype] = d_record[nodetype]
            # filter facets in db, but not in metadata yaml
            #hit[nodetype] = { key:value for (key, value) in hit[str(nodetype)].items() if key in METADATA_FIELDS}
            if nodetype == "subject":
                hit[nodetype] = { key:value for (key, value) in hit[nodetype].items() if key not in SUBJECT_EXCLUDE_LIST}
            else:
                hit[nodetype] = { key:value for (key, value) in hit[nodetype].items() if key not in SAMPLE_EXCLUDE_LIST}
    try:
        res.close()
    except:
        pass
    
    return hit


# Pull all the data associated with a particular file ID.
def get_file_data(file_id):
    rename_filename = config['search']['files-table']['rename-filename-absolute-path']
    data = {}
    
    query = "MATCH (subject:subject)<-[:extracted_from]-(sample:sample)<-[D:derived_from]-(file:file) WHERE file.id = {id} RETURN subject, sample, file"
    res = execute_safe_query(query, id=file_id)
    
    #Extract node properties from record
    for record in res:
        data.update({
            'subject': dict(record)['subject'],
            'sample': dict(record)['sample']
        })
        current_file = dict(record)['file']
        
        # filter facets in db, but not in metadata yaml
        data['subject'] = { key:value for (key, value) in data['subject'].items() if key not in SUBJECT_EXCLUDE_LIST}
        data['sample'] = { key:value for (key, value) in data['sample'].items() if key not in SAMPLE_EXCLUDE_LIST}
        
        file_url = extract_url(current_file)
        
        current_file = { key:value for (key, value) in current_file.items() if key not in FILE_EXCLUDE_LIST}

        #Manually add file_id and file_name
        current_file['file_id'] = current_file['id']
        if rename_filename in [True, "true"]:
            # Changes file_name to the absolute file path url (NeMO uses only filename, no path)
            current_file['file_name'] = file_url

    
        #TODO: mschor: This is HMP specific and has been hardcoded since the beginning.
        #Check if data is private 
        if 'private' in file_url.lower():
            current_file['access'] = 'controlled'
        else:
            current_file['access'] = 'open'

    try:
        res.close()
    except:
        pass
    
    data.update({'file': current_file})
    return {'data' : data }


def get_returns():
    returns = {
        'samples': "RETURN DISTINCT subject, sample",
        'files': "RETURN DISTINCT file"
    }
    
    if config:
        count_queries = config['search']['piechart-api']['count-queries']
        for k, v in count_queries.iteritems():
            k = k.replace('-', '_') #config is hypen-separated, but need underscore_separated at this point
            returns[k] = v

    return returns

def cache_facet_counts():
    
    count_dict = {}
    print("Building facet counts...")
    for label in _get_node_labels():
        for prop in _get_all_property_keys_for_node_type(label):
            count_dict.update(_build_facet_counts([label + "." + prop]))

    current_app.cache.set("facet_counts", count_dict)
    print("Done")

# Function to determine what component file property names to look for
# based on the file type, obtained from the URL.
def determine_component_files(urls, urls_node):
    url = ','.split(urls)[0]
    if urls_node['format'] == 'FASTQ':
        r1_fastq = urls_node["r1_fastq"] if 'r1_fastq' in urls_node else "NA"
        r2_fastq = urls_node["r2_fastq"] if 'r2_fastq' in urls_node else "NA"
        i1_fastq = urls_node["i1_fastq"] if 'i1_fastq' in urls_node else "NA"
        i2_fastq = urls_node["i2_fastq"] if 'i2_fastq' in urls_node else "NA"
        barcodes_fastq = urls_node["barcodes_fastq"] if 'barcodes_fastq' in urls_node else "NA"
        component_files = "{};{};{};{};{}".format(r1_fastq, r2_fastq, i1_fastq, i2_fastq, barcodes_fastq)
    elif urls_node['format'] == 'BAM':
        bam = urls_node["bam"] if 'bam' in urls_node else "NA"
        bai = urls_node["bai"] if 'bai' in urls_node else "NA"
        component_files = "{};{};".format(bam, bai)
    elif urls_node['format'] == 'MEX':
        mtx = urls_node["mtx"] if 'mtx' in urls_node else "NA"
        barcodes_tsv = urls_node["barcodes_tsv"] if 'barcodes_tsv' in urls_node else "NA"
        genes_tsv = urls_node["genes_tsv"] if 'genes_tsv' in urls_node else "NA"
        component_files = "{};{};{}".format(mtx, barcodes_tsv, genes_tsv)
    elif urls_node['format'] == 'TSV':
        tsv = urls_node["tsv"] if 'tsv' in urls_node else "NA"
        tsv_index = urls_node["tsv_index"] if 'tsv_index' in urls_node else "NA"
        component_files = "{};{};".format(tsv, tsv_index)
    elif urls_node['format'] == 'FPKM':
        isoforms_fpkm = urls_node["isoforms_fpkm"] if 'isoforms_fpkm' in urls_node else "NA"
        genes_fpkm = urls_node["genes_fpkm"] if 'genes_fpkm' in urls_node else "NA"
        component_files = "{};{}".format(isoforms_fpkm, genes_fpkm)
    elif urls_node['format'] == 'TABcounts':
        col_counts = urls_node["col_counts"] if 'col_counts' in urls_node else "NA"
        row_counts = urls_node["row_counts"] if 'row_counts' in urls_node else "NA"
        mtx_counts = urls_node["mtx_counts"] if 'mtx_counts' in urls_node else "NA"
        exp_json = urls_node["exp_json"] if 'exp_json' in urls_node else "NA"
        component_files = "{};{};{};{}".format(col_counts, row_counts, mtx_counts, exp_json)
    elif urls_node['format'] == 'TABanalysis':
        col_analysis = urls_node["col_analysis"] if 'col_analysis' in urls_node else "NA"
        row_analysis = urls_node["row_analysis"] if 'row_analysis' in urls_node else "NA"
        dimred = urls_node["dimred"] if 'dimred' in urls_node else "NA"
        component_files = "{};{};{}".format(col_analysis, row_analysis, dimred)
    else:
        component_files = "NA"
    return component_files

# Function to extract a file name and an HTTP URL given values from a urls
# property from an OSDF node. Note that this prioritizes http>ftp>s3
# and that it only returns a single one of the endpoints. This is in an effort
# to communicate a base URL in the result tables in the portal.
def extract_url(urls_node):
    private_filename = config['search']['files-table']['private-data-filename']
    fn = private_filename if private_filename else "Private data"

    if 'http' in urls_node:
        fn = urls_node['http']
    elif 'https' in urls_node:
        fn = urls_node['https']
    elif 'ftp' in urls_node:
        fn = urls_node['ftp']
    elif 's3' in urls_node:
        fn = urls_node['s3']
    elif 'gs' in urls_node:
        fn = urls_node['gs']
    elif 'file' in urls_node:   # SAdkins test
        fn = urls_node['file']
    elif 'private_url' in urls_node:
        fn += ": {}".format(urls_node['private_url'])

    return fn

# Function to return all present URLs for the manifest file
def extract_manifest_urls(urls_node):

    urls = []

    # Note that these are all individual ifs in order to grab all endpoints present
    if 'http' in urls_node:
        urls.append(urls_node['http'])
    if 'https' in urls_node:
        urls.append(urls_node['https'])
    if 'ftp' in urls_node:
        urls.append(urls_node['ftp'])
    if 's3' in urls_node:
        urls.append(urls_node['s3'])
    if 'gs' in urls_node:
        urls.append(urls_node['gs'])
    if 'file' in urls_node:   # SAdkins test
        urls.append(urls_node['file'])

    if len(urls) == 0: # if here, there is no downloadable file
        urls.append('Private: Data not accessible via the HMP DACC.')

    return ",".join(urls)

#DOlley removed because appears to not be used. Remaining as precaution
# def get_all_proj_data():
#     cquery = "MATCH (VSS:subject) RETURN DISTINCT VSS.study_name, VSS.study_description"
#     return _process_cquery_http(cquery)
 
def get_all_study_data(size=None, order=None, f=None):
    cquery = config['projects']['study-data-query']
    param_map = {}

    if order is not None:
        if ":asc" in order.lower():
            order = order.lower().replace(":asc", "")
        if ":desc" in order.lower():
            order = order.lower().replace(":desc", " DESC")
        if order.endswith(","):
            order = order[:-1]
        
        cypher_order = " ORDER BY " + order

        cquery = cquery + cypher_order
    if f is not None:
        f = int(f)
        if f != 0:
            f = f-1
        param_map['skip'] = f
    if size is not None:
        size = int(size)
        param_map['size'] = size

    res = execute_safe_query(cquery, **param_map)
    results = []
    for record in res:
        results.append(dict(record))
    
    return results

def get_study_sample_counts():
    cquery = config['projects']['study-sample-count-query']
    return _process_cquery_http(cquery)

def get_front_page_bar_chart_data():
    return_stmt = config['search']['barchart-config']['count-query']
    cquery = ("{0} " + return_stmt).format(full_traversal)
    return _process_cquery_http(cquery)

def get_front_page_example_query_data(): 
    data = []

    for example_query in config['home']['example-queries']:
        results = execute_safe_query(example_query['count-query'])
        
        for record in results:
            data.append({
                'case_count': record['case_count'],
                'file_count': record['file_count'],
                'description': example_query['description'],
                'has-cases-link': example_query['has-cases-link'],
                'has-files-link': example_query['has-files-link'],
                'cases-link': example_query['cases-link'],
                'files-link': example_query['files-link']
            })
        
        try:
            results.close()
        except:
            pass
        
    return data

# Function to return all relevant values for the pie charts. Takes in WHERE from UI
def get_pie_chart_summary(cy):

    cquery = ""
    charts = []
    file_size = 0

    cache_results = False
    return_from_cache = False

    # Get chart names/order from config
    chart_order = config['search']['piechart-api']['chart-order']
    count_queries = config['search']['piechart-api']['count-queries']
    
    counter = 0
    for chart in chart_order:
        chart_query_key = chart.replace("_","-")
        
        param_map = {}
        
        if cy:
            if '"op"' in cy:
                #TODO: mschor: why is cases. being passed in here from the UI?
                cy = cy.replace("cases.","")
                cy = cy.replace("files.","")
                (where, param_map) = _build_where(cy)
                chart_query_return = count_queries[chart_query_key + "-detailed"]
                cquery = FULL_TRAVERSAL + " " + where + " " + chart_query_return
            else:
                # advanced pie chart search
                chart_query_return = count_queries[chart_query_key + "-detailed"]
                #cquery = FULL_TRAVERSAL + " " + chart_query_return 
                (cquery, param_map) = _build_adv_cypher(cy,"null","null","null","samples")
                cquery = cquery[0:cquery.index(" RETURN ")] + chart_query_return
        else:
            # Getting default piecharts
            # If cache is found, use them
            #cache_key = "default_piechart_counts"
            #if current_app.cache.get(cache_key) is not None:
            #    return_from_cache = True
            #    break
            #else:
            #    #Cache default piecharts
            #    cache_results = True
            
            chart_query_return = count_queries[chart_query_key + "-detailed"]
            cquery = FULL_TRAVERSAL + " " + chart_query_return
        
        res = execute_safe_query(cquery, **param_map)

        buckets = []
        for record in res:
            if counter == 0:
                file_size += record['tot'] # calculate this here as projects most likely to return lowest amount of rows
            
            bucket = { "case_count" : record['scount'],
                       "doc_count" : record['fcount'],
                       "file_size" : record["tot"],
                       "key" : record["prop"] }
            buckets.append(bucket)
        
        charts.append({ "buckets" : buckets, "id": counter, "name": "chart" + str(counter) })
             
        try:
            res.close()
        except:
            pass
    
        counter += 1

        tot_dict = { "fs" : { "value": file_size }, "charts" : charts }

    #if cache_results is True:
    #    current_app.cache.set(cache_key, tot_dict)

    #if return_from_cache is True:
    #    return current_app.cache.get(cache_key)

    return tot_dict


# Elsewhere, facets are referred to as 'aggregations'. I find it to be confusing to have two 
# different terms for the same thing (facets)    
def get_facet_counts(fields):
    # Params: fields = list of fields prefixed with node label as in ['VSS.study_name','PS.time_point']
    
    # Returns aggregations (values and counts) for specific node properties for specific node_types
    # Return dict as
    """
    {
     "aggregations": {
        "study_name": {
            "buckets": [
              {
                "key": "PROTECT", 
                "doc_count": 1212
              }, 
              {
                "key": "Herfarth", 
                "doc_count": 1083
              }, 
              {
                "key": "Jansson-Lamendella", 
                "doc_count": 1075
              }, 
              {
                "key": "RISK", 
                "doc_count": 849
              }, 
              {
                "key": "Mucosal IBD", 
                "doc_count": 106
              }
            ]
      }
    }
    """
    
    # Check if facet_counts already cached
    if current_app.cache.get("facet_counts") is None:
        current_app.cache.set("facet_counts", {})
                              
    cached_count_dict = current_app.cache.get("facet_counts")

    # facet counts may be cached, but may not be complete and may not contain the incoming fields    
    cached_fields = cached_count_dict.keys()
    uncached_fields = [field for field in fields if field not in cached_fields]
    if uncached_fields:
        cached_count_dict.update(_build_facet_counts(uncached_fields))

    current_app.cache.set("facet_counts", cached_count_dict)
    
    # Only want to return subset of cached aggregations (facet counts). Ones that were requested as fields list
    aggs = {k: cached_count_dict[k] for k in fields if k in cached_count_dict}
    
    return {"aggregations" : aggs}


def execute_safe_query(cypher, **kwargs):

    lower_cy = cypher.lower()
    for pms in POTENTIALLY_MALICIOUS_STRINGS:
        if pms in lower_cy:
            print("Potentially unsafe cypher detected: " + cypher)
            print("Skipping")
            raise Exception("Potentially unsafe cypher detected: " + cypher)
        
    # cypher is now considered safe
    cursor = []
    
    try:
        cursor = cypher_conn.run(cypher, **kwargs)
    except Exception as e:
        print("Error running cypher: ", e)
    
    return cursor
                
def get_urls_for_download(ids):
    cquery = "MATCH (F:file) WHERE F.id IN {ids} RETURN F"
    res = execute_safe_query(cquery, ids=ids)
    urls = []
    for entry in res:
        urls.append(extract_url(dict(entry)['F']))

    return urls

# Function to place a list into a string format that Neo4j understands
def build_neo4j_list(id_list):
    print("build_neo4j_list!")

    ids = ""
    mod_list = []
    
    # Surround each value with quotes for Neo4j comparison
    for id in id_list:
        mod_list.append("'{0}'".format(id))

    print("mod_list: ")
    print( mod_list)
    
    # Separate by commas to make a Neo4j list
    if len(mod_list) > 1:
        ids = ",".join(mod_list)
    else: # just a single ID
        ids = mod_list[0]

    return ids

def get_manifest_data(id_list):
    ids = build_neo4j_list(id_list)

    # Surround in brackets to format list syntax
    ids = "[{0}]".format(ids)
    # cquery = "MATCH (F:file)-[:derived_from]->(S:sample) WHERE F.id IN {0} RETURN F,S".format(ids)
    cquery = "UNWIND {0} AS file_id MATCH (file:file{{id:file_id}})-[:derived_from]->(sample:sample) RETURN file, sample".format(ids)
    res = _process_cquery_http(cquery)

    items = [(col['col-name'], []) for col in config['cart']['manifest-download']['cols']] # essentially defaultdict of OrderedDict
    cols = OrderedDict(items)

    for entry in res:
        for col in config['cart']['manifest-download']['cols']:
            col_name = col['col-name']
            node_type = col['node-type']
            prop = col['prop']

            if node_type == '' or node_type == 'null':
                if col_name == "urls":
                    cols["urls"].append(extract_manifest_urls(entry["file"]))

                if col_name == "component_files":
                    urls = extract_manifest_urls(entry["file"])
                    cols["component_files"].append(determine_component_files(urls, entry["file"]))
            else:
                cols[col_name].append(entry[node_type][prop])

    return build_tsv(cols)


def get_metadata(id_list):

    # If study-level matrices are enabled, add the related file IDs to the id_list
    if config['cart']['enable-study-level-matrices']:
        id_list = apply_file_ids_from_study_level_matrix(id_list)

    # cquery = "MATCH (file:file)-[:derived_from]->(sample:sample)-[:extracted_from]->(subject:subject) WHERE file.id IN {0} RETURN sample,subject,file".format(id_list)
    cquery = "UNWIND {0} AS file_id MATCH (file:file{{id:file_id}})-[:derived_from]->(sample:sample)-[:extracted_from]->(subject:subject) RETURN sample,subject,file".format(id_list)
    res = _process_cquery_http(cquery)
    
    items = [(col['col-name'], []) for col in config['cart']['metadata-download']['cols']] # essentially defaultdict of OrderedDict
    cols = OrderedDict(items)

    for entry in res:
        for meta in config['cart']['metadata-download']['cols']:
            col_name = meta['col-name']
            node_type = meta['node-type']
            prop = meta['prop']
            cols[col_name].append(entry[node_type][prop])

    return build_tsv(cols)

def build_tsv(download_data):
    rows = []
    rows.append("\t".join(list(download_data.keys()))) # header

    # Create a string with all the found data to pass to the file
    length_of_first_col = len(list(download_data[download_data.keys()[0]]))
    
    for i in range(0, length_of_first_col):
        row = []
        for key in download_data:
            try:
                row.append(download_data[key][i])
            except:
                print("'{}' column data was short. skipping... '{}'... skipping".format(key, download_data[list(download_data.keys())[0]][i]))
                pass
        rows.append( "\t".join(str(val) for val in row) ) #DOLLEY: ensure each val is string. otherwise ints cause errors

    return ("\n").join(rows)

def apply_file_ids_from_study_level_matrix(id_list):
    # Create an id_list array for better handling
    id_array = json.loads(id_list)
    study_level_flag = config['cart']['study-level-matrix-flag']
    study_name_field = config['cart']['study-name-on-node']
    
    # Get the study of the study level matrix
    study_cquery = "MATCH(subject:subject)<-[:extracted_from]-(sample:sample)<-[:derived_from]-(file:file) WHERE " + study_level_flag + " = true AND file.id IN {id_array} RETURN " + study_name_field + " AS study_name, file.id AS file_id"
    res = execute_safe_query(study_cquery, id_array=id_array)
    
    # For each study, get a list of file_ids associated with that study
    for study_record in res:
        study = dict(study_record)['study_name']
        matrix_file_id = dict(study_record)['file_id']

        # Remove the study-level matrix ID. We don't want metadata on it
        id_array.remove(matrix_file_id)
        
        # Get file IDs that are related to the study in question
        ids_cquery = "MATCH(subject:subject)<-[:extracted_from]-(sample:sample)<-[:derived_from]-(file:file) WHERE " + study_name_field + " = {study} RETURN COLLECT(file.id) AS file_ids"
        ids_res = execute_safe_query(ids_cquery, study=study)

        # Add each file ID to id_list if it's not already there
        for ids_record in ids_res:
            for file_id in dict(ids_record)['file_ids']:
                if file_id not in id_array:
                    id_array.append(file_id)

    return json.dumps(id_array)


# Makes sure we generate a unique token
def check_token(token,ids):

    subset_token = ""

    for j in range(0,len(token)-6):
        subset_token = token[j:j+6]
        token_check = _process_cquery_http("MATCH (t:token{id:'{0}'}) RETURN t".format(subset_token))
        if len(token_check) == 0:
            cquery = "CREATE (t:token{{id:'{0}',id_list:{1}}})".format(subset_token,ids)
            _process_cquery_http(cquery)
            return subset_token
        else:
            if str(token_check[0]['t']['id_list']) == ids:
                return subset_token

    return subset_token

def get_manifest_token(id_list):

    id_list.sort() # ensure ordering doesn't affect the token creation

    ids = build_neo4j_list(id_list)

    # overkill, but should suffice
    original_token = hashlib.sha256(ids).hexdigest()
    original_token += hashlib.sha224(ids).hexdigest()
    ids = "[{0}]".format(ids)

    token = check_token(original_token,ids)

    if token != "":
        return token
    else:
        token = check_token(original_token[::-1],ids) # try the reverse

    if token != "":
        return token
    else:
        return "ERROR generating token."

# Takes in a token and hits the Neo4j server to create a manifest on the fly
# using all the IDs noted within the particular token.
def token_to_manifest(token):

    # Leave early if the token is obviously corrupt
    if len(token) != 6:
        return 'Error -- Invalid token length.'
    if not re.match(r"^[a-zA-Z0-9]+$",token):
        return 'Error -- Invalid characters detected.'

    ids = _process_cquery_http("MATCH (t:token{{id:'{0}'}}) RETURN t.id_list AS id_list".format(token))[0]['id_list']
    urls = ['https','http','ftp','gs','s3']
    manifest = ""
    for id in ids:
        file = _process_cquery_http("MATCH (f:file{{id:'{0}'}}) RETURN f".format(id))[0]['f']
        url_list = []
        for url in urls:
            if url in file:
                url_list.append(file[url])

        if manifest != "":
            manifest += "\n"

        manifest += "{0}\t{1}\t{2}".format(id,file['md5'],','.join(url_list))

    return manifest

# This is a recursive function originally used to traverse and find the depth
# of nested JSON. Now used to traverse the op/filters query from GDC and
# ultimately aims to provide input to build the WHERE clause of a Cypher query.
# Accepts input of json.loads parsed GDC portal query input and an empty array.
# Note that this is currently only called when facet search is being performed.
import decimal

def get_depth(x, arr):
    if type(x) is dict and x:
        if 'op' in x:
            arr.append(x['op'])
        if 'field' in x:
            left = x['field']
            right = x['value']
            if type(x['value']) is list:
                l = []
                for element in x['value']:
                    if isinstance(element,float):
                        element = decimal.Decimal(element)
                    l.append("\"{0}\"".format(element)) # need to add quotes around each element to make Cypher happy
                right = ",".join(l)
            else:
                # mschor, this format() was causing a big problem for precise decimals.
                # E.g. format converts float 20.8307031940412 to 20.830703194 as does the str frunction.
                # Using decimal now to handle it more precisely
                if isinstance(element,float):
                    right = decimal.Decimal(right)
                right = "\"{0}\"".format(right) # again, quotes for Cypher.
            arr.append(left)
            arr.append(right)
        return max(get_depth(x[a], arr) for a in x)
    if type(x) is list and x:
        return max(get_depth(a, arr) for a in x)
    
    return arr # give the array back after traversal is complete

# Fxn to build Cypher based on facet search, accepts output from get_depth
def build_facet_where(inp):
    
    facets = OrderedDict() # going to build an array of all the facets params present
    
    lstr, rstr = ("" for i in range(2))
    for x in reversed(range(0,len(inp))):
        if "\"" in inp[x]: # found the values to search for
            value_list = inp[x].replace("\"", "").split(',')
            clean_vals = list()
            for val in value_list:
                try:
                    val = float(val)
                    clean_vals.append(val)
                except:
                    clean_vals.append(val) 
            rstr = "{0}".format(str(clean_vals))
        elif "." in inp[x]: # found the fields to search on
            lstr = inp[x]
        elif "in" == inp[x]: # found the comparison op, build the full string
            facet_key = lstr.replace(".","_") # Cypher can't have a . in a param name and this will be used to run a parameterized query later
            # At this point, rstr should be string representation of a list. Need to convert this to an actual list of strings
            facets[facet_key]= ast.literal_eval(rstr) 
    
    return facets    

# Whether or not to traverse to the tag level, only required when a tag is
# being searched
def _which_traversal(where):
    traversal = ""
    if "T.term" in where:
        traversal = tag_traversal
    else:
        traversal = FULL_TRAVERSAL
    return traversal


def _build_where(whereFilters):
    
    arr = []

    q = json.loads(whereFilters) # parse filters input into JSON (yields hashes of arrays) 
    w1 = get_depth(q, arr) # first step of building where clause is the array of individual comparison elements
    facet_value_dict = build_facet_where(w1)

    # At this point, facet_value_dict contains entries like:
    # { "sample_study_name" : "['study1']" }
    where_clause = " WHERE "
    
    for facet in facet_value_dict:
        where_clause += facet.replace("_",".",1) + " in {" + facet + "} and " # replace . with _ because cypher param placeholder cannot contain a .
    
    if where_clause.endswith(" and "):
        where_clause = where_clause[0:-5] # remove last 'and'
    return (where_clause, facet_value_dict)

# This advanced Cypher builder expects the string generated by any of the advanced queries.

# Final function needed to build the entirety of the Cypher query taken from facet search. Accepts the following:
# match = base MATCH query for Cypher
# whereFilters = filters string passed from GDC portal
# order = parameters to order results by (needed for pagination)
# start = index of sort to start at
# size = number of results to return
# rtype = return type, want to be able to hit this for both cases, files, and aggregation counts.

def _build_adv_cypher(whereFilters,order,start,size,rtype):
    returns = get_returns() # Get updated version of returns
    order = order.replace("cases.","")
    order = order.replace("files.","")
    
    where = _preprocess_wherefilters(whereFilters)
    traversal = _which_traversal(where)
    retval1 = returns[rtype] # actual RETURN portion of statement
    
    # At this point, where is something like: 
    # sample.study_name in ['Jansson_Lamendella_Crohns','RISK'] and subject.race = 'african_american'
    # where every first word is the cypher field, the second is the operator, and the third field is the value. If there's a 4th word, it's an 'and' or 'or'

    # Now convert into a parameterized where statement
    paramed_where = ""
    
    # For shlex to keep bracketed values as one word, put them in escaped quotes
    where = where.replace("[","\"[").replace("]","\"]") 
    # Now split into words
    try:
        words = shlex.split(where)
    except:
        print("Failed to parse query: " + where)
        words = []
    
    param_dict = {}
    
    # Potential clauses of advanced search follow the form of:
    # <field> <operator> <value> (optional [and|or] for additional clauses
    
    # More specifically, clauses may be any of these (all of which may be followed by and/or) 
    # 1) <field> [= | != | < | <= | >= | > | EXCLUDE ] <value>
    # 2) <field> IN <bracketed value list>
    # 3) <field> [IS | NOT] MISSING

    # Append an extra word to make query divisible by 4 
    # as the final clause will only be 3 words instead of 4 (missing and/or) 
    words.append("") 
    
    for i in range(0,len(words)/4):
        cypher_field = words[i*4]
        param_field = cypher_field.replace(".","_")
        op = words[i*4+1]
        value = words[i*4+2]
        
        if op.lower() not in ["=", "<>", "<", "<=", ">", ">=", "is", "not", "in", "exclude"]:
            raise Exception("Invalid operation. op was: -->" + op + "<--")
        if value.startswith("["):
            value = value[1:-1] # chop off enclosing "[ ]"
            value = value.split(",")
            value = list(map(_trim_value, value))
        elif value.lower() == "missing":
            value = None
            if op.lower() == "not":
                op = "IS NOT"

        # because params go into a dictionary, see if key already exists so as to not overwrite it
        while param_field in param_dict:
            param_field += "_"
            
        if op.lower() == "exclude":
            paramed_where += " NOT " + cypher_field + " IN " + " {" + param_field + "} "
        elif value is None:
            paramed_where += " " + cypher_field + " " + op + " NULL "
        else:
            paramed_where += " " + cypher_field + " " + op + " {" + param_field + "} "
        
        if len(words) > i*4+3:
            logical_op = words[i*4+3] # AND | OR
            paramed_where += " " + logical_op
        
        if value is None:
            continue
        
        converted_value = _convert_value_to_correct_type(cypher_field, value)
        param_dict[param_field] = converted_value
    
    return ("{0} WHERE {1} {2}".format(traversal,paramed_where,retval1), param_dict)


def _process_cquery_http(query):
    res = execute_safe_query(query)
    results = []
    for record in res:
        results.append(dict(record))
    # results = res.data() #DOLLEY: this is a py2neo function that does the same as above (not tested)
    
    try:
        res.close()
    except:
        pass
    
    return results

# Removes extra quotes if present and trims whitespace
def _trim_value(value):
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")): 
            value = value[1:-1]
        return value.strip()

# Accepts value as a string or list of strings
# Returns appropriate type (or list of appropriate type) as defined in metadata mapping
def _convert_value_to_correct_type(cypher_field, value):
    
    metadata_field_name = cypher_field[cypher_field.find(".")+1:]
    field_type = METADATA_MAPPING[metadata_field_name]['type'].lower()
    
    # default to input
    converted_value = value
    
    if field_type == "string":
        return converted_value
    
    if field_type == "number" or field_type == "integer" or field_type == "long" or field_type == "float":
        if type(value) is list:
            try:
                converted_value = list(map(float, value))
            except ValueError as e:
                print("Error converting number. Expected numeric values in list: " + str(value), e)
        else:
            try:
                converted_value = float(value)
            except ValueError as e:
                print("Error converting number. Expected numeric values in list: " + str(value), e)
    else:
        print("Unexpected type found in METADATA MAPPING: " + field_type)
    
    return converted_value


def _preprocess_wherefilters(whereFilters):
    
    if '%20' in whereFilters:
        whereFilters = urllib.unquote(whereFilters).decode('utf-8')

    # whereFilters comes in like: {"query": "sample.study_name = \"Jansson_Lamendella_Crohns\""}
    # remove leading part of string ({"query": ")
    where = whereFilters[10:len(whereFilters)-2]
    where = where.replace("!=","<>")
    where = where.strip()
    
    # Add quotes that FE missed
    if '=' in where:
        where = regexForEqual.sub(r'= "\1"',where)
    if '<>' in where:
        where = regexForNotEqual.sub(r'<> "\1"',where)

    # Replace \" with just '
    where = where.replace("\\\"", "'")
    
    # some cases where it has a leading quote. Should track down. From original code.
    if where.startswith("\""):
        where = where[1:]
    
    return where    

def _calc_pages(total, size):
    if size == 0:
        return 0
    
    if total > 0:
        pages = int(total / size)
        if total % size != 0:
            pages += 1
    else:
        pages = 0
    return pages

# TODO: mschor: Look at combining this function with _build_facet_counts()
def _build_facet_counts_where(fields, where, param_map):
    
    facet_counts = {}

    for field in fields:
        if field not in METADATA_CY_FIELDS:
            print("Field: " + field + " was not found in METADATA_MAPPING. Skipping this.")
            return facet_counts
    
    match = "MATCH (subject:subject)<-[:extracted_from]-(sample:sample)<-[:derived_from]-(file:file) " 
    exists_and_return =  " and EXISTS({0}.{1}) RETURN {0}.{1} as key, COUNT(DISTINCT({0})) as doc_count"
    
    
    # We don't want to recalculate buckets based on latest facet clicked because 
    # if users wants to select additional values for that facet, then they can       
    most_recent_facet_clicked = None
    start = 0
    if "." in where:
        dot_loc = where.rfind(".")
        start = where.find("WHERE ") + 6
        stop = where.find(" ", start)
        most_recent_facet_clicked = where[start:stop]
        stop = where.find("}", where.find("WHERE ") + 6) + 1
        if where[stop:].startswith(" and "):
            stop = stop + 5
        
    label_field_map = {}
    
    for field in fields:
        if field == most_recent_facet_clicked:
            where_without_most_recent = where[0:start] + where[stop:]
            if where_without_most_recent == " WHERE ":
                exists_and_return_minus_and = exists_and_return[4:]
                query = match + where_without_most_recent + exists_and_return_minus_and
            else:
                query = match + where_without_most_recent + exists_and_return
        else:
            query = match + where + exists_and_return
            
            
        if "." not in field:
            # somewhat hacky. The '.' comes through in the default facets, but in the added facets, it doesn't.
            # could A) Figure out how to make the '.' come through in the added facets
            # or    B) if it doesn't come through, pull it from the METADATA_MAPPING
            if field in METADATA_MAPPING:
                field = METADATA_MAPPING[field]['cypher_field']
            else:
                # Log instead of print. TOOD: mschor: add logging
                print("Unexpected field: " + field + " passed in as facet. Not found in mapping")
                continue
        
        (label, property) = field.split(".", 1)
        if label not in label_field_map:
            label_field_map[label] = _get_all_property_keys_for_node_type(label)
            
        facet_counts[field] = {}
        buckets = []
        
        # avert injection attempt or otherwise bad param 
        if property not in label_field_map[label]:
            print("Field: " + property + " was not found to be a valid type, returning blank")
            facet_counts[field]["buckets"] = []
            continue
        
        if "." in property:
            property = "`" + property + "`"
        #results = execute_safe_query(query.format(label, property), param_map)
        q = query.replace("{0}",label).replace("{1}",property)
        results = execute_safe_query(q, **param_map)
        
        for record in results:
            # result like: (u'VSS.study_name': u'LSS-PRISM', u'counts': 1)
            d_record = dict(record)
            buckets.append(d_record)
        facet_counts[field]["buckets"] = buckets
        
        try:
            results.close()
        except:
            pass
    
    return facet_counts

def _build_facet_counts(fields):
    facet_counts = {}

    for field in fields:
        if field not in METADATA_CY_FIELDS:
            print("Field: " + field + " was not found in METADATA_MAPPING. Skipping it.")
            return facet_counts
       
    query = """
        MATCH (subject:subject)<-[:extracted_from]-(sample:sample)<-[:derived_from]-(file:file) 
        WHERE EXISTS({0}.{1}) RETURN {0}.{1} as key, COUNT(DISTINCT({0})) as doc_count
    """
    
    label_field_map = {}
    
    for field in fields:
        if "." not in field:
            # somewhat hacky. The '.' comes through in the default facets, but in the added facets, it doesn't.
            # could A) Figure out how to make the '.' come through in the added facets
            # or    B) if it doesn't come through, pull it from the METADATA_MAPPING
            if field in METADATA_MAPPING:
                field = METADATA_MAPPING[field]['cypher_field']
            else:
                # Log instead of print. TOOD: mschor: add logging
                print("Unexpected field: " + field + " passed in as facet. Not found in mapping")
                continue
        
        (label, property) = field.split(".", 1)
        if label not in label_field_map:
            label_field_map[label] = _get_all_property_keys_for_node_type(label)
            
        facet_counts[field] = {}
        buckets = []
        
        # avert injection attempt or otherwise bad param 
        if property not in label_field_map[label]:
            print("Field: " + property + " was not found to be a valid type, returning blank")
            facet_counts[field]["buckets"] = []
            continue
        
        if "." in property:
            property = "`" + property + "`"
        results = execute_safe_query(query.format(label, property))
        
        for record in results:
            # result like: (u'VSS.study_name': u'LSS-PRISM', u'counts': 1)
            d_record = dict(record)
            buckets.append(d_record)
        facet_counts[field]["buckets"] = sorted(buckets, key = lambda d: d["key"])
        
        try:
            results.close()
        except:
            pass
    
        
    return facet_counts

def _convert_order(order):

    # garbage in / garbage out
    if not order or len(order) == 0:
        return order
    
    # replace UI ':' with a ' '
    order = order.replace(':',' ')
    order = order.replace('.raw','') # trim more GDC syntax (mschor: not sure what this is, but keep for now)

    # UI has an erroneous ',' appended for files occasionally 
    if order[-1] == ',':
        order = order[:-1]

    # At this point, order should be in the form of: <node_type>.<property> <asc|desc>
    
    node_type = order[:order.find(".")]
    property = order[order.find(".")+1:order.find(" ")]
    sort = order[order.find(" ")+1:]
    if node_type not in _get_node_labels():
        return ""
    if property not in _get_all_property_keys_for_node_type(node_type):
        return ""
    if sort != "" and not (sort.lower() == "asc" or sort.lower() == "desc"):
        return ""
    
    # It's valid, return it
    return " ORDER BY " + order

def _get_all_property_keys_for_node_type(node_type):
    
    # Check if prop keys already cached
    cache_key = "prop_keys_" + node_type
    if current_app.cache.get(cache_key) is None:
     
        #validate node_type
        if node_type not in _get_node_labels():
            print("node type was not in: " + str(_get_node_labels()))
            return
        
        keys = cypher_conn.run("MATCH (n:" + node_type + ") UNWIND keys(n) AS key RETURN collect(distinct key) as key_list").data()
        
        #keys is something like: [{u'key_list': [u'database', u'sample_accession', u'id', u'study_name', u'sample_accession_db']}]
        current_app.cache.set(cache_key, keys[0]['key_list'])
        return keys[0]['key_list']
    
    else:
        return current_app.cache.get(cache_key)
    
    
def _get_node_labels():
    
    cache_key = "node_labels"
    if current_app.cache.get(cache_key) is None:
        labels = cypher_conn.run("call db.labels()").data()
        label_list = [ subdict['label'] for subdict in labels ]
        current_app.cache.set(cache_key, label_list)
        return label_list
    else:
        return current_app.cache.get(cache_key)

