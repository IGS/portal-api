import re, json, requests, hashlib
import ujson, urllib
from py2neo import Graph # Using py2neo v3 not v2
from conf import neo4j_ip, neo4j_bolt, neo4j_http, neo4j_un, neo4j_pw
from models import Project,Pagination,CaseHits,IndivFiles,Analysis,AssociatedEntities
from models import FileHits,Bucket,BucketCounter,Aggregations,SBucket,SBucketCounter,FileSize

# The match var is the base query to prepend all queries. The idea is to traverse
# the graph entirely and use filters to return a subset of the total traversal. 
# PSS = Project/Study/Subject
# VS = Visit/Sample
# File = File
full_traversal = "MATCH (PSS:subject)<-[:extracted_from]-(VS:sample)<-[:derived_from]-(F:file) "

# If the following return ends in "counts", then it is for a pie chart. The first two are for
# cases/files tabs and the last is for the total size. 
#
# All of these returns are pre-pended with "WITH DISTINCT File.*". This is because there is 
# some redundancy in the HMP data in that some nodes are iterated over multiple times. In order 
# to get around this, need to just return each file that is seen only once and bundle any of the
# other nodes alongside this single file. Meaning, "WITH DISTINCT File,Project" and only returning
# aspects of 'Project' like Project.name or something is only counted once along a given path to a 
# particular file. Note that each one has a fairly unique "WITH DISTINCT" clause, this is to help
# optimize the query and ensure the distinct check is as simple as the return allows it to be.

# The detailed queries require specifics about both sample and file counts to be 
# returned so they require some extra handling. 
base_detailed_return = ("WITH COUNT(DISTINCT(VS)) as ccounts, "
    "COUNT(F) AS dcounts, {0} AS prop, SUM(toInt(F.size)) as tot "
    "RETURN prop,ccounts,dcounts,tot"
    )

returns = {
    'cases': "RETURN DISTINCT PSS, VS",
    'files': "RETURN PSS, VS, F",
    'project_name': "RETURN PSS.project_name AS prop, count(PSS.project_name) AS counts",
    'project_name_detailed': base_detailed_return.format('PSS.project_name'),
    'study_name': "RETURN PSS.study_name AS prop, count(PSS.study_name) AS counts",
    'study_name_detailed': base_detailed_return.format('PSS.study_name'),
    'body_site': "RETURN VS.body_site AS prop, count(VS.body_site) AS counts",
    'body_site_detailed': base_detailed_return.format('VS.body_site'), 
    'study': "RETURN PSS.study_name AS prop, count(PSS.study_name) AS counts",
    'gender': "RETURN PSS.gender AS prop, count(PSS.gender) AS counts",
    'gender_detailed': base_detailed_return.format('PSS.gender'),
    'race': "RETURN PSS.race AS prop, count(PSS.race) AS counts",
    'format': "RETURN F.format AS prop, count(F.format) AS counts",
    'format_detailed': base_detailed_return.format('F.format'),
    'subtype_detailed': base_detailed_return.format('F.subtype'),
    'size': "RETURN (SUM(toInt(F.size))) AS tot",
    'f_pagination': "RETURN (count(F)) AS tot",
    'c_pagination': "RETURN (count(DISTINCT(VS.id))) AS tot"
}

# This populates the values in the side table of facet search. Want to let users
# know how many samples per category in a given property. 
count_props_dict = {
    "PSS": "MATCH (n:subject)<-[:extracted_from]-(VS:sample)<-[:derived_from]-(F:file) RETURN n.{0} AS prop, COUNT(DISTINCT(VS)) as counts",
    "VS": "MATCH (PSS:subject)<-[:extracted_from]-(n:sample)<-[:derived_from]-(F:file) RETURN n.{0} AS prop, COUNT(DISTINCT(n)) as counts",
    "F": "MATCH (PSS:subject)<-[:extracted_from]-(VS:sample)<-[:derived_from]-(n:file) RETURN n.{0} AS prop, COUNT(DISTINCT(VS)) as counts"
}

