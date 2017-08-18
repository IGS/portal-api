import re, json, requests, hashlib, time
import ujson, urllib
from collections import OrderedDict
from autocomplete_map import gql_map
from py2neo import Graph ***REMOVED***Using py2neo v3 not v2
from conf import neo4j_ip, neo4j_bolt, neo4j_http, neo4j_un, neo4j_pw
from models import Project,Pagination,CaseHits,IndivFiles,IndivSample,Analysis,AssociatedEntities
from models import FileHits,Bucket,BucketCounter,Aggregations,SBucket,SBucketCounter,FileSize,PieCharts

***REMOVED***The match var is the base query to prepend all queries. The idea is to traverse
***REMOVED***the graph entirely and use filters to return a subset of the total traversal. 
***REMOVED***PS = Project/Subject
***REMOVED***VSS = Visit/Sample/Study
***REMOVED***File = File
***REMOVED***D = derived from (contains prep data)
full_traversal = "MATCH (PS:subject)<-[:extracted_from]-(VSS:sample)<-[D:derived_from]-(F:file) "

tag_traversal = "MATCH (PS:subject)<-[:extracted_from]-(VSS:sample)<-[D:derived_from]-(F:file)-[:has_tag]->(T:tag) "

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
base_detailed_return = '''
    WITH COUNT(DISTINCT(VSS)) as scount, 
    COUNT(DISTINCT(F)) AS fcount, {0} AS prop, SUM(DISTINCT(F.size)) as tot 
    RETURN prop,scount,fcount,tot
'''

returns = {
    'cases': "RETURN DISTINCT PS, VSS",
    'files': "RETURN DISTINCT F",
    'project_name': "RETURN PS.project_name AS prop, count(PS.project_name) AS counts",
    'study_name': "RETURN VSS.study_name AS prop, count(VSS.study_name) AS counts",
    'body_site': "RETURN VSS.body_site AS prop, count(VSS.body_site) AS counts",
    'study': "RETURN VSS.study_name AS prop, count(VSS.study_name) AS counts",
    'gender': "RETURN PS.gender AS prop, count(PS.gender) AS counts",
    'race': "RETURN PS.race AS prop, count(PS.race) AS counts",
    'format': "WITH DISTINCT F RETURN F.format AS prop, count(F.format) AS counts",
    'node_type': "WITH DISTINCT F RETURN F.node_type AS prop, count(F.node_type) AS counts",
    'size': "WITH DISTINCT F RETURN SUM(F.size) AS tot",
    'f_pagination': "RETURN (count(DISTINCT(F))) AS tot",
    'c_pagination': "RETURN (count(DISTINCT(VSS.id))) AS tot",
    'project_name_detailed': base_detailed_return.format('PS.project_name'),
    'study_name_detailed': base_detailed_return.format('VSS.study_name'),
    'sample_body_site_detailed': base_detailed_return.format('VSS.body_site'), 
    'subject_gender_detailed': base_detailed_return.format('PS.gender'),
    'file_format_detailed': base_detailed_return.format('F.format'),
    'file_node_type_detailed': base_detailed_return.format('F.node_type')
}

***REMOVED***The loader missed some of these decimals/floats, convert here. Should fix
***REMOVED***in loader but leaving here due to time constraint. Need to ensure what is being
***REMOVED***passed by OSDF is indeed a numerical value.
strings_to_nums = {
    "VSS.fecalcal": "toFloat(VSS.fecalcal)"
}

***REMOVED***This populates the values in the side table of facet search. Want to let users
***REMOVED***know how many samples per category in a given property. 
count_props_dict = {
    "PS": "MATCH (n:subject)<-[:extracted_from]-(VSS:sample)<-[:derived_from]-(F:file) RETURN n.{0} AS prop, COUNT(DISTINCT(VSS)) as counts",
    "VSS": "MATCH (PS:subject)<-[:extracted_from]-(n:sample)<-[:derived_from]-(F:file) RETURN n.{0} AS prop, COUNT(DISTINCT(n)) as counts",
    "F": "MATCH (PS:subject)<-[:extracted_from]-(VSS:sample)<-[:derived_from]-(n:file) RETURN n.{0} AS prop, COUNT(DISTINCT(VSS)) as counts",
    "T": "MATCH (PS:subject)<-[:extracted_from]-(VSS:sample)<-[:derived_from]-(F:file)-[:has_tag]->(n:tag) RETURN n.{0} AS prop, COUNT(DISTINCT(VSS)) as counts"
}

###############
***REMOVED***NEO4J SETUP #
###############

***REMOVED***Get all these values from the conf
neo4j_bolt = int(neo4j_bolt)
neo4j_http = int(neo4j_http)
cypher_conn = Graph(password = neo4j_pw)

***REMOVED***This section will have all the logic for populating the actual data in the schema (data from Neo4j)
#graph = Graph(host=neo4j_ip,bolt_port=neo4j_bolt,http_port=neo4j_http,user=neo4j_un,password=neo4j_pw)

