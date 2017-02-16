import re, os, sys, socket
import graphene
from conf import neo4j_ip, neo4j_bolt, neo4j_http, neo4j_un, neo4j_pw
from py2neo import Graph ***REMOVED***Using py2neo v3 not v2
from query import match, build_cypher, build_adv_cypher, convert_gdc_to_osdf

###################
***REMOVED***DEFINING MODELS #
###################

***REMOVED***This section will contain all the necessary models needed to populate the schema

class Project(graphene.ObjectType): ***REMOVED***Graphene object for node
    projectId = graphene.String(name="project_id")
    primarySite = graphene.String(name="primary_site")
    name = graphene.String()
    studyName = graphene.String(name="study_name")
    studyFullName = graphene.String(name="study_full_name")

class Pagination(graphene.ObjectType): ***REMOVED***GDC expects pagination data for populating table
    count = graphene.Int()
    sort = graphene.String()
    fromNum = graphene.Int(name="from")
    page = graphene.Int()
    total = graphene.Int()
    pages = graphene.Int()
    size = graphene.Int()

class CaseHits(graphene.ObjectType): ***REMOVED***GDC defines hits as matching Project node + Case ID (in our case sample ID)
    project = graphene.Field(Project)
    caseId = graphene.String(name="case_id")

class IndivFiles(graphene.ObjectType): ***REMOVED***individual files to populate all files list
    dataType = graphene.String(name="data_type")
    fileName = graphene.String(name="file_name")
    dataFormat = graphene.String(name="data_format")
    access = graphene.String() ***REMOVED***only exists for consistency with GDC
    fileId = graphene.String(name="file_id")
    fileSize = graphene.Int(name="file_size")

class Analysis(graphene.ObjectType):
    updatedDatetime = graphene.String(name="updated_datetime")
    workflowType = graphene.String(name="workflow_type")
    analysisId = graphene.String(name="analysis_id")
    inputFiles = graphene.List(IndivFiles, name="input_files")

class AssociatedEntities(graphene.ObjectType):
    entityId = graphene.String(name="entity_id")
    caseId = graphene.String(name="case_id")
    entityType = graphene.String(name="entity_type")

class FileHits(graphene.ObjectType): ***REMOVED***GDC defined file hits for data type, file name, data format, and more
    dataType = graphene.String(name="data_type")
    fileName = graphene.String(name="file_name")
    md5sum = graphene.String()
    dataFormat = graphene.String(name="data_format")
    submitterId = graphene.String(name="submitter_id")
    state = graphene.String()
    access = graphene.String()
    fileId = graphene.String(name="file_id")
    dataCategory = graphene.String(name="data_category")
    experimentalStrategy = graphene.String(name="experimental_strategy")
    fileSize = graphene.Float(name="file_size")
    cases = graphene.List(CaseHits)
    associatedEntities = graphene.List(AssociatedEntities, name="associated_entities")
    analysis = graphene.Field(Analysis)

class Bucket(graphene.ObjectType): ***REMOVED***Each bucket is a distinct property in the node group
    key = graphene.String()
    docCount = graphene.Int(name="doc_count")

class BucketCounter(graphene.ObjectType): ***REMOVED***List of Buckets
    buckets = graphene.List(Bucket)

