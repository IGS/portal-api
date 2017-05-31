***REMOVED***simple app to allow GraphiQL interaction with the schema and verify it is
***REMOVED***structured how it ought to be. 
from flask import Flask, jsonify, request, abort, redirect, make_response
from flask_graphql import GraphQLView
from flask.views import MethodView
from sum_schema import sum_schema
from ac_schema import ac_schema
from files_schema import files_schema
from table_schema import table_schema
from indiv_files_schema import indiv_files_schema
from indiv_sample_schema import indiv_sample_schema
from query import get_url_for_download,convert_gdc_to_osdf,get_all_proj_data,get_all_proj_counts,get_manifest_data,get_all_study_data,token_to_manifest,convert_portal_to_neo4j
from autocomplete_map import gql_map
from conf import access_origin,be_port
from front_page_results import q1_query,q1_cases,q1_files,q2_query,q2_cases,q2_files,q3_query,q3_cases,q3_files
import graphene
import json, urllib2, urllib, re

application = Flask(__name__)
application.debug = True

***REMOVED***Function to handle access control allow headers
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = access_origin

    response.headers['Access-Control-Allow-Credentials'] = 'true'
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response

application.after_request(add_cors_headers)

@application.route('/gql/_mapping', methods=['GET'])
def get_maps():
    res = jsonify({"project.name": gql_map['project_name'],
        "project.subtype": gql_map['project_subtype'],
        "study.center": gql_map['study_center'],
        "study.contact": gql_map['study_contact'],
        "study.description": gql_map['study_description'],
        "study.name": gql_map['study_name'],
        "study.srp_id": gql_map['study_srp_id'],
        "study.subtype": gql_map['study_subtype'],
        "subject.gender": gql_map['subject_gender'],
        "subject.race": gql_map['subject_race'],
        "subject.subtype": gql_map['subject_subtype'],
        "visit.date": gql_map['visit_date'],
        "visit.id": gql_map['visit_id'],
        "visit.interval": gql_map['visit_interval'],
        "visit.number": gql_map['visit_number'],
        "visit.subtype": gql_map['visit_subtype'],
        "sample.id": gql_map['sample_id'], 
        "sample.fma_body_site": gql_map['sample_fma_body_site'], 
        "sample.biome": gql_map['sample_biome'],
        "sample.body_product": gql_map['sample_body_product'],
        "sample.collection_date": gql_map['sample_collection_date'],
        "sample.env_package": gql_map['sample_env_package'],
        "sample.feature": gql_map['sample_feature'],
        "sample.geo_loc_name": gql_map['sample_geo_loc_name'],
        "sample.lat_lon": gql_map['sample_lat_lon'],
        "sample.material": gql_map['sample_material'],
        "sample.project_name": gql_map['sample_project_name'],
        "sample.rel_to_oxygen": gql_map['sample_rel_to_oxygen'],
        "sample.samp_collect_device": gql_map['sample_samp_collect_device'],
        "sample.samp_mat_process": gql_map['sample_samp_mat_process'],
        "sample.size": gql_map['sample_size'],
        "sample.subtype": gql_map['sample_subtype'],
        "sample.supersite": gql_map['sample_supersite'], 
        "file.format": gql_map['file_format'],
        "file.type": gql_map['file_node_type'],
        "file.id": gql_map['file_id'],
        "tag": gql_map['tag']
        })
    return res