##########################################################
***REMOVED***FUNCTIONS FOR MANAGING USER SESSIONS AND QUERY HISTORY #
##########################################################

***REMOVED***Establish a "session" node in the Neo4j DB to consider the user logged in. 
***REMOVED***Note that only ONE session will be allowed per user at a given time. 
def establish_session(username):

    session_id = hashlib.sha256(username+str(time.time())).hexdigest()

    unique_session = True ***REMOVED***loop until we get a unique session_id regardless of user
    while unique_session:
        if cypher_conn.find_one("session", property_key='id', property_value=session_id):
            session_id = hashlib.sha256(username+str(time.time())).hexdigest()
        else:
            unique_session = False

    ***REMOVED***We know that if we've made it here this is a valid user found in the
    ***REMOVED***MySQL database. Need to create nodes individually before linking or 
    ***REMOVED***else the entire structure will throw an error due to uniqueness 
    ***REMOVED***constraints on the username/id in user/session.
    create_new_session = """
        MERGE (u:user { username:{un} }) 
        MERGE (s:session { id:{si}, created_at:TIMESTAMP() }) 
        MERGE (u)-[:has_session]->(s)
    """
    
    ***REMOVED***Modify this to limit how many logins a single user can have across instances
    concurrent_sessions = 2
    
    remove_old_session = """
        MATCH (s:session)<-[:has_session]-(u:user) 
        WHERE u.username={un} 
        WITH s ORDER BY s.created_at DESC LIMIT {cs} 
        WITH COLLECT(s.id) AS newest_sessions 
        MATCH (s:session)<-[:has_session]-(u:user) 
        WHERE u.username={un} 
        AND NOT s.id IN newest_sessions 
        DETACH DELETE s
    """

    tx = cypher_conn.begin()
    tx.run(create_new_session, parameters={'un':username, 'si':session_id})
    tx.run(remove_old_session, parameters={'un':username, 'cs':concurrent_sessions})
    tx.commit()

    return session_id

***REMOVED***If the user logs out, then disconnect deliberately here. The auto-loader
***REMOVED***should handle timeout disconnects.
def disconnect_session(session_id):

    cypher = "MATCH (s:session { id:{si} }) DETACH DELETE s"
    cypher_conn.run(cypher, parameters={'si':session_id})

    return

***REMOVED***Given a session ID and see if it checks out with what was set in the cookies
def get_user_info(session_id):

    user_info = {'username':"",'queries':[],'hrefs':[],'scounts':[],'fcounts':[]}

    cypher = """
        MATCH (s:session)<-[:has_session]-(u:user) 
        WHERE s.id = {si}
        WITH u 
        OPTIONAL MATCH (u)-[:saved_query]->(q:query)  
        RETURN u.username AS username,q
    """
    results = cypher_conn.run(cypher, parameters={'si':session_id}).data()

    ***REMOVED***Need to check here in case a user has been "logged out" by having too 
    ***REMOVED***many sessions.
    if results:
        if results[0]['username']:
            user_info['username'] = results[0]['username']

        if results[0]['q']:
            for x in range(0,len(results)):
                user_info['queries'].append(results[x]['q']['query_str'])
                user_info['hrefs'].append(results[x]['q']['url'])
                user_info['scounts'].append(results[x]['q']['s_count'])
                user_info['fcounts'].append(results[x]['q']['f_count'])

    if len(user_info['username']) > 0:
        return user_info
    else:
        return

***REMOVED***Given a session ID, reference URL, query, a count for how many samples, load
***REMOVED***into Neo4j that this user has made this query before and the number of 
***REMOVED***results returned from it. 
def save_query_sample_data(session_id,reference_url,query,count):

    ***REMOVED***If a sample, set the reference URL and sample count
    cypher = """
        MATCH (s:session)<-[:has_session]-(u:user) 
        WHERE s.id = {si} 
        WITH u
        MERGE (q:query { url:{url} })
        SET q.query_str={qs}, q.s_count={sc}
        WITH q,u
        MERGE (u)-[:saved_query]->(q)
        """
    ***REMOVED***Note the trimming of the save parameter from the reference URL, this is 
    ***REMOVED***so that when a user clicks a query to go back to they don't re-invoke
    ***REMOVED***all this save functionality as it's unnecessary at that point.
    cypher_conn.run(cypher, parameters={'si':session_id,'url':reference_url.replace('save=yes',''),'qs':query,'sc':count})

    return

***REMOVED***Simply append file count data to this particular query node. All other 
***REMOVED***information will be handled by the sample data function 
***REMOVED***save_query_sample_data().
def save_query_file_data(reference_url,count):

    cypher = """
        MERGE (q:query { url:{url} })
        SET q.f_count={fc}
        """
    cypher_conn.run(cypher, parameters={'url':reference_url.replace('save=yes',''),'fc':count})

    return

####################################
***REMOVED***FUNCTIONS FOR GETTING NEO4J DATA #
####################################

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