class Aggregations(graphene.ObjectType): ***REMOVED***Collecting lists of buckets (BucketCounter)
    ***REMOVED***Note that many of the "name" values are identical to the variable assigned to,
    ***REMOVED***but all are explicitly named for clarity and to match syntax of more complex names
    Project_name = graphene.Field(BucketCounter, name="Project_name")

    Study_subtype = graphene.Field(BucketCounter, name="Study_subtype")
    Study_center = graphene.Field(BucketCounter, name="Study_center")
    Study_name = graphene.Field(BucketCounter, name="Study_name")

    Subject_gender = graphene.Field(BucketCounter, name="Subject_gender")
    Subject_race = graphene.Field(BucketCounter, name="Subject_race")

    Visit_number = graphene.Field(BucketCounter, name="Visit_number")
    Visit_interval = graphene.Field(BucketCounter, name="Visit_interval")
    Visit_date = graphene.Field(BucketCounter, name="Visit_date")

    Sample_bodyproduct = graphene.Field(BucketCounter, name="Sample_body_product")
    Sample_fmabodysite = graphene.Field(BucketCounter, name="Sample_fma_body_site")
    Sample_geolocname = graphene.Field(BucketCounter, name="Sample_geo_loc_name")
    Sample_sampcollectdevice = graphene.Field(BucketCounter, name="Sample_samp_collect_device")
    Sample_envpackage = graphene.Field(BucketCounter, name="Sample_env_package")
    Sample_supersite = graphene.Field(BucketCounter, name="Sample_supersite")
    Sample_feature = graphene.Field(BucketCounter, name="Sample_feature")
    Sample_material = graphene.Field(BucketCounter, name="Sample_material")
    Sample_biome = graphene.Field(BucketCounter, name="Sample_biome")
    Sample_id = graphene.Field(BucketCounter, name="Sample_id")
    
    File_id = graphene.Field(BucketCounter, name="File_id")
    File_format = graphene.Field(BucketCounter, name="File_format")
    File_node_type = graphene.Field(BucketCounter, name="File_node_type")

    dataType = graphene.Field(BucketCounter, name="data_type")
    dataFormat = graphene.Field(BucketCounter, name="data_format")

class SBucket(graphene.ObjectType): ***REMOVED***Same idea as early bucket but used for summation (pie charts)
    key = graphene.String()
    docCount = graphene.Int(name="doc_count")
    caseCount = graphene.Int(name="case_count")
    fileSize = graphene.Float(name="file_size")

class SBucketCounter(graphene.ObjectType): ***REMOVED***List of SBuckets
    buckets = graphene.List(SBucket)

class FileSize(graphene.ObjectType): ***REMOVED***total aggregate file size of current set of chosen data
    value = graphene.Float()


####################################
***REMOVED***FUNCTIONS FOR GETTING NEO4J DATA #
####################################

***REMOVED***Get all these values from the conf
neo4j_bolt = int(neo4j_bolt)
neo4j_http = int(neo4j_http)

***REMOVED***This section will have all the logic for populating the actual data in the schema (data from Neo4j)
graph = Graph(host=neo4j_ip,bolt_port=neo4j_bolt,http_port=neo4j_http,user=neo4j_un,password=neo4j_pw)

***REMOVED***Base Cypher for traversing the entirety of the schema
full_traversal = ("MATCH (Project:Case{node_type:'project'})"
    "<-[:PART_OF]-(Study:Case{node_type:'study'})"
    "<-[:PARTICIPATES_IN]-(Subject:Case{node_type:'subject'})"
    "<-[:BY]-(Visit:Case{node_type:'visit'})"
    "<-[:COLLECTED_DURING]-(Sample:Case{node_type:'sample'})"
    "<-[:PREPARED_FROM]-(pf)"
    "<-[:SHORTCUT]-(File)"
)

***REMOVED***Function to extract a file name and an HTTP URL given values from a urls property from an OSDF node
def extract_url(urls_node):
    fn = ""
    if 'http' in urls_node:
        fn = urls_node['http']
    elif 'fasp' in urls_node:
        fn = urls_node['fasp']
        ***REMOVED***Do a replacement to just output http
        fn = fn.replace("fasp://aspera","http://downloads")
    elif 'ftp' in urls_node:
        fn = urls_node['ftp']
    elif 's3' in urls_node:
        fn = urls_node['s3']
    else:
        fn = "No File Found."
    return fn