***REMOVED***Note the multiple endpoints going to the same "cases endpoint to accommodate GDC syntax"
@application.route('/cases', methods=['GET','OPTIONS','POST'])
@application.route('/sample', methods=['GET','OPTIONS','POST'], endpoint='sample_alt_ep')
@application.route('/file', methods=['GET','OPTIONS','POST'], endpoint='file_alt_ep')
def get_cases():
    
    filters = request.args.get('filters')
    from_num = request.args.get('from')
    size = request.args.get('size')
    order = request.args.get('sort')
    url = "http://localhost:{0}/ac_schema".format(be_port)

    if filters == q1_query: ***REMOVED***return the front page data without hitting neo4j
        return make_json_response(q1_cases)
    elif filters == q2_query:  
        return make_json_response(q2_cases)
    elif filters == q3_query:
        return make_json_response(q3_cases)

    ***REMOVED***Processing autocomplete here as well as finding counts for the set category
    if(request.args.get('facets') and not request.args.get('expand')):

        original_facet = request.args.get('facets') ***REMOVED***original facet
        gql_facet = original_facet.replace('.','_')

        gql = '''
            {{
                aggregations {{
                    {0} {{
                        buckets {{
                            key
                            doc_count
                        }}
                    }}     
                }}
            }}
        '''.format(gql_facet)

        query = {'query':gql}

        response = urllib2.urlopen(url,data=urllib.urlencode(query))
        r = response.read()
        data = ('{0}, "warnings": {{}}}}'.format(r[:-1]).replace(gql_facet,original_facet))
        return make_json_response(data)

    else:

        if filters == "{}":
            filters = ""
            if not size:
                size = 20
            if not from_num:
                from_num = 1

        ac_gql = '''
            {{
                pagination(cy:"{0}",s:{1},f:{2}) {{
                    count
                    total
                    page
                    pages
                    from
                    sort
                    size
                }}
                hits(cy:"{0}",s:{1},f:{2},o:"{3}"){{
                    case_id
                    project{{
                    project_id
                    study_name
                    study_full_name
                    primary_site
                    }}
                }}
                aggregations{{
                    project_name{{
                        buckets{{
                            key
                            doc_count
                        }}
                    }}
                    sample_body_site{{
                        buckets{{
                            key
                            doc_count
                        }}
                    }}
                    subject_gender{{
                        buckets{{
                            key
                            doc_count
                        }}
                    }}
                }}
            }}         
        '''
        
        if request.get_data():      
            f1 = request.get_data()
            f2 = json.loads(f1)
            filters = f2['filters']
            from_num = f2['from']
            order = f2['sort']
            size = f2['size']
            filters = json.dumps(filters)

        if filters:
            filters = convert_gdc_to_osdf(filters)
        else:
            size = 20
            from_num = 1
            order = "case_id.raw:asc"
            filters = ""

        query = {'query':ac_gql.format(filters,size,from_num,order)}
        response = urllib2.urlopen(url,data=urllib.urlencode(query))
        r = response.read()
        data = ('{0}, "warnings": {{}}}}'.format(r[:-1]))
        return make_json_response(data)

***REMOVED***Route for specific cases endpoints that associates with various files
@application.route('/cases/<case_id>', methods=['GET','OPTIONS'])
def get_case_files(case_id):

    if not request.args.get('expand'):
        url = "http://localhost:{0}/files_schema".format(be_port)

        files_gql = '''
            {{
                project(id:"{0}") {{
                    project_id
                    name
                }}
                files(id:"{0}") {{
                    data_type
                    file_name
                    data_format
                    access
                    file_id
                    file_size
                }}
                case_id(id:"{0}")
                submitter_id
            }}
        '''

        query = {'query':files_gql.format(case_id)}
        response = urllib2.urlopen(url,data=urllib.urlencode(query))
        r = response.read()
        data = ('{0}, "warnings": {{}}}}'.format(r[:-1]))
        return make_json_response(data)
    else:
        url = "http://localhost:{0}/indiv_sample_schema".format(be_port)

        sample_gql = '''
            {{
                sample(id: "{0}") {{
                    sample_id
                    body_site
                    subject_id
                    rand_subject_id
                    subject_gender
                    study_center
                    project_name
                }}
            }}
        '''

        query = {'query':sample_gql.format(case_id)}
        response = urllib2.urlopen(url,data=urllib.urlencode(query))
        r = response.read()
        data = ('{0}, "warnings": {{}}}}'.format(r[:-1]))
        return make_json_response(data)