***REMOVED***Placeholder until the UI is completely stripped of GDC syntax
def convert_order(order):

    ***REMOVED***replace UI ':' with a ' '
    order = order.replace(':',' ')
    order = order.replace('.raw','') ***REMOVED***trim more GDC syntax

    ***REMOVED***UI has an erroneous ',' appended for files occassionally
    if order[-1] == ',':
        order = order[:-1]

    map_order = {
        'case_id': 'VSS.id',
        'file_name': 'F.id',
        'file_id': 'F.id',
        'project.primary_site': 'VSS.body_site',
        'data_category': 'F.node_type',
        'data_format': 'F.format',
        'cases.project.project_id': 'PS.project_name',
        'file_size': 'F.size'
    }
    
    for k,v in map_order.items():
        order = order.replace(k,v)

    return order

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
        cquery = "MATCH (F:file) RETURN SUM(DISTINCT(F.size)) AS tot"
    elif '"op"' in cy:
        cquery = build_cypher(cy,"null","null","null","size")
    else:
        cquery = build_adv_cypher(cy,"null","null","null","size")
        cquery = cquery.replace('WHERE "',"WHERE ") ***REMOVED***where does this phantom quote come from?!
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
                cquery = build_cypher(cy,"null","null","null","c_pagination")
            else:
                cquery = build_cypher(cy,"null","null","null","f_pagination")
        else:
            if c_or_f == 'c':
                cquery = build_adv_cypher(cy,"null","null","null","c_pagination")
                cquery = cquery.replace('WHERE "',"WHERE ") ***REMOVED***where does this phantom quote come from?!
            else:
                cquery = build_adv_cypher(cy,"null","null","null","f_pagination")
                cquery = cquery.replace('WHERE "',"WHERE ") ***REMOVED***where does this phantom quote come from?!
                
        res = process_cquery_http(cquery)
        calcs = pagination_calcs(res[0]['tot'],f,size,c_or_f)
        return Pagination(count=calcs[2], sort=calcs[4], fromNum=f, page=calcs[1], total=calcs[3], pages=calcs[0], size=size)

***REMOVED***retrieve the number of samples associated with the particular IDs
def get_sample_count(cy):
    cquery = build_cypher(cy,"null","null","null",'c_pagination')
    cquery = cquery.replace('WHERE "',"WHERE ") ***REMOVED***where does this phantom quote come from?!
    res = process_cquery_http(cquery)
    return int(res[0]['tot'])
    
***REMOVED***Retrieve ALL files associated with a given Subject ID.
def get_files(sample_id):
    fl = []
    dt, fn, df, ac, fi = ("" for i in range(5))

    cquery = "{0} WHERE VSS.id='{1}' RETURN F".format(full_traversal,sample_id)
    res = process_cquery_http(cquery)

    for x in range(0,len(res)): ***REMOVED***iterate over each unique path
        fs = 0
        dt = res[x]['F']['subtype']
        df = res[x]['F']['format']
        ac = "open" ***REMOVED***need to change this once a new private/public property is added to OSDF
        if 'size' in res[x]['F']:
            fs = res[x]['F']['size']
        fi = res[x]['F']['id']
        fn = extract_url(res[x]['F'])
        fl.append(IndivFiles(dataType=dt,fileName=fn,dataFormat=df,access=ac,fileId=fi,fileSize=fs))

    return fl

***REMOVED***Query to traverse top half of OSDF model (Project<-....-Sample). 
def get_proj_data(sample_id):
    cquery = "{0} WHERE VSS.id='{1}' RETURN PS.project_name AS name,PS.project_subtype AS subtype".format(full_traversal,sample_id)
    res = process_cquery_http(cquery)
    return Project(name=res[0]['name'],projectId=res[0]['subtype'])

def get_all_proj_data():
    cquery = "MATCH (VSS:subject) RETURN DISTINCT VSS.study_name, VSS.study_description"
    return process_cquery_http(cquery)

def get_all_study_data():
    cquery = '''
        {0} RETURN VSS.study_name AS study_name, VSS.study_full_name AS study_full_name, 
        PS.project_subtype AS project_subtype, VSS.study_subtype AS study_subtype, 
        COUNT(DISTINCT(VSS)) as case_count, COUNT(DISTINCT(F)) as file_count, F.node_type as file_type, 
        SUM(DISTINCT(F.size)) AS file_size, VSS.body_site AS body_site
    '''.format(full_traversal)
    return process_cquery_http(cquery)

def get_study_sample_counts():
    cquery = '{0} RETURN VSS.study_name AS study_name, COUNT(DISTINCT(VSS)) AS sample_count'.format(full_traversal)
    return process_cquery_http(cquery)

***REMOVED***This function is a bit unique as it's only called to populate the bar chart on the home page
def get_all_proj_counts():
    cquery = "{0} RETURN DISTINCT VSS.study_id, VSS.study_name, VSS.body_site, COUNT(DISTINCT(VSS)) as case_count, COUNT(DISTINCT(F)) as file_count".format(full_traversal)
    return process_cquery_http(cquery)

