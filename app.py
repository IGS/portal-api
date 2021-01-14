#!/usr/bin/env python

# simple app to allow GraphiQL interaction with the schema and verify it is
# structured how it ought to be.
from shutil import Error
from flask import Flask, jsonify, request, redirect, jsonify, make_response, render_template, flash, abort, send_from_directory
from flask.views import MethodView

from query import get_urls_for_download, cache_facet_counts
from query import get_front_page_bar_chart_data, get_all_study_data
from query import get_front_page_example_query_data
from query import token_to_manifest, get_study_sample_counts
from query import get_sample_hits, get_file_hits, get_facet_counts
import query
from conf import access_origin, be_port, secret_key, JSON_OUTDIR
import graphene
import json, re
import mysql.connector, hashlib
from flask_cors import CORS
from lib import mysql_fxns
from aws_util import download_manifest
import uuid, os
from config_utils import load_config

#load model_metadata mapping
from metadata_mapping import metadata_mapping as METADATA_MAPPING

from flask_caching import Cache
config = { "CACHE_TYPE": "simple" }


application = Flask(__name__)
application.config.from_mapping(config)
application.secret_key = secret_key
application.cache = Cache(application)

# Set to True to see print statements in log file
application.debug = True
CORS(application, origins=access_origin, supports_credentials=True, methods=['GET','OPTIONS','POST'])

# pdata = get_all_proj_data() #DOlley removed because it's not used. remaining as precaution
bar_graph_data = get_front_page_bar_chart_data()
sdata_counts = get_study_sample_counts()


@application.before_first_request
def initialize_cache():
    config = load_config(file_name='config.json')
    build_cache = config['site-wide']['build-cache-on-first-request'] if "build-cache-on-first-request" in config else False 
    if build_cache:
        cache_facet_counts()
    
@application.before_request
def before():
    if request.method == 'OPTIONS':
        return 'OK'

@application.route('/gql/_mapping', methods=['GET','OPTIONS','POST'])
def get_maps():
    # consider anything in model_metadata_mapping as searchable
    return jsonify(dict(METADATA_MAPPING))

@application.route('/home_example_queries', methods=['GET','OPTIONS','POST'])
def get_example_query_results():
    results = get_front_page_example_query_data()
    data_wrapped = {'data': results}
    data = json.dumps(data_wrapped) #json.dumps will escape the ", but this will broke the link 
    return make_json_response(data)


# Route for specific cases endpoints that associates with various files
@application.route('/samples/<case_id>', methods=['GET','OPTIONS','POST'])
def get_case_files(case_id):
    
    data = query.get_subject_sample(case_id)
    data.update(query.get_files(case_id))
    data = { "data": data }
    #data["data"][]
    #["files"] = files
    data = json.dumps(data, indent=2)
    return make_json_response(data)

    
@application.route('/files/<file_id>', methods=['GET','OPTIONS','POST'])
def get_file_metadata(file_id):

    result = query.get_file_data(file_id)
    data = json.dumps(result, indent=2)
    return make_json_response(data)

@application.route('/login', methods=['GET','OPTIONS','POST'])
def login():
    error = None

    if request.method == 'POST':

        username = request.form['username']

        pw = mysql_fxns.login(username)

        sha1_pw = hashlib.sha1(request.form['password']).hexdigest()

        if sha1_pw != pw:
            error = 'Invalid credentials'
        elif pw and sha1_pw == pw: # don't allow null=null
            new_session = mysql_fxns.establish_session(username)
            response = make_response(redirect(access_origin[0]))
            response.set_cookie('csrftoken',new_session)
            return response

    return render_template('login.html',error=error)

@application.route('/status/logout', methods=['GET','OPTIONS','POST'])
def logout():

    # nullify all the info both in MySQL and stored in the UI for this session
    mysql_fxns.disconnect_session(request.cookies['csrftoken'])
    response = make_response(redirect(request.referrer))
    response.set_cookie('csrftoken','')

    return response

@application.route('/status', methods=['GET','OPTIONS','POST'])
def get_status():
    return 'OK'

def unauthorized(message):
    response = jsonify({'message': message})
    response.status_code = 401
    return response

