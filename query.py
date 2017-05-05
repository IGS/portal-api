import re, json, requests, hashlib
import ujson
from py2neo import Graph ***REMOVED***Using py2neo v3 not v2
from conf import neo4j_ip, neo4j_bolt, neo4j_http, neo4j_un, neo4j_pw
from models import Project,Pagination,CaseHits,IndivFiles,Analysis,AssociatedEntities
from models import FileHits,Bucket,BucketCounter,Aggregations,SBucket,SBucketCounter,FileSize

***REMOVED***The match var is the base query to prepend all queries. The idea is to traverse
***REMOVED***the graph entirely and use filters to return a subset of the total traversal. 
***REMOVED***PSS = Project/Study/Subject
***REMOVED***VS = Visit/Sample
***REMOVED***File = File
full_traversal = "MATCH (PSS:subject)<-[:extracted_from]-(VS:sample)<-[:derived_from]-(F:file) "

***REMOVED***If the following return ends in "counts", then it is for a pie chart. The first two are for
***REMOVED***cases/files tabs and the last is for the total size. 
#
***REMOVED***All of these returns are pre-pended with "WITH DISTINCT File.*". This is because there is 
***REMOVED***some redundancy in the HMP data in that some nodes are iterated over multiple times. In order 
***REMOVED***to get around this, need to just return each file that is seen only once and bundle any of the
***REMOVED***other nodes alongside this single file. Meaning, "WITH DISTINCT File,Project" and only returning
***REMOVED***aspects of 'Project' like Project.name or something is only counted once along a given path to a 
***REMOVED***particular file. Note that each one has a fairly unique "WITH DISTINCT" clause, this is to help
***REMOVED***optimize the query and ensure the distinct check is as simple as the return allows it to be.

***REMOVED***The detailed queries require specifics about both sample and file counts to be 
***REMOVED***returned so they require some extra handling. 
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

***REMOVED***This populates the values in the side table of facet search. Want to let users
***REMOVED***know how many samples per category in a given property. 
count_props_dict = {
    "PSS": "MATCH (n:subject)<-[:extracted_from]-(VS:sample)<-[:derived_from]-(F:file) RETURN n.{0} AS prop, COUNT(DISTINCT(VS)) as counts",
    "VS": "MATCH (PSS:subject)<-[:extracted_from]-(n:sample)<-[:derived_from]-(F:file) RETURN n.{0} AS prop, COUNT(DISTINCT(n)) as counts",
    "F": "MATCH (PSS:subject)<-[:extracted_from]-(VS:sample)<-[:derived_from]-(n:file) RETURN n.{0} AS prop, COUNT(DISTINCT(VS)) as counts"
}

####################################
***REMOVED***FUNCTIONS FOR GETTING NEO4J DATA #
####################################

***REMOVED***Get all these values from the conf
neo4j_bolt = int(neo4j_bolt)
neo4j_http = int(neo4j_http)

***REMOVED***This section will have all the logic for populating the actual data in the schema (data from Neo4j)
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

***REMOVED***Function to extract a file name and an HTTP URL given values from a urls 
***REMOVED***property from an OSDF node. Note that this prioritizes http>fasp>ftp>s3
***REMOVED***and that it only returns a single one of the endpoints. This is in an effort
***REMOVED***to communicate a base URL in the result tables in the portal. 
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

***REMOVED***Function to return all present URLs for the manifest file
def extract_manifest_urls(urls_node):

    urls = []

    ***REMOVED***Note that these are all individual ifs in order to grab all endpoints present
    if 'http' in urls_node:
        urls.append(urls_node['http'])
    if 'fasp' in urls_node:
        urls.append(urls_node['fasp'])
    if 'ftp' in urls_node:
        urls.append(urls_node['ftp'])
    if 's3' in urls_node:
        urls.append(urls_node['s3'])

    if len(urls) == 0: ***REMOVED***if here, there is no downloadable file
        urls.append('private: Data not accessible via the HMP DACC.')

    return ",".join(urls)

***REMOVED***Function to get file size from Neo4j. 
***REMOVED***This current iteration should catch all the file data types EXCEPT for the *omes and the multi-step/repeat
***REMOVED***edges like the two "computed_from" edges between abundance matrix and 16s_raw_seq_set. Should be
***REMOVED***rather easy to accommodate these oddities once they're loaded and I can test.
def get_total_file_size(cy):
    cquery = ""
    if cy == "":
        cquery = "MATCH (F:file) RETURN SUM(toInt(F.size)) AS tot"
    elif '"op"' in cy:
        cquery = build_cypher(full_traversal,cy,"null","null","null","size")
    else:
        cquery = build_adv_cypher(full_traversal,cy,"null","null","null","size")
    res = process_cquery_http(cquery)
    return res[0]['tot']