***REMOVED***Function to return all relevant values for the pie charts. Takes in WHERE from UI
def get_pie_chart_summary(cy):
   
    cquery = ""
    pn_bl,sn_bl,sbs_bl,sg_bl,fnt_bl,ff_bl = ([] for i in range(6))
    file_size = 0

    chart_order = [
        'project_name',
        "study_name",
        "sample_body_site",
        "subject_gender",
        "file_node_type",
        "file_format"
    ]

    tx = cypher_conn.begin()

    for chart in chart_order:        
        if "op" in cy:
            cquery = build_cypher(cy,"null","null","null","{0}_detailed".format(chart))
        else:
            cquery = build_adv_cypher(cy,"null","null","null","{0}_detailed".format(chart))

        res = tx.run(cquery)
        for record in res:
            if chart == 'sample_body_site': ***REMOVED***minor optimization, those with more groups towards the top
                sbs_bl.append(SBucket(key=record['prop'], caseCount=record['scount'], docCount=record['fcount'], fileSize=record['tot']))
            elif chart == 'study_name':
                sn_bl.append(SBucket(key=record['prop'], caseCount=record['scount'], docCount=record['fcount'], fileSize=record['tot']))
            elif chart == 'file_node_type':
                fnt_bl.append(SBucket(key=record['prop'], caseCount=record['scount'], docCount=record['fcount'], fileSize=record['tot']))
            elif chart == 'file_format':
                ff_bl.append(SBucket(key=record['prop'], caseCount=record['scount'], docCount=record['fcount'], fileSize=record['tot']))
            elif chart == 'subject_gender':
                sg_bl.append(SBucket(key=record['prop'], caseCount=record['scount'], docCount=record['fcount'], fileSize=record['tot']))
            elif chart == 'project_name':
                pn_bl.append(SBucket(key=record['prop'], caseCount=record['scount'], docCount=record['fcount'], fileSize=record['tot']))
                file_size += record['tot'] ***REMOVED***calculate this here as projects most likely to return lowest amount of rows

        res.close()

    tx.commit()

    return PieCharts(project_name=SBucketCounter(buckets=pn_bl),
        subject_gender=SBucketCounter(buckets=sg_bl),
        file_format=SBucketCounter(buckets=ff_bl),
        study_name=SBucketCounter(buckets=sn_bl),
        file_type=SBucketCounter(buckets=fnt_bl),
        sample_body_site=SBucketCounter(buckets=sbs_bl),
        fs=FileSize(value=file_size))

***REMOVED***Cypher query to count the amount of each distinct property
def count_props(node, prop, cy):
    cquery = ""
    if cy == "":
        cquery = count_props_dict[node].format(prop)
    else:
        cquery = build_cypher(cy,"null","null","null",prop)
    return process_cquery_http(cquery)

***REMOVED***Cypher query to count the amount of each distinct property
def count_props_and_files(node, prop, cy):

    cquery,with_distinct = ("" for i in range (2))
    
    if cy == "":
        retval = "RETURN {0}.{1} AS prop, COUNT(DISTINCT(VSS)) AS ccounts, COUNT(F) AS dcounts, SUM(DISTINCT(F.size)) as tot".format(node,prop)
        cquery = "{0} {1}".format(full_traversal,retval)

    else:
        prop_detailed = "{0}_detailed".format(prop)
        if "op" in cy:
            cquery = build_cypher(cy,"null","null","null",prop_detailed)
        else:
            cquery = build_adv_cypher(cy,"null","null","null",prop_detailed)
            cquery = cquery.replace('WHERE "',"WHERE ") ***REMOVED***where does this phantom quote come from?!

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
    order = convert_order(order)

    if cy == "":
        if f != 0:
            f = f-1
        retval = "RETURN DISTINCT PS,VSS ORDER BY {0} SKIP {1} LIMIT {2}".format(order,f,size)
        cquery = "{0} {1}".format(full_traversal,retval)
    elif '"op"' in cy:
        cquery = build_cypher(cy,order,f,size,"cases")
    else:
        cquery = build_adv_cypher(cy,order,f,size,"cases")
        cquery = cquery.replace('WHERE "',"WHERE ") ***REMOVED***where does this phantom quote come from?!

    res = process_cquery_http(cquery)

    for x in range(0,len(res)):
        cur = CaseHits(
            project=Project(projectId=res[x]['PS']['project_subtype'],
                primarySite=res[x]['VSS']['body_site'],
                name=res[x]['PS']['project_name'],
                studyName=res[x]['VSS']['study_name'],
                studyFullName=res[x]['VSS']['study_name']),
                caseId=res[x]['VSS']['id'],
                visitNumber=res[x]['VSS']['visit_visit_number'],
                subjectId=res[x]['PS']['rand_subject_id'])
        hits.append(cur)
    return hits