@application.route('/status/user', methods=['GET','OPTIONS','POST'])
def get_status_user_unauthorized():

    if 'HTTP_X_CSRFTOKEN' in request.environ:
        if request.environ['HTTP_X_CSRFTOKEN']:

            response = '''
                {{
                    "username": "{0}",
                    "projects": {{
                        "gdc_ids": {{
                            "TCGA-LAML": []
                        }}
                    }},
                    "queries": {1},
                    "hrefs": {2},
                    "scounts": {3},
                    "fcounts": {4},
                    "comments": {5},
                    "timestamps": {6}
                }}
            '''

            user_info = mysql_fxns.get_user_info(request.environ['HTTP_X_CSRFTOKEN'])
            if user_info is not None:
                if user_info['username'] != "": # if successfully logged in, should be in DB
                    return make_json_response(
                        response.format(user_info['username'],
                            json.dumps(user_info['queries']),
                            json.dumps(user_info['hrefs']),
                            json.dumps(user_info['scounts']),
                            json.dumps(user_info['fcounts']),
                            json.dumps(user_info['comments']),
                            json.dumps(user_info['timestamps'])
                            )
                        )

    return 'Not yet logged in'


# @application.route('/status/api/data', methods=['GET','OPTIONS','POST'])
# def get_status_api_data():
#     id = request.form.get('ids')
#     #ids = request.form.getlist('ids') # need to figure out how to bundle
#     return redirect(get_url_for_download(id))

@application.route('/status/api/data', methods=['GET','OPTIONS','POST'])
def get_status_api_data():
    cookie = request.form.get('downloadCookieKey')
    try:
        ids = request.get_json()['ids']
    except:
        ids = request.form.getlist('ids')

    if len(ids) == 1:
        # Only 1 file to download
        file_url = get_urls_for_download(ids)[0]

        # Wrap the redirect in a response to reset cookie (prevents inappropriate UI error popup)
        response = make_response(redirect(file_url))

        # Reset the cookie
        if cookie:
            response.set_cookie(cookie, '', expires=0)

        return response

    else: 
        # Multiple files to download
        print("IDS: ", ids)
        
        # Get File download URLs
        download_urls = get_urls_for_download(ids)
        print "download_urls: ", download_urls

        # Download token - use the request cookie or create uuid snippet
        #  - This is returned to UI and later used to check the download's status
        token = cookie if cookie else str(uuid.uuid4()).rsplit("-")[-1] #use cookie or last group of uuid
        print("TOKEN: ", token)

        print("Token '%s' sending request..." % token)

        # Send task to server
        data = {'token': token, 'urls': download_urls}

        # Initialize the multifile downloader plugin.
        #  As currently implemented, this will only run the QueueClient class, which submits
        #  the token and download urls to the queue.
        from plugin_collection import PluginCollection
        mfd_plugin = PluginCollection('plugins.multifile_downloader') #only load MFD plugin
        mfd_plugin.apply_all_plugins_on_value(data)

        print("Delivered token %s with %s urls." % (token, str(len(download_urls))) )

        
        response = make_response(json.dumps({"data": {"download_token": token}}))
        
        # Reset cookie to satisfy UI side of downloader. Prevents the inappropriate trigger of error alert
        if cookie:
            response.set_cookie(cookie, '', expires=0)

        return response


@application.route('/check_download_status', methods=['GET','OPTIONS','POST'])
def get_tarball_status():
    is_complete = False
    # Get token from request
    download_token = request.get_json()['download_token']

    try:
        from plugins.multifile_downloader import download_checker

        dc = download_checker.DownloadChecker()

        # First check that an error-tagged file was not created by queue_server
        # This is an empty file that the queue_server creates to communicate that the download failed.
        download_failed = dc.check_error_file(download_token)
        # import time
        # time.sleep(5)
        if download_failed:
            # An error file was found. Exit now.
            return make_response(json.dumps({"error": "Failed to build download file."}))


        (is_complete, file_url) = dc.check_download_status(download_token)
        
        if is_complete:
            response = make_response(json.dumps({"data": {"is_download_complete": is_complete, "file_url": file_url}}))
        else:
            response = make_response(json.dumps({"data": {"is_download_complete": is_complete}}))

    except Error as e:
        print("Caught error: ")
        print(e)
        response = make_response(json.dumps({"error": "Failed to check status of download file."}))
        # response = make_response({"error": e })
        # response.headers["status"] = 500

    return response


