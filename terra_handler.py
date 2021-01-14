#!/usr/bin/env python

""" terra_handler.py - Functions that aid in creating the JSON structure needed to send data to the Terra platform."""

import json
import uuid
import requests

from collections import defaultdict
from flask import make_response
from query import get_manifest_data, get_metadata
from manifest_handler import ManifestHandler

TERRA_FXN_URL = 'https://us-central1-broad-nemo-handoff-prod.cloudfunctions.net/build-terra-import'

def create_file_entity(headers, values):
    """Create JSON-based file entity structure to push into overall JSON structure."""
    file_entity = {
        "attributes": {},
        "entityType": "file",
    }
    for idx, val in enumerate(headers):
        if idx > 0:
            # Determine which URL to add
            if val == "urls":
                urls =  values[idx].split(',')    # Should be HTTPS url, and potentially a GCP one as well
                values[idx] = urls[0]
                for url in urls:
                    if 'gs:' in url:
                        values[idx] = url
                        continue
            file_entity["attributes"][val] = values[idx]
        else:
            file_entity["name"] = values[0]
    return file_entity

def create_sample_entity(headers, values):
    """Create JSON-based sample entity structure to push into overall JSON structure."""
    sample_entity = {
        "attributes": {},
        "entityType": "sample",
    }
    for idx, val in enumerate(headers):
        # Unicode to String
        val = str(val)
        values[idx] = str(values[idx])
        if idx > 0:
            sample_entity["attributes"][val] = values[idx]
        else:
            sample_entity["name"] = values[0]
    return sample_entity

def determine_component_headers(filetype):
    """Determine component file names to append to headers, given file type provided."""
    if filetype == "FASTQ":
        return ["r1_fastq", "r2_fastq", "i1_fastq", "i2_fastq", "barcodes_fastq"]
    elif filetype == "BAM":
        return ["bam", "bai"]
    elif filetype == "TSV":
        return ["tsv", "tsv_index"]
    elif filetype == "MEX":
        return ["mtx", "barcodes_tsv", "genes_tsv"]
    elif filetype == "FPKM":
        return ["isoforms_fpkm", "genes_fpkm"]
    elif filetype == "TABcounts":
        return ["col_counts", "row_counts", "mtx_counts", "exp_json"]
    elif filetype == "TABanalysis":
        return ["col_analysis", "row_analysis", "dimred"]

class TerraHandler(ManifestHandler):

    """Converts manifest and metadata into a JSON data structure that will be sent to the Terra platform."""

    def __init__(self, bundle_id=None, **kwargs):
       # initialize baseClass first
        super(TerraHandler, self).__init__(**kwargs)

        if bundle_id is None:
            bundle_id = str(uuid.uuid4())
        self.bundle_id = bundle_id

    def build_json(self, file_data, metadata):
        """Build JSON entity structure based on various manifest data."""
        entities = []    # Overall structure

        # Group files by file format
        files_by_type = defaultdict(list)
        for line in file_data.split("\n")[1:]:
            filetype = line.split("\t")[3]
            files_by_type[filetype].append(line)

        # Create file-set entities for each filetype present (still work in progress)
        #for filetype, lines in files_by_type.items():
            #for line in lines:

        # Create dicts from file names
        # Currently only operating on FASTQ files
        for line in files_by_type["FASTQ"]:
            file_headers = file_data.split("\n")[0].split("\t")
            values = line.split("\t")
            component_files = values.pop().split(";")
            # For FASTQ files, leave out files missing required component files (r1_fastq, r2_fastq)
            if component_files[0] == "NA" or component_files[1] == "NA":
                continue
            # Replace any "NA" values from component sections with a JSON null so the Cromwell system on Terra's side validates those fields as missing
            component_files[:] = [None if x == "NA" else x for x in component_files]
            file_headers.pop()	# Pop "components"
            component_headers = determine_component_headers(values[3])
            if component_headers:
                file_headers.extend(component_headers)
                values.extend(component_files)
            entities.append(create_file_entity(file_headers, values))

        # Create dicts from sample names
        samp_set = set(metadata.split("\n")[1:])    # Duplication of entities not allowed in Terra payload
        samp_headers = metadata.split("\n")[0].split("\t")
        samp_name = []
        for line in samp_set:
            values = line.split("\t")
            samp_name.append(values[0])
            # Add counter to sample name if sample_name is duplicated across non-unique sample metadata
            if samp_name.count(values[0]) > 1:
                values[0] = "{}.{}".format(values[0], samp_name.count(values[0]))
            entities.append(create_sample_entity(samp_headers, values))

        json_entity = {"entities":entities, "cohortName":self.bundle_id}
        #print(json_entity)
        # JSON structure is complete
        return json_entity

    def download_file(self, request, file_data):
        """Write data to downloadable file."""
        filename = self.file_name
        response = make_response(file_data)

       # If we've processed the data, reset the cookie key for the cart.
        cookie = request.form.get('downloadCookieKey')
        if cookie:
            response.set_cookie(cookie,'',expires=0)

            response.headers["Content-Disposition"] = "attachment; filename={0}_{1}.tsv".format(filename, cookie)
        else:
            response.headers["Content-Disposition"] = "attachment; filename={0}.tsv".format(filename)
        return response

    def handle_manifest(self, request):
        """Given IDs, return dict of file manifest information."""
        ids = ''
        if request.is_json:
            # IDs need to be in JSON
            ids = json.loads(request.data)['ids']
        else:
            ids = request.form.getlist('ids')
        return get_manifest_data(ids) # get all the relevant properties for this file

    def handle_metadata(self, request):
        """Given IDs, return dict of metadata information."""
        ids = ''
        if request.is_json:
            # IDs need to be in a list
            ids = json.dumps(json.loads(request.data)['ids'])
        else:
            filters = json.loads(request.form.get('filters')) # use json lib to parse the nested dict
            ids = json.dumps(filters['content'][0]['content']['value'])
        return get_metadata(ids)

    def post_json_to_terra(self, json_entities):
        """Send JSON payload to Terra servers via POST."""
        terra_fxn_url = TERRA_FXN_URL
        #print(json.dumps(json_entities))
        response = requests.post(terra_fxn_url, data=json.dumps(json_entities), headers={'Content-Type': 'application/json'})
        response_json = json.loads(response.text)
        #print(response_json)
        if "url" not in response_json:
            err_response = make_response(response_json["message"], 422)
            return err_response
        response_url = response_json["url"]
        return response_url