####################################
# FUNCTIONS FOR GETTING NEO4J DATA #
####################################

# Get all these values from the conf
neo4j_bolt = int(neo4j_bolt)
neo4j_http = int(neo4j_http)

# This section will have all the logic for populating the actual data in the schema (data from Neo4j)
#graph = Graph(host=neo4j_ip,bolt_port=neo4j_bolt,http_port=neo4j_http,user=neo4j_un,password=neo4j_pw)

def process_cquery_http(cquery):
    headers = {'Content-Type': 'application/json'}
    data = {'statements': [{'statement': cquery, 'includeStats': False}]}
    rq_res = requests.post(url='http://localhost:7474/db/data/transaction/commit',headers=headers, data=ujson.dumps(data), auth=(neo4j_un,neo4j_pw))

    query_res = []
    jsResp = ujson.loads(rq_res.text)
    column_names = jsResp['results'][0]['columns']

    for result in jsResp["results"][0]["data"]:
        res_dict = {}
        for i in range(0, len(column_names)):
            elem = result['row'][i]
            res_dict[column_names[i]] = elem
        query_res.append(res_dict)

    return query_res

# Function to extract a file name and an HTTP URL given values from a urls 
# property from an OSDF node. Note that this prioritizes http>fasp>ftp>s3
# and that it only returns a single one of the endpoints. This is in an effort
# to communicate a base URL in the result tables in the portal. 
def extract_url(urls_node):
   
    fn = ""

    if 'http' in urls_node:
        fn = urls_node['http']
    elif 'fasp' in urls_node:
        fn = urls_node['fasp'].replace("fasp://aspera","http://downloads")
    elif 'ftp' in urls_node:
        fn = urls_node['ftp']
    elif 's3' in urls_node:
        fn = urls_node['s3']
    else:
        fn = "No file attached to ID ({0})".format(urls_node['id'])

    return fn

# Function to return all present URLs for the manifest file
def extract_manifest_urls(urls_node):

    urls = []

    # Note that these are all individual ifs in order to grab all endpoints present
    if 'http' in urls_node:
        urls.append(urls_node['http'])
    if 'fasp' in urls_node:
        urls.append(urls_node['fasp'])
    if 'ftp' in urls_node:
        urls.append(urls_node['ftp'])
    if 's3' in urls_node:
        urls.append(urls_node['s3'])

    if len(urls) == 0: # if here, there is no downloadable file
        urls.append('private: Data not accessible via the HMP DACC.')

    return ",".join(urls)

# Function to get file size from Neo4j. 
# This current iteration should catch all the file data types EXCEPT for the *omes and the multi-step/repeat
# edges like the two "computed_from" edges between abundance matrix and 16s_raw_seq_set. Should be
# rather easy to accommodate these oddities once they're loaded and I can test.
def get_total_file_size(cy):
    cquery = ""
    if cy == "":
        cquery = "MATCH (F:file) RETURN SUM(toInt(F.size)) AS tot"
    elif '"op"' in cy:
        cquery = build_cypher(full_traversal,cy,"null","null","null","size")
    else:
        cquery = build_adv_cypher(full_traversal,cy,"null","null","null","size")
        cquery = cquery.replace('WHERE "',"WHERE ") # where does this phantom quote come from?!
    res = process_cquery_http(cquery)
    return res[0]['tot']