***REMOVED***Function for pagination calculations. Find the page, number of pages, and number of entries on a single page.
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
    if (start+size) < tot: ***REMOVED***less than full page, count must be page size
        cnt = size
    else: ***REMOVED***if less than a full page (only possible on last page), find the difference
        cnt = tot-start
    pagcalcs = []
    pagcalcs.append(pgs)
    pagcalcs.append(pg)
    pagcalcs.append(cnt)
    pagcalcs.append(tot)
    pagcalcs.append(sort)
    return pagcalcs

***REMOVED***Function to determine how pagination is to work for the cases/files tabs. This will 
***REMOVED***take a Cypher query and a given table size and determine how many pages are needed
***REMOVED***to display all this data. 
***REMOVED***cy = Cypher filters/ops
***REMOVED***size = size of each page
***REMOVED***f = from/start position
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
            else:
                cquery = build_adv_cypher(full_traversal,cy,"null","null","null","f_pagination")
        res = process_cquery_http(cquery)
        calcs = pagination_calcs(res[0]['tot'],f,size,c_or_f)
        return Pagination(count=calcs[2], sort=calcs[4], fromNum=f, page=calcs[1], total=calcs[3], pages=calcs[0], size=size)

***REMOVED***Retrieve ALL files associated with a given Subject ID.
def get_files(sample_id):
    fl = []
    dt, fn, df, ac, fi = ("" for i in range(5))
    fs = 0
    
    cquery = "{0} WHERE VS.id='{1}' RETURN F".format(full_traversal,sample_id)
    res = process_cquery_http(cquery)

    for x in range(0,len(res)): ***REMOVED***iterate over each unique path
        dt = res[x]['F']['subtype']
        df = res[x]['F']['format']
        ac = "open" ***REMOVED***need to change this once a new private/public property is added to OSDF
        fs = res[x]['F']['size']
        fi = res[x]['F']['id']
        fn = extract_url(res[x]['F'])
        fl.append(IndivFiles(dataType=dt,fileName=fn,dataFormat=df,access=ac,fileId=fi,fileSize=fs))

    return fl

***REMOVED***Query to traverse top half of OSDF model (Project<-....-Sample). 
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

***REMOVED***This function is a bit unique as it's only called to populate the bar chart on the home page
def get_all_proj_counts():
    cquery = "{0} RETURN DISTINCT PSS.study_id, PSS.study_name, VS.body_site, COUNT(DISTINCT(VS)) as case_count, COUNT(F) as file_count".format(full_traversal)
    return process_cquery_http(cquery)

***REMOVED***Cypher query to count the amount of each distinct property
def count_props(node, prop, cy):
    cquery = ""
    if cy == "":
        cquery = count_props_dict[node].format(prop)
    else:
        cquery = build_cypher(full_traversal,cy,"null","null","null",prop)
    return process_cquery_http(cquery)

***REMOVED***Cypher query to count the amount of each distinct property
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

    return process_cquery_http(cquery)

***REMOVED***Formats the values from count_props & count_props_and_files functions above into GQL
def get_buckets(inp,sum, cy):

    splits = inp.split('.') ***REMOVED***parse for node/prop values to be counted by
    node = splits[0]
    prop = splits[1]
    bucketl,sortl = ([] for i in range(2)) ***REMOVED***need two lists to sort these buckets by size

    if sum == "no": ***REMOVED***not a full summary, just key and doc count need to be returned
        res = count_props(node, prop, cy)
        for x in range(0,len(res)):
            if res[x]['prop'] != "":
                cur = Bucket(key=res[x]['prop'], docCount=res[x]['counts'])
                sortl.append(int(res[x]['counts']))
                bucketl.append(cur)

        return BucketCounter(buckets=[bucket for(sort,bucket) in sorted(zip(sortl,bucketl),reverse=True)])

    else: ***REMOVED***return full summary including case_count, doc_count, file_size, and key
        res = count_props_and_files(node, prop, cy)
        for x in range(0,len(res)):
            if res[x]['prop'] != "":
                cur = SBucket(key=res[x]['prop'], docCount=res[x]['dcounts'], fileSize=res[x]['tot'], caseCount=res[x]['ccounts'])
                bucketl.append(cur)

        return SBucketCounter(buckets=bucketl)

