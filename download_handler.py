import json
from flask import make_response
from query import get_manifest_data, get_metadata

from manifest_handler import ManifestHandler

class DownloadHandler(ManifestHandler):
    """
    Returns manifest and metadata file data to download files to user's computer.

    """
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