# Developing a parallel track for the /cases route to migrate it off of the hard-coded GQL query
@application.route('/samples', methods=['GET','OPTIONS','POST'])
def get_samples():
    

    # Copied from get_cases(), but unsure why this is needed
    if not request.args:
        return 'placeholder' # return a value when the cart page sends no args
    
    filters = request.args.get('filters')
    
    #TODO: mschor: Need to figure out why facets filters are coming through prefixed with "cases." and get rid of that
    if filters is not None:
        filters = filters.replace("cases.","")
        filters = filters.replace("files.","")
    else:
        filters = ""

    #mschor: not sure where this comes from, but handle it
    if filters == "{}":
        filters = ""
        
    unmodified_filters = filters
    from_num = request.args.get('from')
    from_str = from_num
    size = request.args.get('size')
    order = request.args.get('sort')

    if request.get_data():
        f1 = request.get_data()
        f2 = json.loads(f1)
        #filters = f2['filters']
        from_str = f2['from']
        order = f2['sort']
        size = f2['size']
        #filters = json.dumps(filters)

    if not from_str:
        from_str = "0"
        
    try:
        #if type(from_str) == int:
        from_num = int(from_str)
    except ValueError:
        from_num = 0
    
    facets_param = ""
    if request.args.get('facets'):
        facets_param = request.args.get('facets')
        facets_param = facets_param.replace("cases.", "")
        facets_param = facets_param.replace("files.", "")
        
    result = get_sample_hits(size, order, from_num, filters, facets_param.split(","))
    
    # if aggregations not yet calculated, get defaults
    if "aggregations" not in result["data"]:
        result["data"].update(get_facet_counts(facets_param.split(",")))
    
    data = json.dumps(result, indent=2)

    save_query = request.args.get('save') # saving query
    comment = request.args.get('comment') # adding custom comment to query
    if save_query and save_query == 'yes':
        if 'HTTP_X_CSRFTOKEN' in request.environ:

            # Not sure what's up with the JSON lib and parsing this, just
            # hacking at it for now. Should render an exact copy of what
            # displays in the advanced query input box.
            query = re.search(r'query":"(.*)"}',unmodified_filters.replace('\\','')).group(1)

            mysql_fxns.save_query_sample_data(request.environ['HTTP_X_CSRFTOKEN'],
                request.environ['HTTP_REFERER'],
                query,
                re.search(r'"total":(\d+)',data).group(1)
            )

    elif comment:
        query = re.search(r'query":"(.*)"}',unmodified_filters.replace('\\','')).group(1)
        mysql_fxns.save_query_comment_data(request.environ['HTTP_X_CSRFTOKEN'],
            query,
            comment
        )

    return make_json_response(data)


@application.route('/files', methods=['GET','OPTIONS','POST'])
def get_files():

    #TODO: mschor: So much of get_samples and get_files functions is similar; break out into smaller functions
    filters = request.args.get('filters')

    #TODO: mschor: Need to figure out why facets filters are coming through prefixed with "cases." and get rid of that
    if filters is not None:
        filters = filters.replace("cases.","")
        filters = filters.replace("files.","")
    else:
        filters = ""


    #mschor: not sure where this comes from, but handle it
    if filters == "{}":
        filters = ""
        
    unmodified_filters = filters
    from_num = request.args.get('from')
    from_str = from_num
    
    
    size = request.args.get('size')
    order = request.args.get('sort')
    
    # This apparently means it's a POST
    if request.get_data():        
        f1 = request.get_data()
        f2 = json.loads(f1)
        filters = f2['filters']
        from_str = f2['from']
        order = f2['sort']
        size = f2['size']
        filters = json.dumps(filters)

    if not from_str:
        from_str = "0"

    try:
        #if type(from_str) == int:
        from_num = int(from_str)
    except ValueError:
        from_num = 0
    
    facets_param = ""
    if request.args.get('facets'):
        facets_param = request.args.get('facets')
        
    if type(from_str) == int:
        from_num = int(from_str)
    result = get_file_hits(size, order, from_num, filters, facets_param.split(","))
    
        
    # if aggregations not yet calculated, get defaults
    if "aggregations" not in result["data"]:
        result["data"].update(get_facet_counts(facets_param.split(",")))        
    
    data = json.dumps(result, indent=2)

    save_query = request.args.get('save')
    if save_query and save_query == 'yes':
        mysql_fxns.save_query_file_data(request.environ['HTTP_X_CSRFTOKEN'],
            request.environ['HTTP_REFERER'],
            re.search(r'"total":(\d+)',data).group(1)
        )

    return make_json_response(data)