***REMOVED***Function to return file values to populate the table.
def get_file_hits(size,order,f,cy):
    hits = []
    cquery = ""
    if order != '':
        order = convert_order(order)

    if cy == "":
        if f != 0:
            f = f-1
        retval = "RETURN DISTINCT(F) ORDER BY {0} SKIP {1} LIMIT {2}".format(order,f,size)
        cquery = "{0} {1}".format(full_traversal,retval)
    elif '"op"' in cy:
        cquery = build_cypher(cy,order,f,size,"files")
    else:
        cquery = build_adv_cypher(cy,order,f,size,"files")
        cquery = cquery.replace('WHERE "',"WHERE ") ***REMOVED***where does this phantom quote come from?!

    if order == '': ***REMOVED***for adding all to cart, allow no 'ORDER BY' for the sake of speed
        cquery = cquery.replace('ORDER BY','')

    res = process_cquery_http(cquery)

    for x in range(0,len(res)):
        ***REMOVED***For now, just returning file data for file hits
        #case_hits = [] ***REMOVED***reinit each iteration
        #cur_case = CaseHits(project=Project(projectId=res[x]['PS']['project_subtype'],name=res[x]['PS']['project_name']),caseId=res[x]['VSS']['id'])
        #case_hits.append(cur_case)

        furl = extract_url(res[x]['F']) ***REMOVED***File name is our URL
        if '.hmpdacc' in furl and '/data/' in furl: ***REMOVED***HMP endpoint
            furl = re.search(r'/data/(.*)',furl).group(1)
        elif '.ihmpdcc' in furl and 'org/' in furl:
            furl = re.search(r'\.org/(.*)',furl).group(1)

        ***REMOVED***Should try handle this at an earlier phase, but make sure size exists
        if 'size' not in res[x]['F']:
            res[x]['F']['size'] = 0

        cur_file = FileHits(dataType=res[x]['F']['subtype'],
            fileName=furl,
            dataFormat=res[x]['F']['format'],
            submitterId="null",
            access="open",
            state="submitted",
            fileId=res[x]['F']['id'],
            dataCategory=res[x]['F']['node_type'],
            experimentalStrategy=res[x]['F']['subtype'],
            fileSize=res[x]['F']['size']
            )

        hits.append(cur_file)    
    return hits

***REMOVED***Pull all the data associated with a particular case (sample) ID. 
def get_sample_data(sample_id):
    retval = "WHERE VSS.id='{0}' RETURN PS,VSS,F".format(sample_id)
    cquery = "{0} {1}".format(full_traversal,retval)
    res = process_cquery_http(cquery)
    fl = []
    for x in range(0,len(res)):
        fl.append(IndivFiles(fileId=res[x]['F']['id']))
    return IndivSample(sample_id=sample_id,
        body_site=res[0]['VSS']['body_site'],
        subject_id=res[0]['PS']['id'],
        rand_subject_id=res[0]['PS']['rand_subject_id'],
        subject_gender=res[0]['PS']['gender'],
        study_center=res[0]['VSS']['study_center'],
        project_name=res[0]['PS']['project_name'],
        files=fl
        )

***REMOVED***Pull all the data associated with a particular file ID. 
def get_file_data(file_id):
    cl, al, fl = ([] for i in range(3))
    retval = "WHERE F.id='{0}' RETURN PS,VSS,D,F".format(file_id)
    cquery = "{0} {1}".format(full_traversal,retval)
    res = process_cquery_http(cquery)
    size = 0
    if 'size' in res[0]['F']: ***REMOVED***some files with non-valid URLs can have no size
        size = res[0]['F']['size']
    furl = extract_url(res[0]['F']) 
    sample_bs = res[0]['VSS']['body_site']
    wf = "{0} -> {1}".format(sample_bs,res[0]['D']['node_type'])
    cl.append(CaseHits(project=Project(projectId=res[0]['PS']['project_subtype']),caseId=res[0]['VSS']['id']))
    al.append(AssociatedEntities(entityId=res[0]['D']['id'],caseId=res[0]['VSS']['id'],entityType=res[0]['D']['node_type']))
    fl.append(IndivFiles(fileId=res[0]['F']['id']))
    a = Analysis(updatedDatetime="null",workflowType=wf,analysisId="null",inputFiles=fl) ***REMOVED***can add analysis ID once node is present or remove if deemed unnecessary
    return FileHits(
        dataType=res[0]['F']['node_type'],
        fileName=furl,
        md5sum=res[0]['F']['md5'],
        dataFormat=res[0]['F']['format'],
        submitterId="null",
        state="submitted",
        access="open",
        fileId=res[0]['F']['id'],
        dataCategory=res[0]['F']['node_type'],
        experimentalStrategy=res[0]['F']['study'],
        fileSize=size,
        cases=cl,
        associatedEntities=al,
        analysis=a
        )

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
    cquery = "MATCH (F:file)-[:derived_from]->(S:sample) WHERE F.id IN {0} RETURN F,S".format(ids)
    res = process_cquery_http(cquery)

    outlist = []

    ***REMOVED***Grab the ID, file URL, md5, and size
    for entry in res:
        md5,size = ("" for i in range(2)) ***REMOVED***private node data won't have these properties
        file_id = entry['F']['id']
        urls = extract_manifest_urls(entry['F'])
        if 'md5' in entry['F']:
            md5 = entry['F']['md5']
        if 'size' in entry['F']:
            size = entry['F']['size']
        sample_id = entry['S']['id']
        outlist.append("\n{0}\t{1}\t{2}\t{3}\t{4}".format(file_id,md5,size,urls,sample_id))

    return outlist