***REMOVED***Function to get file size from Neo4j. 
***REMOVED***This current iteration should catch all the file data types EXCEPT for the *omes and the multi-step/repeat
***REMOVED***edges like the two "computed_from" edges between abundance matrix and 16s_raw_seq_set. Should be
***REMOVED***rather easy to accommodate these oddities once they're loaded and I can test.
def get_total_file_size(cy):
    cquery = ""
    if cy == "":
        cquery = "MATCH (File) WHERE NOT File.node_type=~'.*prep' RETURN SUM(toInt(File.size)) AS tot"
    elif '"op"' in cy:
        cquery = build_cypher(match,cy,"null","null","null","size")
    else:
        cquery = build_adv_cypher(match,cy,"null","null","null","size")
    res = graph.data(cquery)
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
            cquery = "MATCH (n:Case {node_type:'sample'}) RETURN count(n) AS tot"
        else:
            cquery = "MATCH (n:File) WHERE NOT n.node_type=~'.*prep' RETURN count(n) AS tot"
        res = graph.data(cquery)
        calcs = pagination_calcs(res[0]['tot'],f,size,c_or_f)
        return Pagination(count=calcs[2], sort=calcs[4], fromNum=f, page=calcs[1], total=calcs[3], pages=calcs[0], size=size)
    else:
        if '"op"' in cy:
            if c_or_f == 'c':
                cquery = build_cypher(match,cy,"null","null","null","c_pagination")
            else:
                cquery = build_cypher(match,cy,"null","null","null","f_pagination")
        else:
            if c_or_f == 'c':
                cquery = build_adv_cypher(match,cy,"null","null","null","c_pagination")
            else:
                cquery = build_adv_cypher(match,cy,"null","null","null","f_pagination")
        res = graph.data(cquery)
        calcs = pagination_calcs(res[0]['tot'],f,size,c_or_f)
        return Pagination(count=calcs[2], sort=calcs[4], fromNum=f, page=calcs[1], total=calcs[3], pages=calcs[0], size=size)

***REMOVED***Function to build and run a basic Cypher query. Accepts the following parameters:
***REMOVED***attr = property to match against, val = desired value of the property of attr,
***REMOVED***links = an array with two elements [name of node to hit, name of edge].
***REMOVED***For example, for Study object you want to use the following parameters:
***REMOVED***buildQuery("node_type", "Study", ["Project","PART_OF"])
***REMOVED***Note that this is a single-step query meaning 2 nodes and 1 edge
def build_basic_query(attr, val, links):
    if links:
        node = links[0] ***REMOVED***parse links array as described earlier, don't need attr
        edge = links[1]
        ***REMOVED***Note that collecting distinct nodes connected by the edge doesn't help much
        ***REMOVED***since each unique originating node comes paired with a link. Thus, check for
        ***REMOVED***unique-ness when appending to lists in the get_* functions below
        cquery = "MATCH (a:%s)<-[:%s]-(b:%s) RETURN a.name AS link, b" % (node, edge, val)
        return graph.data(cquery)
    else:
        cquery = "MATCH (n {%s: '%s'}) RETURN n" % (attr, val)
        return graph.data(cquery)

***REMOVED***Retrieve ALL files associated with a given Subject ID.
def get_files(sample_id):
    fl = []
    dt, fn, df, ac, fi = ("" for i in range(5))
    fs = 0
    
    cquery = ("MATCH (Sample:Case{node_type:'sample'})"
        "<-[:PREPARED_FROM]-(p)<-[:SHORTCUT]-(File) "
        "WHERE Sample.id=\"%s\" RETURN File"
        ) 
    cquery = cquery % (sample_id)
    res = graph.data(cquery)

    for x in range(0,len(res)): ***REMOVED***iterate over each unique path
        dt = res[x]['File']['subtype']
        df = res[x]['File']['format']
        ac = "open" ***REMOVED***need to change this once a new private/public property is added to OSDF
        fs = res[x]['File']['size']
        fi = res[x]['File']['id']
        fn = extract_url(res[x]['File'])
        fl.append(IndivFiles(dataType=dt,fileName=fn,dataFormat=df,access=ac,fileId=fi,fileSize=fs))

    return fl