***REMOVED***Function to return case values to populate the table, note that this will just return first 25 values arbitrarily for the moment
***REMOVED***size = number of hits to return
***REMOVED***order = what to ORDER BY in Cypher clause
***REMOVED***f = position to star the return 'f'rom based on the ordering (python prevents using that word)
***REMOVED***cy = filters/op sent from GDC portal
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

    res = process_cquery_http(cquery)

    for x in range(0,len(res)):
        cur = CaseHits(project=Project(projectId=res[x]['PSS']['project_subtype'],primarySite=res[x]['VS']['body_site'],name=res[x]['PSS']['project_name'],studyName=res[x]['PSS']['study_name'],studyFullName=res[x]['PSS']['study_name']),caseId=res[x]['VS']['id'])
        hits.append(cur)
    return hits

***REMOVED***Function to return file values to populate the table.
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

    res = process_cquery_http(cquery)

    for x in range(0,len(res)):
        case_hits = [] ***REMOVED***reinit each iteration
        cur_case = CaseHits(project=Project(projectId=res[x]['PSS']['project_subtype'],name=res[x]['PSS']['project_name']),caseId=res[x]['VS']['id'])
        case_hits.append(cur_case)

        furl = extract_url(res[x]['F']) ***REMOVED***File name is our URL
        if '.hmpdacc' in furl and '/data/' in furl: ***REMOVED***HMP endpoint
            furl = re.search(r'/data/(.*)',furl).group(1)
        elif '.ihmpdcc' in furl and 'org/' in furl:
            furl = re.search(r'\.org/(.*)',furl).group(1)

        ***REMOVED***Should try handle this at an earlier phase, but make sure size exists
        if 'size' not in res[x]['F']:
            res[x]['F']['size'] = 0

        cur_file = FileHits(dataType=res[x]['F']['subtype'],fileName=furl,dataFormat=res[x]['F']['format'],submitterId="null",access="open",state="submitted",fileId=res[x]['F']['id'],dataCategory=res[x]['F']['node_type'],experimentalStrategy=res[x]['F']['subtype'],fileSize=res[x]['F']['size'],cases=case_hits)

        hits.append(cur_file)    
    return hits

***REMOVED***Pull all the data associated with a particular file ID. 
def get_file_data(file_id):
    cl, al, fl = ([] for i in range(3))
    retval = "WHERE F.id='{0}' RETURN PSS,VS,F".format(file_id)
    cquery = "{0} {1}".format(full_traversal,retval)
    res = process_cquery_http(cquery)
    furl = extract_url(res[0]['F']) 
    sample_bs = res[0]['VS.body_site']
    wf = "{0} -> {1}".format(sample_bs,res[0]['F.prep_node_type'])
    cl.append(CaseHits(project=Project(projectId=res[0]['PSS.project_subtype']),caseId=res[0]['VS.id']))
    al.append(AssociatedEntities(entityId=res[0]['F.prep_id'],caseId=res[0]['VS.id'],entityType=res[0]['F.prep_node_type']))
    fl.append(IndivFiles(fileId=res[0]['F.id']))
    a = Analysis(updatedDatetime="null",workflowType=wf,analysisId="null",inputFiles=fl) ***REMOVED***can add analysis ID once node is present or remove if deemed unnecessary
    return FileHits(dataType=res[0]['F.node_type'],fileName=furl,md5sum=res[0]['F.md5'],dataFormat=res[0]['F.format'],submitterId="null",state="submitted",access="open",fileId=res[0]['F.id'],dataCategory=res[0]['F.node_type'],experimentalStrategy=res[0]['F.study'],fileSize=res[0]['F.size'],cases=cl,associatedEntities=al,analysis=a)

def get_url_for_download(id):
    cquery = "MATCH (F:file) WHERE F.id='{0}' RETURN F".format(id)
    res = process_cquery_http(cquery)
    return extract_url(res[0]['F'])

***REMOVED***Function to place a list into a string format that Neo4j understands
def build_neo4j_list(id_list):

    ids = ""
    mod_list = []
    
    ***REMOVED***Surround each value with quotes for Neo4j comparison
    for id in id_list:
        mod_list.append("'{0}'".format(id))
    ***REMOVED***Separate by commas to make a Neo4j list
    if len(mod_list) > 1:
        ids = ",".join(mod_list)
    else: ***REMOVED***just a single ID
        ids = mod_list[0]

    return ids