***REMOVED***Load these lists on startup to use for parsing optional metadata. Notice 
***REMOVED***that subject_ prefix is trimmed while visit_ is not. This is because 
***REMOVED***subject is a base node while visit is not and so searching on the visit
***REMOVED***property requires that visit prefix to work properly. 
def filter_attr_metadata(non_attr_set,md_type):

    fields = list(gql_map.keys())
    attr_list = []

    ***REMOVED***Insert additional sample_attr fields here, since fecalcal is essentially
    ***REMOVED***on its own as the only sample metadata searchable it is handled here. 
    if md_type == 'visit':
        attr_list.append('fecalcal')

    for field in fields:
        if field.startswith(md_type):
            if field not in non_attr_set:
                if md_type == 'subject':
                    field = field.replace('subject_','')
                attr_list.append(field)

    return attr_list

subject_metadata = filter_attr_metadata(
    {
        'subject_gender',
        'subject_race',
        'subject_subtype',
        'subject_uuid',
        'subject_id'
    },
    'subject')
visit_metadata = filter_attr_metadata(
    {
        'visit_date',
        'visit_interval',
        'visit_number',
        'visit_subtype',
        'visit_id'
    },
    'visit')

def get_metadata(id_list):

    cquery = "MATCH (F:file)-[:derived_from]->(S:sample)-[:extracted_from]->(J:subject) WHERE F.id IN {0} RETURN S,J".format(id_list)
    res = process_cquery_http(cquery)

    base_metadata = [
        'sample_id',
        'subject_id',
        'sample_body_site',
        'visit_number',
        'subject_gender',
        'subject_race',
        'study_full_name',
        'project_name',
    ]

    items = [(field, []) for field in (base_metadata + subject_metadata + visit_metadata)] ***REMOVED***essentially defaultdict of OrderedDict
    cols = OrderedDict(items)

    ***REMOVED***first process those that are required
    for entry in res:

        ***REMOVED***Prevent missing data points in any of these properties as there have
        ***REMOVED***been cases of missing keys which cause a crash in the metadata download. 
        ***REMOVED***Those without 'ifs' are guaranteed by cutlass. Also note that any 
        ***REMOVED***numbers need to be converted to strings in order to join str list. 
        cols['sample_id'].append(entry['S']['id'])
        cols['subject_id'].append(entry['J']['id'])
        cols['sample_body_site'].append(entry['S']['body_site'])
        cols['visit_number'].append(str(entry['S']['visit_visit_number']))
        cols['subject_gender'].append(entry['J']['gender'])
        ***REMOVED***Match missing 'race' it up with the 'unknown' value already present in some of the data
        cols['subject_race'].append(str(entry['J']['race'])) if 'race' in entry['J'] else cols['subject_race'].append("unknown") 
        cols['study_full_name'].append(entry['S']['study_full_name'])
        cols['project_name'].append(entry['J']['project_name'])

        ***REMOVED***Subject attrs
        for attr in subject_metadata:
            cols[attr].append(str(entry['J'][attr])) if attr in entry['J'] else cols[attr].append("NA")

        ***REMOVED***Visit attrs
        for attr in visit_metadata:
            cols[attr].append(str(entry['S'][attr])) if attr in entry['S'] else cols[attr].append("NA")

    ***REMOVED***Now that we've parsed through everything in Neo4j, delete any columns that
    ***REMOVED***solely contain "NA"s in the optional attribute fields. 
    for attr in (subject_metadata + visit_metadata):
        if len(set(cols[attr])) == 1 and cols[attr][0] == "NA":
            del cols[attr] ***REMOVED***going to exist no matter what
        else:
            ***REMOVED***Rename the key so that the metadata file is all-encompassing and
            ***REMOVED***describes what this metadata is tied to (subject/sample/visit)
            if attr in subject_metadata:
                cols["subject_{0}".format(attr)] = cols[attr]
                del cols[attr]
            elif not attr.startswith('visit'):
                cols["sample_{0}".format(attr)] = cols[attr]
                del cols[attr]                

    rows = []
    rows.append("\t".join(list(cols.keys()))) ***REMOVED***header

    ***REMOVED***Create a string with all the found data to pass to the file
    for i in range(0,len(cols['sample_id'])):
        row = []
        for key in cols:
            row.append(cols[key][i])
        rows.append(("\t").join(row))

    return ("\n").join(rows)