***REMOVED***Query to traverse top half of OSDF model (Project<-....-Sample). 
def get_proj_data(sample_id):
    cquery = ("MATCH (Project:Case{node_type:'project'})"
        "<-[:PART_OF]-(Study:Case{node_type:'study'})"
        "<-[:PARTICIPATES_IN]-(Subject:Case{node_type:'subject'})"
        "<-[:BY]-(Visit:Case{node_type:'visit'})"
        "<-[:COLLECTED_DURING]-(Sample:Case{node_type:'sample'}) WHERE Sample.id=\"%s\" RETURN Project"
        ) 
    cquery = cquery % (sample_id)
    res = graph.data(cquery)
    return Project(name=res[0]['Project']['name'],projectId=res[0]['Project']['subtype'])

def get_all_proj_data():
    cquery = "MATCH (n:Case{node_type:'study'}) RETURN DISTINCT n"
    res = graph.data(cquery)
    return res

def get_all_study_data():
    cquery = ("MATCH (Project:Case{node_type:'project'})"
        "<-[:PART_OF]-(Study:Case{node_type:'study'})"
        "<-[:PARTICIPATES_IN]-(Subject:Case{node_type:'subject'})"
        "<-[:BY]-(Visit:Case{node_type:'visit'})"
        "<-[:COLLECTED_DURING]-(Sample:Case{node_type:'sample'})"
        "<-[:PREPARED_FROM]-(pf)"
        "<-[:SHORTCUT]-(File)"
        " RETURN DISTINCT Study.name, Project.subtype, Study.full_name, COUNT(DISTINCT Sample) as case_count, (COUNT(DISTINCT File)) as file_count"
        )
    res = graph.data(cquery)
    return res

***REMOVED***This function is a bit unique as it's only called to populate the bar chart on the home page
def get_all_proj_counts():
    cquery = ("MATCH (Project:Case{node_type:'project'})"
        "<-[:PART_OF]-(Study:Case{node_type:'study'})"
        "<-[:PARTICIPATES_IN]-(Subject:Case{node_type:'subject'})"
        "<-[:BY]-(Visit:Case{node_type:'visit'})"
        "<-[:COLLECTED_DURING]-(Sample:Case{node_type:'sample'})"
        "<-[:PREPARED_FROM]-(pf)"
        "<-[:SHORTCUT]-(File)"
        " RETURN DISTINCT Study.id, Study.name, Sample.fma_body_site, COUNT(DISTINCT Sample) as case_count, (COUNT(DISTINCT File)) as file_count"
        )
    res = graph.data(cquery)
    return res

***REMOVED***This populates the values in the side table of facet search. Want to let users
***REMOVED***know how many samples per category in a given property. 
count_props_dict = {
    "project": "MATCH (n:Case{node_type:'project'})<-[:PART_OF]-(study)<-[:PARTICIPATES_IN]-(subject)<-[:BY]-(visit)<-[:COLLECTED_DURING]-(sample)<-[:PREPARED_FROM]-(pf)<-[:SHORTCUT]-(File) WITH DISTINCT n,sample RETURN n.%s AS prop, count(sample) as counts",
    "study": "MATCH (n:Case{node_type:'study'})<-[:PARTICIPATES_IN]-(subject)<-[:BY]-(visit)<-[:COLLECTED_DURING]-(sample)<-[:PREPARED_FROM]-(pf)<-[:SHORTCUT]-(File) WITH DISTINCT n,sample RETURN n.%s AS prop, count(sample) as counts",
    "subject": "MATCH (n:Case{node_type:'subject'})<-[:BY]-(visit)<-[:COLLECTED_DURING]-(sample)<-[:PREPARED_FROM]-(pf)<-[:SHORTCUT]-(File) WITH DISTINCT n,sample RETURN n.%s AS prop, count(sample) as counts",
    "visit": "MATCH (n:Case{node_type:'visit'})<-[:COLLECTED_DURING]-(sample)<-[:PREPARED_FROM]-(pf)<-[:SHORTCUT]-(File) WITH DISTINCT n,sample RETURN n.%s AS prop, count(sample) as counts",
}