# Function for pagination calculations. Find the page, number of pages, and number of entries on a single page.
def pagination_calcs(total,start,size,c_or_f):
    pg,pgs,cnt,tot = (0 for i in range(4))
    sort = ""
    if c_or_f == "c":
        tot = int(total)
        sort = "case_id.raw:asc"      
    else:
        tot = int(total)
        sort = "file_name.raw:asc"
    if size != 0: pgs = int(tot / size) + (tot % size > 0)
    if size != 0: pg = int(start / size) + (start % size > 0)
    if (start+size) < tot: # less than full page, count must be page size
        cnt = size
    else: # if less than a full page (only possible on last page), find the difference
        cnt = tot-start
    pagcalcs = []
    pagcalcs.append(pgs)
    pagcalcs.append(pg)
    pagcalcs.append(cnt)
    pagcalcs.append(tot)
    pagcalcs.append(sort)
    return pagcalcs

# Function to determine how pagination is to work for the cases/files tabs. This will 
# take a Cypher query and a given table size and determine how many pages are needed
# to display all this data. 
# cy = Cypher filters/ops
# size = size of each page
# f = from/start position
def get_pagination(cy,size,f,c_or_f):
    cquery = ""
    if cy == "":
        if c_or_f == 'c':
            cquery = "MATCH (n:sample) RETURN count(n) AS tot"
        else:
            cquery = "MATCH (n:file) RETURN count(n) AS tot"
        res = process_cquery_http(cquery)
        calcs = pagination_calcs(res[0]['tot'],f,size,c_or_f)
        return Pagination(count=calcs[2], sort=calcs[4], fromNum=f, page=calcs[1], total=calcs[3], pages=calcs[0], size=size)
    else:
        if '"op"' in cy:
            if c_or_f == 'c':
                cquery = build_cypher(full_traversal,cy,"null","null","null","c_pagination")
            else:
                cquery = build_cypher(full_traversal,cy,"null","null","null","f_pagination")
        else:
            if c_or_f == 'c':
                cquery = build_adv_cypher(full_traversal,cy,"null","null","null","c_pagination")
                cquery = cquery.replace('WHERE "',"WHERE ") # where does this phantom quote come from?!
            else:
                cquery = build_adv_cypher(full_traversal,cy,"null","null","null","f_pagination")
                cquery = cquery.replace('WHERE "',"WHERE ") # where does this phantom quote come from?!
                
        res = process_cquery_http(cquery)
        calcs = pagination_calcs(res[0]['tot'],f,size,c_or_f)
        return Pagination(count=calcs[2], sort=calcs[4], fromNum=f, page=calcs[1], total=calcs[3], pages=calcs[0], size=size)

# Retrieve ALL files associated with a given Subject ID.
def get_files(sample_id):
    fl = []
    dt, fn, df, ac, fi = ("" for i in range(5))
    fs = 0
    
    cquery = "{0} WHERE VS.id='{1}' RETURN F".format(full_traversal,sample_id)
    res = process_cquery_http(cquery)

    for x in range(0,len(res)): # iterate over each unique path
        dt = res[x]['F']['subtype']
        df = res[x]['F']['format']
        ac = "open" # need to change this once a new private/public property is added to OSDF
        fs = res[x]['F']['size']
        fi = res[x]['F']['id']
        fn = extract_url(res[x]['F'])
        fl.append(IndivFiles(dataType=dt,fileName=fn,dataFormat=df,access=ac,fileId=fi,fileSize=fs))

    return fl

# Query to traverse top half of OSDF model (Project<-....-Sample). 
def get_proj_data(sample_id):
    cquery = "{0} WHERE VS.id='{1}' RETURN PSS.project_name AS name,PSS.project_subtype AS subtype".format(full_traversal,sample_id)
    res = process_cquery_http(cquery)
    return Project(name=res[0]['name'],projectId=res[0]['subtype'])

def get_all_proj_data():
    cquery = "MATCH (PSS:subject) RETURN DISTINCT PSS.study_name, PSS.study_description"
    return process_cquery_http(cquery)

def get_all_study_data():
    cquery = "{0} RETURN DISTINCT PSS.study_name, PSS.project_subtype, VS.body_site, COUNT(DISTINCT(VS)) as case_count, COUNT(F) as file_count".format(full_traversal)
    return process_cquery_http(cquery)