# Get data for table and piecharts on projects ("Studies") page 
@application.route('/projects', methods=['GET','OPTIONS','POST'])
def get_projects():
    from_num = request.args.get('from')
    from_str = from_num
    size = request.args.get('size')
    order = request.args.get('sort')

    if not from_str:
        from_str = "0"
        
    try:
        from_num = int(from_str)
    except ValueError:
        from_num = 0

    studies_data = get_all_study_data(size, order, from_num)

    np = len(studies_data)

    p_str = "{{ \"count\": {0}, \"sort\": \"\", \"from\": 1, \"page\": 1, \"total\": {1}, \"pages\": 1, \"size\": 100 }}".format(np, np)
    hit_str = json.dumps(studies_data)
    data = ("{{\"data\" : {{\"hits\" :  {0} , \"pagination\": {1}}}, \"warnings\": {{}}}}".format(hit_str, p_str))

    return make_json_response(data)


#Get data for bargraph on home page
@application.route("/projects_graph_data", methods=['GET','OPTIONS','POST'])
def get_projects_visualization_data():
    graph_type = request.args.get('graph_type')

    if graph_type == 'bar_graph':
        graph_data_length = len(bar_graph_data)

        p_str = "{{ \"count\": {0}, \"sort\": \"\", \"from\": 1, \"page\": 1, \"total\": {1}, \"pages\": 1, \"size\": 100 }}".format(graph_data_length, graph_data_length)
        counts = {}
        hit_list = []

        config = load_config(file_name='config.json')

        for row in bar_graph_data:
            bar_segment_tip = row[config['search']['barchart-config']['data-tooltip-label']]
            x_labels = row[config['search']['barchart-config']['x-axis-labels']]
            n_files = row["file_count"]
            n_cases = row["case_count"]
            if x_labels is None:
                x_labels = "None"
            if x_labels in counts:
                counts[x_labels] = counts[x_labels] + 1
            else:
                counts[x_labels] =  1
            hit_list.append({"x_axis" : x_labels, "bar_segment_tip": bar_segment_tip , "summary": { "case_count": n_cases, "file_count": n_files} })

        buckets_list = []
        for ckey in counts:
            ccount = counts[ckey]
            buckets_list.append({ "key": ckey, "doc_count": ccount})

        buckets_str = json.dumps(buckets_list)
        hit_str = json.dumps(hit_list)
        agg_str = "{{ \"x_labels\": {{ \"buckets\": {0} }}}}".format(buckets_str)

        data = ("{{\"data\" : {{\"aggregations\": {0}, \"hits\" : {1}, \"pagination\": {0}}}, \"warnings\": {{}}}}".format(agg_str, hit_str, p_str))
        return make_json_response(data)


@application.route('/annotations', methods=['GET','OPTIONS','POST'])
def get_annotation():
    return 'placeholder' # trimmed endpoint from GDC, not using for now

# Calls sum_schema endpoint/GQL instance in order to return the necessary data
# to populate the pie charts
@application.route('/ui/search/summary', methods=['GET','OPTIONS','POST'])
def get_ui_search_summary():
    
    filters = ""
    if request.method == 'POST':
        post_dict = json.loads(request.get_data())
        if post_dict['filters']:
            filters = json.dumps(post_dict['filters'])
        
    data = query.get_pie_chart_summary(filters)

    summary = { 'fs': {}, 'charts': [] }
    summary['fs'] = data['fs']
    summary['charts'] = data['charts']

    #sort the pie charts
    from operator import itemgetter
    summary['charts'] = sorted(summary['charts'], key=itemgetter('id'))

    data = json.dumps(summary)
    return make_json_response(data)

# NOTE: Used later for downloading manifest once user is 'in cloud' by utility:
#       https://github.com/dcppc-phosphorous/manifest-downloader
#       Currently used for DCPPC which runs on AWS
@application.route('/manifest/download', methods=['GET'])
def retrieve_manifest():
    id = request.args.get('id')
    try:
        manifest = download_manifest(id)
        response = make_response(manifest)
        response.headers["Content-Disposition"] = "attachment; filename={0}".format(id)
    except Error as e:
        print ("Caught error: ")
        print (e)
        response = make_response("Error occurred. Invalid ID")
        response.headers["status"] = 404
    return response