***REMOVED***Cypher query to count the amount of each distinct property
def count_props(node, prop, cy):
    cquery = ""
    if cy == "":
        if node in count_props_dict:
            cquery = count_props_dict[node] % (prop)
        elif node == 'sample':
            cquery = "MATCH (n:Case{node_type:'sample'})<-[:PREPARED_FROM]-(pf)<-[:SHORTCUT]-(File) WITH DISTINCT n RETURN n.%s AS prop, COUNT(n.%s) as counts" % (prop,prop)
        else:
            cquery = "Match (n:File) WHERE NOT n.node_type=~'.*prep' RETURN n.%s as prop, count(n.%s) as counts" % (prop, prop)
    else:
        cquery = build_cypher(match,cy,"null","null","null",prop)
    return graph.data(cquery)

***REMOVED***Cypher query to count the amount of each distinct property
def count_props_and_files(node, prop, cy):

    cquery,with_distinct = ("" for i in range (2))
    
    if cy == "":
        retval = ("WITH (COUNT(DISTINCT(Sample))) as ccounts, "
            "COUNT(DISTINCT(File)) AS dcounts, %s.%s AS prop, "
            "collect(DISTINCT File) AS f UNWIND f AS fs "
            "RETURN prop,ccounts,dcounts,SUM(toInt(fs.size)) as tot"
            )

        mod_retval = retval % (node,prop)
        cquery = "%s %s" % (full_traversal,mod_retval)

    else:
        if node == 'Study' and prop == 'name':
            prop = 'sname'

        prop_detailed = "%s_detailed" % (prop)
        if "op" in cy:
            cquery = build_cypher(match,cy,"null","null","null",prop_detailed)
        else:
            cquery = build_adv_cypher(match,cy,"null","null","null",prop_detailed)

    return graph.data(cquery)

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
        retval = "RETURN DISTINCT Project.name,Study.name,Study.full_name,Sample.id,Project.subtype,Sample.fma_body_site ORDER BY %s %s SKIP %s LIMIT %s"
        cquery = "%s %s" % (full_traversal,retval)
        if f != 0:
            f = f-1
        cquery = cquery % (order[0],order[1].upper(),f,size)
    elif '"op"' in cy:
        cquery = build_cypher(match,cy,order,f,size,"cases")
    else:
        cquery = build_adv_cypher(match,cy,order,f,size,"cases")
    res = graph.data(cquery)
    for x in range(0,len(res)):
        cur = CaseHits(project=Project(projectId=res[x]['Project.subtype'],primarySite=res[x]['Sample.fma_body_site'],name=res[x]['Project.name'],studyName=res[x]['Study.name'],studyFullName=res[x]['Study.full_name']),caseId=res[x]['Sample.id'])
        hits.append(cur)
    return hits