# This function is a bit unique as it's only called to populate the bar chart on the home page
def get_all_proj_counts():
    cquery = "{0} RETURN DISTINCT PSS.study_id, PSS.study_name, VS.body_site, COUNT(DISTINCT(VS)) as case_count, COUNT(F) as file_count".format(full_traversal)
    return process_cquery_http(cquery)

# Cypher query to count the amount of each distinct property
def count_props(node, prop, cy):
    cquery = ""
    if cy == "":
        cquery = count_props_dict[node].format(prop)
    else:
        cquery = build_cypher(full_traversal,cy,"null","null","null",prop)
    return process_cquery_http(cquery)

# Cypher query to count the amount of each distinct property
def count_props_and_files(node, prop, cy):

    cquery,with_distinct = ("" for i in range (2))
    
    if cy == "":
        retval = "RETURN {0}.{1} AS prop, COUNT(DISTINCT(VS)) AS ccounts, COUNT(F) AS dcounts, SUM(toInt(F.size)) as tot".format(node,prop)
        cquery = "{0} {1}".format(full_traversal,retval)

    else:
        prop_detailed = "{0}_detailed".format(prop)
        if "op" in cy:
            cquery = build_cypher(full_traversal,cy,"null","null","null",prop_detailed)
        else:
            cquery = build_adv_cypher(full_traversal,cy,"null","null","null",prop_detailed)
            cquery = cquery.replace('WHERE "',"WHERE ") # where does this phantom quote come from?!

    return process_cquery_http(cquery)

# Formats the values from count_props & count_props_and_files functions above into GQL
def get_buckets(inp,sum, cy):

    splits = inp.split('.') # parse for node/prop values to be counted by
    node = splits[0]
    prop = splits[1]
    bucketl,sortl = ([] for i in range(2)) # need two lists to sort these buckets by size

    if sum == "no": # not a full summary, just key and doc count need to be returned
        res = count_props(node, prop, cy)
        for x in range(0,len(res)):
            if res[x]['prop'] != "":
                cur = Bucket(key=res[x]['prop'], docCount=res[x]['counts'])
                sortl.append(int(res[x]['counts']))
                bucketl.append(cur)

        return BucketCounter(buckets=[bucket for(sort,bucket) in sorted(zip(sortl,bucketl),reverse=True)])

    else: # return full summary including case_count, doc_count, file_size, and key
        res = count_props_and_files(node, prop, cy)
        for x in range(0,len(res)):
            if res[x]['prop'] != "":
                cur = SBucket(key=res[x]['prop'], docCount=res[x]['dcounts'], fileSize=res[x]['tot'], caseCount=res[x]['ccounts'])
                bucketl.append(cur)

        return SBucketCounter(buckets=bucketl)

# Function to return case values to populate the table, note that this will just return first 25 values arbitrarily for the moment
# size = number of hits to return
# order = what to ORDER BY in Cypher clause
# f = position to star the return 'f'rom based on the ordering (python prevents using that word)
# cy = filters/op sent from GDC portal
def get_case_hits(size,order,f,cy):
    hits = []
    cquery = ""
    if cy == "":
        order = order.split(":")
        if f != 0:
            f = f-1
        retval = "RETURN DISTINCT PSS,VS ORDER BY {0} {1} SKIP {2} LIMIT {3}".format(order[0],order[1].upper(),f,size)
        cquery = "{0} {1}".format(full_traversal,retval)
    elif '"op"' in cy:
        cquery = build_cypher(full_traversal,cy,order,f,size,"cases")
    else:
        cquery = build_adv_cypher(full_traversal,cy,order,f,size,"cases")
        cquery = cquery.replace('WHERE "',"WHERE ") # where does this phantom quote come from?!

    res = process_cquery_http(cquery)

    for x in range(0,len(res)):
        cur = CaseHits(project=Project(projectId=res[x]['PSS']['project_subtype'],primarySite=res[x]['VS']['body_site'],name=res[x]['PSS']['project_name'],studyName=res[x]['PSS']['study_name'],studyFullName=res[x]['PSS']['study_name']),caseId=res[x]['VS']['id'])
        hits.append(cur)
    return hits