def get_manifest_data(id_list):

    ids = build_neo4j_list(id_list)

    ***REMOVED***Surround in brackets to format list syntax
    ids = "[{0}]".format(ids)
    cquery = "MATCH (F:file) WHERE F.id IN {0} RETURN F".format(ids)
    res = process_cquery_http(cquery)

    outlist = []

    ***REMOVED***Grab the ID, file URL, md5, and size
    for entry in res:
        id = entry['F']['id']
        urls = extract_manifest_urls(entry['F'])
        md5 = entry['F']['md5']
        size = entry['F']['size']
        outlist.append("\n{0}\t{1}\t{2}\t{3}".format(id,md5,size,urls))

    return outlist

def get_manifest_token(id_list):

    id_list.sort() ***REMOVED***ensure no wonky ordering ruins the MD5 creation

    ids = build_neo4j_list(id_list)

    token = hashlib.md5(ids).hexdigest()
    ids = "[{0}]".format(ids)
    cquery = "MERGE (t:token{{id:'{0}',id_list:{1}}})".format(token,ids)
    res = process_cquery_http(cquery)

    return token

***REMOVED***Function to extract known GDC syntax and convert to OSDF. This is commonly needed for performing
***REMOVED***cypher queries while still being able to develop the front-end with the cases syntax.
def convert_gdc_to_osdf(inp_str):
    ***REMOVED***Errors in Graphene mapping prevent the syntax I want, so ProjectName is converted to 
    ***REMOVED***Cypher ready Project.name here (as are the other possible query parameters).
    inp_str = inp_str.replace("cases.ProjectName","PSS.project_name")
    inp_str = inp_str.replace("cases.SampleFmabodysite","VS.body_site")
    inp_str = inp_str.replace("cases.SubjectGender","PSS.gender")
    inp_str = inp_str.replace("project.primary_site","VS.body_site")
    inp_str = inp_str.replace("subject.gender","PSS.gender")
    inp_str = inp_str.replace("study.name","PSS.study_name")
    inp_str = inp_str.replace("file.format","F.format")
    inp_str = inp_str.replace("file.category","F.subtype") ***REMOVED***note the conversion
    inp_str = inp_str.replace("files.file_id","F.id")
    inp_str = inp_str.replace("cases.","") ***REMOVED***these replaces have to be catch alls to replace all instances throughout
    inp_str = inp_str.replace("file.","")
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

    ***REMOVED***Handle facet searches from panel on left side
    inp_str = inp_str.replace("data_type","F.node_type")
    inp_str = inp_str.replace("data_format","F.format")

    ***REMOVED***Next two lines guarantee URL encoding (seeing errors with urllib)
    inp_str = inp_str.replace('"','|')
    inp_str = inp_str.replace('\\','')
    inp_str = inp_str.replace(" ","%20")

    ***REMOVED***While the DB is to be set at read-only, in the case this toggle is 
    ***REMOVED***forgotten do some checks to make sure nothing fishy is happening.
    potentially_malicious = set([";"," delete "," create "," detach "," set ",
                                " return "," match "," merge "," where "," with ",
                                " import "," remove "," union "])
    check_str = inp_str.lower()
    for word in check_str:
        if word in potentially_malicious:
            break

    return inp_str

***REMOVED***This is a recursive function originally used to traverse and find the depth 
***REMOVED***of nested JSON. Now used to traverse the op/filters query from GDC and 
***REMOVED***ultimately aims to provide input to build the WHERE clause of a Cypher query. 
***REMOVED***Accepts input of json.loads parsed GDC portal query input and an empty array. 
***REMOVED***Note that this is currently only called when facet search is being performed.
def get_depth(x, arr):
    if type(x) is dict and x:
        if 'op' in x:
            arr.append(x['op'])
        if 'field' in x:
            left = x['field']
            right = x['value']
            if type(x['value']) is list:
                l = x['value']
                l = ["'{0}'".format(element) for element in l] ***REMOVED***need to add quotes around each element to make Cypher happy
                right = ",".join(l)
            else:
                right = "'{0}'".format(right) ***REMOVED***again, quotes for Cypher
            arr.append(left)
            arr.append(right)
        return max(get_depth(x[a], arr) for a in x)
    if type(x) is list and x: 
        return max(get_depth(a, arr) for a in x)
    return arr ***REMOVED***give the array back after traversal is complete

***REMOVED***Fxn to build Cypher based on facet search, accepts output from get_depth
def build_facet_where(inp): 
    facets = [] ***REMOVED***going to build an array of all the facets params present
    lstr, rstr = ("" for i in range(2))
    for x in reversed(range(0,len(inp))):
        if "'" in inp[x]: ***REMOVED***found the values to search for
            rstr = "[{0}]".format(inp[x]) ***REMOVED***add brackets for Cypher
        elif "." in inp[x]: ***REMOVED***found the fields to search on
            lstr = inp[x]
        elif "in" == inp[x]: ***REMOVED***found the comparison op, build the full string
            facets.append("{0} in {1}".format(lstr, rstr))
    return " AND ".join(facets) ***REMOVED***send back Cypher-ready WHERE clause