@application.route('/files/<file_id>', methods=['GET','OPTIONS'])
def get_file_metadata(file_id):

    url = "http://localhost:{0}/indiv_files_schema".format(be_port)

    idv_file_gql = '''
        {{
            fileHit(id:"{0}") {{
            data_type
            file_name
            data_format
            file_id
            file_size
            submitter_id
            access
            state
            data_category
            experimental_strategy
                analysis {{
                    updated_datetime
                    workflow_type
                    analysis_id
                }},
                associated_entities {{
                    entity_id
                    entity_type
                }},
                cases {{
                        project{{
                            project_id
                        }}
                        case_id
                    }}
            }}
        }}
    '''

    query = {'query':idv_file_gql.format(file_id)}
    response = urllib2.urlopen(url,data=urllib.urlencode(query))
    r = response.read()
    trimmed_r = r.replace(':{"fileHit"',"") ***REMOVED***HACK for formatting
    final_r = trimmed_r[:-1]
    data = ('{0}, "warnings": {{}}}}'.format(final_r[:-1]))
    return make_json_response(data)

@application.route('/status', methods=['GET','OPTIONS'])
def get_status():
    return 'OK'

@application.route('/status/user', methods=['GET','OPTIONS','POST'])
def get_status_user_unauthorized():
    return 'OK'

@application.route('/status/api/data', methods=['GET','OPTIONS','POST'])
def get_status_api_data():
    id = request.form.get('ids')
    #ids = request.form.getlist('ids') ***REMOVED***need to figure out how to bundle
    return redirect(get_url_for_download(id))

@application.route('/files', methods=['GET','OPTIONS','POST'])
def get_files():

    filters = ""
    url = "http://localhost:{0}/table_schema".format(be_port)

    table_schema_gql = '''
        {{
            pagination(cy:"{0}",s:{1},f:{2}) {{
                count
                sort
                from
                page
                total
                pages
                size
            }}
            hits(cy:"{0}",s:{1},f:{2},o:"{3}") {{
                data_type
                file_name
                data_format
                submitter_id
                access
                state
                file_id
                data_category
                file_size
                experimental_strategy
                cases {{
                    project {{
                        project_id
                        name
                    }}
                    case_id
                }}
            }}
            aggregations {{
                file_type {{
                    buckets {{
                        key
                        doc_count
                    }}
                }}
                file_format {{
                    buckets {{
                        key
                        doc_count
                    }}
                }}
            }}
        }}  
    '''

    from_num = request.args.get('from')
    size = request.args.get('size')
    order = request.args.get('sort')

    if request.args.get('filters'):
        filters = request.args.get('filters')

        if filters == q1_query: ***REMOVED***return the front page data without hitting neo4j
            return make_json_response(q1_files)
        elif filters == q2_query:  
            return make_json_response(q2_files)
        elif filters == q3_query:
            return make_json_response(q3_files)

    elif request.get_data():
        f1 = request.get_data().decode('utf-8')
        f2 = json.loads(f1)
        filters = f2['filters']
    else: ***REMOVED***beyond my understanding why this works at the moment
        if request.method == 'POST':
            return 'OK'
        elif request.method == 'OPTIONS':
            return 'OK'

    if len(filters) < 3:
        if '"op"' in filters or "op" in filters:
            f1 = request.get_data()
            f2 = json.loads(f1)
            from_num = f2['from']
            order = f2['sort']
            size = f2['size']
            filters = json.dumps(filters)
        else:
            filters = ""

    if not size: ***REMOVED***handle sample page cart loading
        size = 10000

    filters = convert_gdc_to_osdf(filters)
    query = {'query':table_schema_gql.format(filters,size,from_num,order)}
    response = urllib2.urlopen(url,data=urllib.urlencode(query))
    r = response.read()
    data = ('{0}, "warnings": {{}}}}'.format(r[:-1]))
    return make_json_response(data)