# Function to return file values to populate the table.
def get_file_hits(size,order,f,cy):
    hits = []
    cquery = ""
    if cy == "":
        order = order.split(":")
        if f != 0:
            f = f-1
        retval = "RETURN DISTINCT PSS,VS,F ORDER BY {0} {1} SKIP {2} LIMIT {3}".format(order[0],order[1].upper(),f,size)
        cquery = "{0} {1}".format(full_traversal,retval)
    elif '"op"' in cy:
        cquery = build_cypher(full_traversal,cy,order,f,size,"files")
    else:
        cquery = build_adv_cypher(full_traversal,cy,order,f,size,"files")
        cquery = cquery.replace('WHERE "',"WHERE ") # where does this phantom quote come from?!

    res = process_cquery_http(cquery)

    for x in range(0,len(res)):
        case_hits = [] # reinit each iteration
        cur_case = CaseHits(project=Project(projectId=res[x]['PSS']['project_subtype'],name=res[x]['PSS']['project_name']),caseId=res[x]['VS']['id'])
        case_hits.append(cur_case)

        furl = extract_url(res[x]['F']) # File name is our URL
        if '.hmpdacc' in furl and '/data/' in furl: # HMP endpoint
            furl = re.search(r'/data/(.*)',furl).group(1)
        elif '.ihmpdcc' in furl and 'org/' in furl:
            furl = re.search(r'\.org/(.*)',furl).group(1)

        # Should try handle this at an earlier phase, but make sure size exists
        if 'size' not in res[x]['F']:
            res[x]['F']['size'] = 0

        cur_file = FileHits(dataType=res[x]['F']['subtype'],fileName=furl,dataFormat=res[x]['F']['format'],submitterId="null",access="open",state="submitted",fileId=res[x]['F']['id'],dataCategory=res[x]['F']['node_type'],experimentalStrategy=res[x]['F']['subtype'],fileSize=res[x]['F']['size'],cases=case_hits)

        hits.append(cur_file)    
    return hits

# Pull all the data associated with a particular file ID. 
def get_file_data(file_id):
    cl, al, fl = ([] for i in range(3))
    retval = "WHERE F.id='{0}' RETURN PSS,VS,F".format(file_id)
    cquery = "{0} {1}".format(full_traversal,retval)
    res = process_cquery_http(cquery)
    furl = extract_url(res[0]['F']) 
    sample_bs = res[0]['VS']['body_site']
    wf = "{0} -> {1}".format(sample_bs,res[0]['F']['prep_node_type'])
    cl.append(CaseHits(project=Project(projectId=res[0]['PSS']['project_subtype']),caseId=res[0]['VS']['id']))
    al.append(AssociatedEntities(entityId=res[0]['F']['prep_id'],caseId=res[0]['VS']['id'],entityType=res[0]['F']['prep_node_type']))
    fl.append(IndivFiles(fileId=res[0]['F']['id']))
    a = Analysis(updatedDatetime="null",workflowType=wf,analysisId="null",inputFiles=fl) # can add analysis ID once node is present or remove if deemed unnecessary
    return FileHits(dataType=res[0]['F']['node_type'],fileName=furl,md5sum=res[0]['F']['md5'],dataFormat=res[0]['F']['format'],submitterId="null",state="submitted",access="open",fileId=res[0]['F']['id'],dataCategory=res[0]['F']['node_type'],experimentalStrategy=res[0]['F']['study'],fileSize=res[0]['F']['size'],cases=cl,associatedEntities=al,analysis=a)