***REMOVED***Makes sure we generate a unique token
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

    id_list.sort() ***REMOVED***ensure ordering doesn't affect the token creation

    ids = build_neo4j_list(id_list)

    ***REMOVED***overkill, but should suffice
    original_token = hashlib.sha256(ids).hexdigest()
    original_token += hashlib.sha224(ids).hexdigest()
    ids = "[{0}]".format(ids)

    token = check_token(original_token,ids)

    if token != "":
        return token
    else:
        token = check_token(original_token[::-1],ids) ***REMOVED***try the reverse

    if token != "":
        return token
    else:
        return "ERROR generating token."

***REMOVED***Takes in a token and hits the Neo4j server to create a manifest on the fly
***REMOVED***using all the IDs noted within the particular token. 
def token_to_manifest(token):

    ***REMOVED***Leave early if the token is obviously corrupt
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

***REMOVED***Function to extract known GDC syntax and convert to OSDF. This is commonly needed for performing
***REMOVED***cypher queries while still being able to develop the front-end with the cases syntax.
def convert_gdc_to_osdf(inp_str):
    ***REMOVED***Errors in Graphene mapping prevent the syntax I want, so ProjectName is converted to 
    ***REMOVED***Cypher ready Project.name here (as are the other possible query parameters).
    inp_str = inp_str.replace("cases.ProjectName","PS.project_name")
    inp_str = inp_str.replace("cases.SampleFmabodysite","VSS.body_site")
    inp_str = inp_str.replace("cases.sample_body_site","VSS.body_site")
    inp_str = inp_str.replace("cases.SubjectGender","PS.gender")
    inp_str = inp_str.replace("project.primary_site","VSS.body_site")
    inp_str = inp_str.replace("file.category","F.subtype") ***REMOVED***note the conversion
    inp_str = inp_str.replace("files.file_id","F.id")
    inp_str = inp_str.replace("cases.","") ***REMOVED***these replaces have to be catch alls to replace all instances throughout
    inp_str = inp_str.replace("Project_","PS.project_")
    inp_str = inp_str.replace("Sample_","VSS.")
    inp_str = inp_str.replace("SampleAttr_","VSS.")
    inp_str = inp_str.replace("Study_","VSS.study_")
    inp_str = inp_str.replace("Subject_","PS.")
    inp_str = inp_str.replace("SubjectAttr_","PS.")
    inp_str = inp_str.replace("Visit_","VSS.visit_")
    inp_str = inp_str.replace("VisitAttr_","VSS.visit_")

    ***REMOVED***Handle facet searches from panel on left side
    inp_str = inp_str.replace("file_type","F.node_type")
    inp_str = inp_str.replace("file_format","F.format")

    ***REMOVED***Next two lines guarantee URL encoding (seeing errors with urllib)
    inp_str = inp_str.replace('"','|')
    inp_str = inp_str.replace('\\','')
    inp_str = inp_str.replace(" ","%20")
    inp_str = inp_str.replace(": ",":")

    ***REMOVED***While the DB is to be set at read-only, in the case this toggle is 
    ***REMOVED***forgotten do some checks to make sure nothing fishy is happening.
    potentially_malicious = set([";"," delete "," create "," detach "," set ",
                                " return "," match "," merge "," where "," with ",
                                " import "," remove "," union "])
    check_str = inp_str.lower()
    for word in check_str:
        if word in potentially_malicious:
            return "Invalid characters."

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
***REMOVED***for Project name as Project.name or something similar instead of PS.project_name.
def convert_portal_to_neo4j(inp_str):

    inp_str = inp_str.replace("cases.","")
    inp_str = inp_str.replace("files.","")

    inp_str = inp_str.replace("Project.","project.")
    inp_str = inp_str.replace("subject.uuid","subject.id")
    inp_str = inp_str.replace("subject.id","subject.rand_subject_id")

    if 'PS.' not in inp_str:
        ***REMOVED***Project -> Study -> Subject
        inp_str = inp_str.replace("project_","project.")
        inp_str = inp_str.replace("study_","study.")
        inp_str = inp_str.replace("subject_","subject.")
        inp_str = inp_str.replace("project."," PS.project_")
        inp_str = inp_str.replace("study.","VSS.study_")
        inp_str = inp_str.replace("subject.","PS.")
        inp_str = inp_str.replace("rand_PS.id","rand_subject_id")

    if 'VSS.' not in inp_str:
         ***REMOVED***Visit -> Sample
        inp_str = inp_str.replace("visit_","visit.")
        inp_str = inp_str.replace("sample_","sample.")  
        inp_str = inp_str.replace("visit.","VSS.visit_")
        if 'VSS.visit_number' in inp_str:
            inp_str = inp_str.replace("VSS.visit_number","VSS.visit_visit_number")
        inp_str = inp_str.replace("sample.","VSS.")   
  
    if "F." not in inp_str:
        ***REMOVED***File
        inp_str = inp_str.replace("file.","F.")
        inp_str = inp_str.replace("File_","F.")

    if "T." not in inp_str:
        ***REMOVED***Tag
        inp_str = inp_str.replace("tag.","T.")

    inp_str = inp_str.replace("%20"," ")

    if inp_str.startswith('"'):
        inp_str = inp_str[1:]
        
    return inp_str