@application.route('/projects', methods=['GET','POST'])
def get_project():
    facets = request.args.get('facets')

    if facets is None:
        ***REMOVED***HACK - should go through GQL endpoint
        pdata = get_all_proj_data()
        proj_list = []

        for p in pdata:
            proj_list.append({ "project_id": p["VSS.study_name"], "primary_site": "multiple", "disease_type": p["VSS.study_description"], "released": True, "name": p["VSS.study_description"] })
        np = len(proj_list)

        p_str = "{{ \"count\": {0}, \"sort\": \"\", \"from\": 1, \"page\": 1, \"total\": {1}, \"pages\": 1, \"size\": 100 }}".format(np, np)
        hit_str = json.dumps(proj_list)
        data = ("{{\"data\" : {{\"hits\" : [ {0} ], \"pagination\": {1}}}, \"warnings\": {{}}}}".format(hit_str, p_str))
        return make_json_response(data)

    ***REMOVED***HACK - should go through GQL endpoint
    if facets == 'primary_site':
        pd = get_all_proj_counts()

        npd = len(pd)
        p_str = "{{ \"count\": {0}, \"sort\": \"\", \"from\": 1, \"page\": 1, \"total\": {1}, \"pages\": 1, \"size\": 100 }}".format(npd, npd)
        counts = {}
        hit_list = []

        for p in pd:
            proj_id = p["VSS.study_name"]
            psite = p["VSS.body_site"]
            n_files = p["file_count"]
            n_cases = p["case_count"]
            if psite is None:
                psite = "None"
            if psite in counts:
                counts[psite] = counts[psite] + 1
            else:
                counts[psite] =  1
            hit_list.append({"primary_site" : psite, "project_id": proj_id , "summary": { "case_count": n_cases, "file_count": n_files} })

        buckets_list = []
        for ckey in counts:
            ccount = counts[ckey]
            buckets_list.append({ "key": ckey, "doc_count": ccount})

        buckets_str = json.dumps(buckets_list)
        hit_str = json.dumps(hit_list)
        agg_str = "{{ \"primary_site\": {{ \"buckets\": {0} }}}}".format(buckets_str)

        data = ("{{\"data\" : {{\"aggregations\": {0}, \"hits\" : {1}, \"pagination\": {0}}}, \"warnings\": {{}}}}".format(agg_str, hit_str, p_str))
        return make_json_response(data)

    ***REMOVED***Enter here if going to the projects tab
    else:
        pdata = get_all_study_data()
        proj_list = []

        for p in pdata:
            proj_list.append({ "project_id": p["VSS.study_name"], "disease_type": p["VSS.study_subtype"], "project_name": p["VSS.project_subtype"], "summary": { "case_count": p["case_count"], "file_count": p["file_count"]} })
        np = len(proj_list)

        p_str = "{{ \"count\": {0}, \"sort\": \"\", \"from\": 1, \"page\": 1, \"total\": {1}, \"pages\": 1, \"size\": 100 }}".format(np, np)
        hit_str = json.dumps(proj_list)
        data = ("{{\"data\" : {{\"hits\" :  {0} , \"pagination\": {1}}}, \"warnings\": {{}}}}".format(hit_str, p_str))
        return make_json_response(data)

@application.route('/annotations', methods=['GET','OPTIONS'])
def get_annotation():
    return 'hi'