def get_url_for_download(id):
    cquery = "MATCH (F:file) WHERE F.id='{0}' RETURN F".format(id)
    res = process_cquery_http(cquery)
    return extract_url(res[0]['F'])

# Function to place a list into a string format that Neo4j understands
def build_neo4j_list(id_list):

    ids = ""
    mod_list = []
    
    # Surround each value with quotes for Neo4j comparison
    for id in id_list:
        mod_list.append("'{0}'".format(id))
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
    cquery = "MATCH (F:file) WHERE F.id IN {0} RETURN F".format(ids)
    res = process_cquery_http(cquery)

    outlist = []

    # Grab the ID, file URL, md5, and size
    for entry in res:
        id = entry['F']['id']
        urls = extract_manifest_urls(entry['F'])
        md5 = entry['F']['md5']
        size = entry['F']['size']
        outlist.append("\n{0}\t{1}\t{2}\t{3}".format(id,md5,size,urls))

    return outlist

# Makes sure we generate a unique token
def check_token(token,ids):

    subset_token = ""

    for j in range(0,len(token)-6):
        subset_token = token[j:j+6]
        token_check = process_cquery_http("MATCH (t:token{id:'{0}'}) RETURN t".format(subset_token))
        if len(token_check) == 0:
            cquery = "CREATE (t:token{{id:'{0}',id_list:{1}}})".format(subset_token,ids)
            process_cquery_http(cquery)
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

    ids = process_cquery_http("MATCH (t:token{{id:'{0}'}}) RETURN t.id_list AS id_list".format(token))[0]['id_list']
    urls = ['http','ftp','fasp','s3']
    manifest = ""
    for id in ids:
        file = process_cquery_http("MATCH (f:file{{id:'{0}'}}) RETURN f".format(id))[0]['f']
        url_list = []
        for url in urls:
            if url in file:
                url_list.append(file[url])

        if manifest != "":
            manifest += "\n"

        manifest += "{0}\t{1}\t{2}".format(id,file['md5'],','.join(url_list))

    return manifest

# Function to extract known GDC syntax and convert to OSDF. This is commonly needed for performing
# cypher queries while still being able to develop the front-end with the cases syntax.
def convert_gdc_to_osdf(inp_str):
    # Errors in Graphene mapping prevent the syntax I want, so ProjectName is converted to 
    # Cypher ready Project.name here (as are the other possible query parameters).
    inp_str = inp_str.replace("cases.ProjectName","PSS.project_name")
    inp_str = inp_str.replace("cases.SampleFmabodysite","VS.body_site")
    inp_str = inp_str.replace("cases.SubjectGender","PSS.gender")
    inp_str = inp_str.replace("project.primary_site","VS.body_site")
    inp_str = inp_str.replace("subject.gender","PSS.gender")
    inp_str = inp_str.replace("study.name","PSS.study_name")
    inp_str = inp_str.replace("file.format","F.format")
    inp_str = inp_str.replace("file.category","F.subtype") # note the conversion
    inp_str = inp_str.replace("files.file_id","F.id")
    inp_str = inp_str.replace("cases.","") # these replaces have to be catch alls to replace all instances throughout
    inp_str = inp_str.replace("sample.","")
    inp_str = inp_str.replace("Project_","PSS.project_")
    inp_str = inp_str.replace("Sample_","VS.")
    inp_str = inp_str.replace("SampleAttr_","VS.")
    inp_str = inp_str.replace("Study_","PSS.study_")
    inp_str = inp_str.replace("Subject_","PSS.")
    inp_str = inp_str.replace("SubjectAttr_","PSS.")
    inp_str = inp_str.replace("Visit_","VS.visit_")
    inp_str = inp_str.replace("VisitAttr_","VS.visit_")
    inp_str = inp_str.replace("File_","F.")

    inp_str = inp_str.replace("file.","F.")

    # Handle facet searches from panel on left side
    inp_str = inp_str.replace("data_type","F.node_type")
    inp_str = inp_str.replace("data_format","F.format")

    # Next two lines guarantee URL encoding (seeing errors with urllib)
    inp_str = inp_str.replace('"','|')
    inp_str = inp_str.replace('\\','')
    inp_str = inp_str.replace(" ","%20")
    inp_str = inp_str.replace(": ",":")

    # While the DB is to be set at read-only, in the case this toggle is 
    # forgotten do some checks to make sure nothing fishy is happening.
    potentially_malicious = set([";"," delete "," create "," detach "," set ",
                                " return "," match "," merge "," where "," with ",
                                " import "," remove "," union "])
    check_str = inp_str.lower()
    for word in check_str:
        if word in potentially_malicious:
            return "Invalid characters."

    return inp_str