@application.route('/status/api/manifest', methods=['GET','OPTIONS','POST'])
def get_manifest():
    file_to_retrieve = 'manifest'
    config = load_config(file_name='config.json')
    module_name = config['cloud-options']['service-name'] + '_handler'        # aws_handler, download_handler
    class_name = config['cloud-options']['service-name'].title() + 'Handler'  # AwsHandler, #DownloadHandler
    handler = None

    import importlib
    module = importlib.import_module(module_name)
    handler_class = getattr(module, class_name)
    handler = handler_class(file_to_retrieve=file_to_retrieve)

    if config['cloud-options']['service-name'].lower() == 'aws':
        # AWS returns a manifest ID {'manifest_id': 'xxx-xxxxxxx-xxxx-xxxxx'}
        return handler.handle_manifest(request)
    else:
        # Download the file
        file_data = handler.handle_manifest(request)
        return handler.download_file(request, file_data)


@application.route('/status/api/files', methods=['GET','OPTIONS','POST'])
def get_cart_metadata():
    file_to_retrieve = 'metadata'
    config = load_config(file_name='config.json')
    module_name = config['cloud-options']['service-name'] + '_handler'        # aws_handler, download_handler
    class_name = config['cloud-options']['service-name'].title() + 'Handler'  # AwsHandler, #DownloadHandler
    handler = None

    import importlib
    module = importlib.import_module(module_name)
    handler_class = getattr(module, class_name)
    handler = handler_class(file_to_retrieve=file_to_retrieve)

    if config['cloud-options']['service-name'].lower() == 'aws':
        # AWS returns a manifest ID {'manifest_id': 'xxx-xxxxxxx-xxxx-xxxxx'}
        return handler.handle_metadata(request)
    else:
        # Download the file
        metadata = handler.handle_metadata(request)
        return handler.download_file(request, metadata)


@application.route('/status/api/terra', methods=['GET','OPTIONS','POST'])
def send_to_terra():
    """Send manifest data to Terra data framework.  Returns URL to UI that will open in new window."""
    file_to_retrieve = 'terra'  #dummy value to prevent erroring out
    config = load_config(file_name='config.json')
    module_name = config['cloud-options']['service-name'] + '_handler'        # aws_handler, download_handler
    class_name = config['cloud-options']['service-name'].title() + 'Handler'  # AwsHandler, #DownloadHandler
    handler = None

    import importlib
    module = importlib.import_module(module_name)
    handler_class = getattr(module, class_name)
    handler = handler_class(file_to_retrieve=file_to_retrieve)

    file_data = handler.handle_manifest(request)
    metadata = handler.handle_metadata(request)
    json_entities = handler.build_json(file_data, metadata)
    return handler.post_json_to_terra(json_entities)

@application.route('/status/api/terra/<manifest_id>', methods=['GET','OPTIONS','POST'])
def export_to_terra(manifest_id):
    config = load_config(file_name='config.json')
    abbr = config['site-wide']['project-abbr'].lower()
    return send_from_directory(JSON_OUTDIR, "{}_{}.json".format(abbr, manifest_id))


@application.route('/status/api/token', methods=['GET','OPTIONS','POST'])
def get_token():
    ids = request.form.getlist('ids')
    token = get_manifest_token(ids) # get all the relevant properties for this file
    return token # need to decide how to communicate the token to the user

@application.route('/client/token', methods=['GET','OPTIONS','POST'])
def handle_client_token():

    cart = token_to_manifest(request.form.get('token'))
    response = make_json_response(cart)
    return response

@application.route('/custom', methods=['GET', 'OPTIONS', 'POST'])
def get_config_custom():
    # Read the custom configuration file and pass it to AngularJS service config.service.ts
    config = load_config(file_name='config.json')
    if config is None:
        response = json.dumps({'error': 'Unable to read config.json'})
    else:
        response = json.dumps(config)

    return make_json_response(response)


# Function to add a JSON content type to the response, takes in the data that
# is to be returned
def make_json_response(data):
    response = make_response(data)
    response.headers['Content-Type'] = 'application/json'
    return response

if __name__ == '__main__':
    #application.run(threaded=True,host='0.0.0.0',port=int(be_port))
    # application.run(host='0.0.0.0',port=int(be_port))
    print('be_loc: ', be_loc)
    # application.run(host=be_loc,port=int(be_port), extra_files=['./config.ini', './models_metadata.ini'])
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_ini_filepath = os.path.join(dir_path, 'config.ini')
    metadata_filepath = os.path.join(dir_path, 'models_metadata.yml')
    facets_filepath = os.path.join(dir_path, 'facets.yml')
    application.run(host=be_loc,port=int(be_port), extra_files=[config_ini_filepath, metadata_filepath, facets_filepath])    