***REMOVED***Calls sum_schema endpoint/GQL instance in order to return the necessary data
***REMOVED***to populate the pie charts
@application.route('/ui/search/summary', methods=['GET','OPTIONS','POST'])
def get_ui_search_summary():

    url = "http://localhost:{0}/sum_schema".format(be_port)

    sum_gql = '''
        {0}(cy:"{1}") {{
            buckets {{
                case_count
                doc_count
                file_size
                key
            }}     
        }}
    '''  

    file_size_gql = '''
        fs(cy:"{0}") {{
            value
        }}
    ''' 

    empty_cy_gql = '''
    {{
        {0}
        {1}
        {2}
        {3}
        {4}
        {5}
        {6}
    }}
    '''.format(
        sum_gql.format("sample_body_site",""),
        sum_gql.format("project_name",""),
        sum_gql.format("subject_gender",""),
        sum_gql.format("file_format",""),
        sum_gql.format("file_type",""),
        sum_gql.format("study_name",""),
        file_size_gql.format("")
    )

    query = {'query':""}

    if request.get_data(): ***REMOVED***only modify call if filters arg is present
        f1 = request.get_data()
        f2 = json.loads(f1)

        if f2['filters']:

            filters = json.dumps(f2['filters'])
            filters = convert_gdc_to_osdf(filters)

            query['query'] = '''
            {{
                {0}
                {1}
                {2}
                {3}
                {4}
                {5}
                {6}
            }}
            '''.format(
                sum_gql.format("sample_body_site",filters),
                sum_gql.format("project_name",filters),
                sum_gql.format("subject_gender",filters),
                sum_gql.format("file_format",filters),
                sum_gql.format("file_type",filters),
                sum_gql.format("study_name",filters),
                file_size_gql.format(filters)
            )

        else:
            query['query'] = empty_cy_gql

    else:
        query['query'] = empty_cy_gql

    response = json.load(urllib2.urlopen(url,data=urllib.urlencode(query)))
    data = json.dumps(response['data'])
    return make_json_response(data)

@application.route('/status/api/manifest', methods=['GET','OPTIONS','POST'])
def get_manifest():
    string = 'id\tmd5\tsize\turls' ***REMOVED***header
    ids = request.form.getlist('ids')
    data = get_manifest_data(ids) ***REMOVED***get all the relevant properties for this file
    
    for result in data:
        string += result

    response = make_response(string)

    ***REMOVED***If we've processed the data, reset the cookie key for the cart.
    cookie = request.form.get('downloadCookieKey')
    response.set_cookie(cookie,'',expires=0)
    
    response.headers["Content-Disposition"] = "attachment; filename=hmp_cart_{0}.tsv".format(cookie)
    return response

@application.route('/status/api/token', methods=['GET','OPTIONS','POST'])
def get_token():
    ids = request.form.getlist('ids')
    token = get_manifest_token(ids) ***REMOVED***get all the relevant properties for this file
    return token ***REMOVED***need to decide how to communicate the token to the user

@application.route('/client/token', methods=['GET','POST','OPTIONS'])
def handle_client_token():

    cart = token_to_manifest(request.form.get('token'))
    response = make_json_response(cart)
    return response

***REMOVED***Function to add a JSON content type to the response, takes in the data that 
***REMOVED***is to be returned
def make_json_response(data):
    response = make_response(data)
    response.headers['Content-Type'] = 'application/json'
    return response

application.add_url_rule(
    '/sum_schema',
    view_func=GraphQLView.as_view(
        'sum_graphql',
        schema=sum_schema,
        graphiql=True
    )
)

application.add_url_rule(
    '/ac_schema',
    view_func=GraphQLView.as_view(
        'ac_graphql',
        schema=ac_schema,
        graphiql=True
    )
)

application.add_url_rule(
    '/files_schema',
    view_func=GraphQLView.as_view(
        'files_graphql',
        schema=files_schema,
        graphiql=True
    )
)

application.add_url_rule(
    '/table_schema',
    view_func=GraphQLView.as_view(
        'table_graphql',
        schema=table_schema,
        graphiql=True
    )
)

application.add_url_rule(
    '/indiv_files_schema',
    view_func=GraphQLView.as_view(
        'indiv_files_graphql',
        schema=indiv_files_schema,
        graphiql=True
    )
)

application.add_url_rule(
    '/indiv_sample_schema',
    view_func=GraphQLView.as_view(
        'indiv_sample_graphql',
        schema=indiv_sample_schema,
        graphiql=True
    )
)

if __name__ == '__main__':
    application.run(threaded=True,host='0.0.0.0',port=int(be_port))