# This is a recursive function originally used to traverse and find the depth 
# of nested JSON. Now used to traverse the op/filters query from GDC and 
# ultimately aims to provide input to build the WHERE clause of a Cypher query. 
# Accepts input of json.loads parsed GDC portal query input and an empty array. 
# Note that this is currently only called when facet search is being performed.
def get_depth(x, arr):
    if type(x) is dict and x:
        if 'op' in x:
            arr.append(x['op'])
        if 'field' in x:
            left = x['field']
            right = x['value']
            if type(x['value']) is list:
                l = x['value']
                l = ["'{0}'".format(element) for element in l] # need to add quotes around each element to make Cypher happy
                right = ",".join(l)
            else:
                right = "'{0}'".format(right) # again, quotes for Cypher
            arr.append(left)
            arr.append(right)
        return max(get_depth(x[a], arr) for a in x)
    if type(x) is list and x: 
        return max(get_depth(a, arr) for a in x)
    return arr # give the array back after traversal is complete

# Fxn to build Cypher based on facet search, accepts output from get_depth
def build_facet_where(inp): 
    facets = [] # going to build an array of all the facets params present
    lstr, rstr = ("" for i in range(2))
    for x in reversed(range(0,len(inp))):
        if "'" in inp[x]: # found the values to search for
            rstr = "[{0}]".format(inp[x]) # add brackets for Cypher
        elif "." in inp[x]: # found the fields to search on
            lstr = inp[x]
        elif "in" == inp[x]: # found the comparison op, build the full string
            facets.append("{0} in {1}".format(lstr, rstr))
    return " AND ".join(facets) # send back Cypher-ready WHERE clause

# Function to convert syntax from facet/advanced search pages and move it into 
# the new Neo4j schema's format. This is a step we likely cannot account for 
# on the portal itself as we want users to be able to do something like search
# for Project name as Project.name or something similar instead of PSS.project_name.
def convert_portal_to_neo4j(inp_str):

    if inp_str[0].isupper():
        inp_str = inp_str[0].lower() + inp_str[1:]

    inp_str = inp_str.replace("Project.","project.")

    # Project -> Study -> Subject
    inp_str = inp_str.replace("project.","PSS.project_")
    inp_str = inp_str.replace("study.","PSS.study_")
    inp_str = inp_str.replace("subject.","PSS.")
    # Visit -> Sample
    inp_str = inp_str.replace("visit.","VS.visit_")
    inp_str = inp_str.replace("sample.","VS.")
    # File
    inp_str = inp_str.replace("file.","F.")

    inp_str = inp_str.replace("%20"," ")
    return inp_str