***REMOVED***Function to convert syntax from facet/advanced search pages and move it into 
***REMOVED***the new Neo4j schema's format. This is a step we likely cannot account for 
***REMOVED***on the portal itself as we want users to be able to do something like search
***REMOVED***for Project name as Project.name or something similar instead of PSS.project_name.
def convert_portal_to_neo4j(inp_str):
    inp_str = inp_str.replace("Project.","PSS.project_")
    return inp_str

***REMOVED***Final function needed to build the entirety of the Cypher query taken from facet search. Accepts the following:
***REMOVED***match = base MATCH query for Cypher
***REMOVED***whereFilters = filters string passed from GDC portal
***REMOVED***order = parameters to order results by (needed for pagination)
***REMOVED***start = index of sort to start at
***REMOVED***size = number of results to return
***REMOVED***rtype = return type, want to be able to hit this for both cases, files, and aggregation counts.
def build_cypher(match,whereFilters,order,start,size,rtype):
    arr = []
    q = json.loads(whereFilters) ***REMOVED***parse filters input into JSON (yields hashes of arrays)
    w1 = get_depth(q, arr) ***REMOVED***first step of building where clause is the array of individual comparison elements
    where = build_facet_where(w1)
    where = convert_portal_to_neo4j(where)
    where = where.replace("cases.","") ***REMOVED***trim the GDC syntax, hack until we refactor cases/files syntax
    where = where.replace("files.","")
    order = order.replace("cases.","")
    order = order.replace("files.","")
    retval1 = returns[rtype] ***REMOVED***actual RETURN portion of statement
    if rtype in ["cases","files"]: ***REMOVED***pagination handling needed for these returns
        order = order.split(":")

        ***REMOVED***When adding all files to cart, a special case happens where there is
        ***REMOVED***no order specified so have to return a more basic query.
        if len(order) < 2:
            return "{0} WHERE {1} {2}".format(match,where,retval1)

        if start != 0:
            start = start - 1
        retval2 = "ORDER BY {0} {1} SKIP {2} LIMIT {3}".format(order[0],order[1].upper(),start,size) 
        return "{0} WHERE {1} {2} {3}".format(match,where,retval1,retval2)
    else:
        return "{0} WHERE {1} {2}".format(match,where,retval1)

***REMOVED***First iteration, handling all regex individually
regexForNotEqual = re.compile(r"<>\s([0-9]*[a-zA-Z_]+[a-zA-Z0-9_]*)\b") ***REMOVED***only want to add quotes to anything that's not solely numbers
regexForEqual = re.compile(r"=\s([0-9]*[a-zA-Z_]+[a-zA-Z0-9_]*)\b") 
regexForIn = re.compile(r"(\[[a-zA-Z\'\"\s\,\(\)]+\])") ***REMOVED***catch anything that should be in a list

***REMOVED***This advanced Cypher builder expects the string generated by any of the advanced queries. 
***REMOVED***Parameters are described above before build_cypher()
def build_adv_cypher(match,whereFilters,order,start,size,rtype):
    where = whereFilters[10:len(whereFilters)-2] 
    where = where.replace("!=","<>")

    ***REMOVED***Add quotes that FE missed
    if '=' in where:
        where = regexForEqual.sub(r'= "\1"',where)
    if '<>' in where:
        where = regexForNotEqual.sub(r'<> "\1"',where)
    if ' in ' in where or ' IN ' in where: ***REMOVED***lists present, parse through and add quotes to all values without them
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
                    parts = re.split(r"""("[^"]*"|'[^']*')""", item) ***REMOVED***remove spaces outside quotes
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
    retval1 = returns[rtype] ***REMOVED***actual RETURN portion of statement
    where = convert_portal_to_neo4j(where)

    if rtype in ["cases","files"]: ***REMOVED***pagination handling needed for these returns
        order = order.split(":")
        if start != 0:
            start = start-1
        retval2 = "ORDER BY {0} {1} SKIP {2} LIMIT {3}".format(order[0],order[1].upper(),start,size)
        if size == 0: ***REMOVED***accounting for inconsistency where front-end asks for a 0 size return
            retval2 = "ORDER BY {0} {1}".format(order[0],order[1].upper())
        return "{0} WHERE {1} {2} {3}".format(match,where,retval1,retval2)
    else:
        return "{0} WHERE {1} {2}".format(match,where,retval1)