***REMOVED***Whether or not to traverse to the tag level, only required when a tag is 
***REMOVED***being searched
def which_traversal(where):
    traversal = ""
    if "T.term" in where:
        traversal = tag_traversal
    else:
        traversal = full_traversal
    return traversal

***REMOVED***Final function needed to build the entirety of the Cypher query taken from facet search. Accepts the following:
***REMOVED***match = base MATCH query for Cypher
***REMOVED***whereFilters = filters string passed from GDC portal
***REMOVED***order = parameters to order results by (needed for pagination)
***REMOVED***start = index of sort to start at
***REMOVED***size = number of results to return
***REMOVED***rtype = return type, want to be able to hit this for both cases, files, and aggregation counts.
def build_cypher(whereFilters,order,start,size,rtype):
    arr = []

    whereFilters = convert_portal_to_neo4j(whereFilters)
    traversal = which_traversal(whereFilters)

    q = json.loads(whereFilters) ***REMOVED***parse filters input into JSON (yields hashes of arrays)
    w1 = get_depth(q, arr) ***REMOVED***first step of building where clause is the array of individual comparison elements
    where = build_facet_where(w1)
    order = order.replace("cases.","")
    order = order.replace("files.","")

    retval1 = returns[rtype] ***REMOVED***actual RETURN portion of statement

    ***REMOVED***FIX IN LOADER TO MAKE TYPES CONSISTENT
    for k,v in strings_to_nums.items():
        where = where.replace(k,v)

    if rtype.endswith('detailed'): ***REMOVED***sum schema handling
        if whereFilters != "":
            return "{0} WHERE {1} {2}".format(traversal,where,retval1)
        else:
            return "{0} {1}".format(traversal,retval1)


    if rtype in ["cases","files"]: ***REMOVED***pagination handling needed for these returns

        ***REMOVED***When adding all files to cart, a special case happens where there is
        ***REMOVED***no order specified so have to return a more basic query.
        if len(order) < 2:
            return "{0} WHERE {1} {2}".format(traversal,where,retval1)

        if start != 0:
            start = start - 1
        retval2 = "ORDER BY {0} SKIP {1} LIMIT {2}".format(order,start,size) 
        return "{0} WHERE {1} {2} {3}".format(traversal,where,retval1,retval2)
    else:
        return "{0} WHERE {1} {2}".format(traversal,where,retval1)

***REMOVED***First iteration, handling all regex individually
regexForNotEqual = re.compile(r"<>\s([0-9]*[a-zA-Z_]+[\-a-zA-Z0-9_]*)\b") ***REMOVED***only want to add quotes to anything that's not solely numbers
regexForEqual = re.compile(r"=\s([0-9]*[a-zA-Z_]+[\-a-zA-Z0-9_]*)\b") 
regexForIn = re.compile(r"(\[[\-a-zA-Z\'\"\s\,\(\)]+\])") ***REMOVED***catch anything that should be in a list

***REMOVED***This advanced Cypher builder expects the string generated by any of the advanced queries. 
***REMOVED***Parameters are described above before build_cypher()
def build_adv_cypher(whereFilters,order,start,size,rtype):

    if '%20' in whereFilters:
        whereFilters = urllib.unquote(whereFilters).decode('utf-8')

    where = whereFilters[10:len(whereFilters)-2]
    where = where.replace("!=","<>")
    where = where.strip()

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
    where = convert_portal_to_neo4j(where)
    traversal = which_traversal(where)

    retval1 = returns[rtype] ***REMOVED***actual RETURN portion of statement

    ***REMOVED***FIX IN LOADER TO MAKE TYPES CONSISTENT
    for k,v in strings_to_nums.items():
        where = where.replace(k,v)

    if rtype.endswith('detailed'): ***REMOVED***sum schema handling
        if whereFilters != "":
            return "{0} WHERE {1} {2}".format(traversal,where,retval1)
        else:
            return "{0} {1}".format(traversal,retval1)

    if rtype in ["cases","files"]: ***REMOVED***pagination handling needed for these returns
        if start != 0:
            start = start-1
        retval2 = "ORDER BY {0} SKIP {1} LIMIT {2}".format(order,start,size)
        if size == 0: ***REMOVED***accounting for inconsistency where front-end asks for a 0 size return
            retval2 = "ORDER BY {0}".format(order)
        return "{0} WHERE {1} {2} {3}".format(traversal,where,retval1,retval2)
    else:
        return "{0} WHERE {1} {2}".format(traversal,where,retval1)