# Final function needed to build the entirety of the Cypher query taken from facet search. Accepts the following:
# match = base MATCH query for Cypher
# whereFilters = filters string passed from GDC portal
# order = parameters to order results by (needed for pagination)
# start = index of sort to start at
# size = number of results to return
# rtype = return type, want to be able to hit this for both cases, files, and aggregation counts.
def build_cypher(match,whereFilters,order,start,size,rtype):
    arr = []
    whereFilters = convert_portal_to_neo4j(whereFilters)
    q = json.loads(whereFilters) # parse filters input into JSON (yields hashes of arrays)
    w1 = get_depth(q, arr) # first step of building where clause is the array of individual comparison elements
    where = build_facet_where(w1)
    where = where.replace("cases.","") # trim the GDC syntax, hack until we refactor cases/files syntax
    where = where.replace("files.","")
    order = order.replace("cases.","")
    order = order.replace("files.","")
    retval1 = returns[rtype] # actual RETURN portion of statement
    if rtype in ["cases","files"]: # pagination handling needed for these returns
        order = order.split(":")

        # When adding all files to cart, a special case happens where there is
        # no order specified so have to return a more basic query.
        if len(order) < 2:
            return "{0} WHERE {1} {2}".format(match,where,retval1)

        if start != 0:
            start = start - 1
        retval2 = "ORDER BY {0} {1} SKIP {2} LIMIT {3}".format(order[0],order[1].upper(),start,size) 
        return "{0} WHERE {1} {2} {3}".format(match,where,retval1,retval2)
    else:
        return "{0} WHERE {1} {2}".format(match,where,retval1)

# First iteration, handling all regex individually
regexForNotEqual = re.compile(r"<>\s([0-9]*[a-zA-Z_]+[a-zA-Z0-9_]*)\b") # only want to add quotes to anything that's not solely numbers
regexForEqual = re.compile(r"=\s([0-9]*[a-zA-Z_]+[a-zA-Z0-9_]*)\b") 
regexForIn = re.compile(r"(\[[a-zA-Z\'\"\s\,\(\)]+\])") # catch anything that should be in a list

# This advanced Cypher builder expects the string generated by any of the advanced queries. 
# Parameters are described above before build_cypher()
def build_adv_cypher(match,whereFilters,order,start,size,rtype):

    if '%20' in whereFilters:
        whereFilters = urllib.unquote(whereFilters).decode('utf-8')

    where = whereFilters[10:len(whereFilters)-2]
    where = where.replace("!=","<>")
    where = where.strip()

    # Add quotes that FE missed
    if '=' in where:
        where = regexForEqual.sub(r'= "\1"',where)
    if '<>' in where:
        where = regexForNotEqual.sub(r'<> "\1"',where)
    if ' in ' in where or ' IN ' in where: # lists present, parse through and add quotes to all values without them
        lists = re.findall(regexForIn,where)
        listDict = {}
        for extractedList in lists:
            original = extractedList
            extractedList = extractedList.replace('[','')
            extractedList = extractedList.replace(']','')
            indivItems = extractedList.split(',')
            newList = []
            for item in indivItems:
                if '"' in item:
                    parts = re.split(r"""("[^"]*"|'[^']*')""", item) # remove spaces outside quotes
                    parts[::2] = map(lambda s: "".join(s.split()), parts[::2])
                    newList.append("".join(parts))
                else:
                    item = item.replace(" ","")
                    newList.append('"{0}"'.format(item))
            extractedList = ",".join(newList)
            new = "[{0}]".format(extractedList)
            listDict[original] = new

        for k,v in listDict.iteritems():
            where = where.replace(k,v)

    order = order.replace("cases.","")
    order = order.replace("files.","")
    retval1 = returns[rtype] # actual RETURN portion of statement
    where = convert_portal_to_neo4j(where)

    if rtype in ["cases","files"]: # pagination handling needed for these returns
        order = order.split(":")
        if start != 0:
            start = start-1
        retval2 = "ORDER BY {0} {1} SKIP {2} LIMIT {3}".format(order[0],order[1].upper(),start,size)
        if size == 0: # accounting for inconsistency where front-end asks for a 0 size return
            retval2 = "ORDER BY {0} {1}".format(order[0],order[1].upper())
        return "{0} WHERE {1} {2} {3}".format(match,where,retval1,retval2)
    else:
        return "{0} WHERE {1} {2}".format(match,where,retval1)