***REMOVED***Function to return file values to populate the table.
def get_file_hits(size,order,f,cy):
    hits = []
    cquery = ""
    if cy == "":
        order = order.split(":")
        retval = "RETURN DISTINCT Project,File,Sample.id ORDER BY %s %s SKIP %s LIMIT %s"
        cquery = "%s %s" % (full_traversal,retval)
        if f != 0:
            f = f-1
        cquery = cquery % (order[0],order[1].upper(),f,size)
    elif '"op"' in cy:
        cquery = build_cypher(match,cy,order,f,size,"files")
    else:
        cquery = build_adv_cypher(match,cy,order,f,size,"files")
    res = graph.data(cquery)
    for x in range(0,len(res)):
        case_hits = [] ***REMOVED***reinit each iteration
        cur_case = CaseHits(project=Project(projectId=res[x]['Project']['subtype'],name=res[x]['Project']['name']),caseId=res[x]['Sample.id'])
        case_hits.append(cur_case)
        furl = extract_url(res[x]['File']) ***REMOVED***File name is our URL
        if '.hmpdacc' in furl: ***REMOVED***HMP endpoint
            furl = re.search(r'/data/(.*)',furl).group(1)
        elif '.ihmpdcc':
            furl = re.search(r'.org/(.*)',furl).group(1)
        cur_file = FileHits(dataType=res[x]['File']['subtype'],fileName=furl,dataFormat=res[x]['File']['format'],submitterId="null",access="open",state="submitted",fileId=res[x]['File']['id'],dataCategory=res[x]['File']['node_type'],experimentalStrategy=res[x]['File']['subtype'],fileSize=res[x]['File']['size'],cases=case_hits)
        hits.append(cur_file)    
    return hits

***REMOVED***Pull all the data associated with a particular file ID. 
def get_file_data(file_id):
    cl, al, fl = ([] for i in range(3))
    retval = "WHERE File.id=\"%s\" RETURN Project,Subject,Sample,pf,File"
    cquery = "%s %s" % (full_traversal,retval)
    cquery = cquery % (file_id)
    res = graph.data(cquery)
    furl = extract_url(res[0]['File']) 
    sample_bs = res[0]['Sample']['fma_body_site']
    wf = "%s -> %s" % (sample_bs,res[0]['pf']['node_type'])
    cl.append(CaseHits(project=Project(projectId=res[0]['Project']['subtype']),caseId=res[0]['Subject']['id']))
    al.append(AssociatedEntities(entityId=res[0]['pf']['id'],caseId=res[0]['Sample']['id'],entityType=res[0]['pf']['node_type']))
    fl.append(IndivFiles(fileId=res[0]['File']['id']))
    a = Analysis(updatedDatetime="null",workflowType=wf,analysisId="null",inputFiles=fl) ***REMOVED***can add analysis ID once node is present or remove if deemed unnecessary
    return FileHits(dataType=res[0]['File']['node_type'],fileName=furl,md5sum=res[0]['File']['checksums'],dataFormat=res[0]['File']['format'],submitterId="null",state="submitted",access="open",fileId=res[0]['File']['id'],dataCategory=res[0]['File']['node_type'],experimentalStrategy=res[0]['File']['study'],fileSize=res[0]['File']['size'],cases=cl,associatedEntities=al,analysis=a)

def get_url_for_download(id):
    cquery = "MATCH (n:File) WHERE n.id=\"%s\" AND NOT n.node_type=~'.*prep' RETURN n" % (id)
    res = graph.data(cquery)
    return extract_url(res[0]['n'])

def get_manifest_data(id_list):

    ids = ""
    mod_list = []

    ***REMOVED***Surround each value with quotes for Neo4j comparison
    for id in id_list:
        mod_list.append("'%s'" % (id))
    ***REMOVED***Separate by commas to make a Neo4j list
    if len(mod_list) > 1:
        ids = ",".join(mod_list)
    else: ***REMOVED***just a single ID
        ids = mod_list[0]

    ***REMOVED***Surround in brackets to format list syntax
    ids = "[%s]" % ids
    cquery = "MATCH (n:File) WHERE n.id IN %s RETURN n" % ids
    res = graph.data(cquery)

    outlist = []

    ***REMOVED***Grab the ID, file URL, md5, and size
    for entry in res:
        id = entry['n']['id']
        url = extract_url(entry['n'])
        md5 = entry['n']['md5']
        size = entry['n']['size']
        outlist.append("\n%s\t%s\t%s\t%s" % (id,url,md5,size))

    return outlist
