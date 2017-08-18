#!/usr/bin/env python

***REMOVED***Script to generate content for the autocomplete_map.py file. This will parse 
***REMOVED***JSON files for the relevant description and name in order to generate the 
***REMOVED***necessary content to pass back to the user while they use advanced search. 

import argparse,re,json,os,collections

def main():

    parser = argparse.ArgumentParser(description='Script to parse through JSON files that contain information on searchable fields.')
    parser.add_argument('--json_dir', '-jd', type=str, required=True, help='Path to the directory holding the JSON files of interest.')
    parser.add_argument('--prefix', '-p', type=str, required=True, help='Prefix to prepend to any of these attributes. Should be a valid node type like project/visit/sample/etc.')
    parser.add_argument('--outfile', '-o', type=str, required=True, help='Name of the outfile to populate content with.')
    args = parser.parse_args()

    gql_entires = [] ***REMOVED***build this list as we find new entries

    for filename in os.listdir(args.json_dir):
        with open(os.path.join(args.json_dir,filename)) as data_file:

            data = json.load(data_file) ***REMOVED***grab the whole file as JSON
            if 'properties' in data:

                for prop in data['properties']: 

                    if data['properties'][prop]: ***REMOVED***only interate over those that contain types/descriptions
                        if 'properties' in data['properties'][prop]: ***REMOVED***has another step in, cover all of these
                            for pro in data['properties'][prop]['properties']:
                                field = "{0}_{1}_{2}".format(args.prefix,prop,pro)
                                information = build_information_dict(field,data['properties'][prop]['description'],data['properties'][prop]['properties'][pro]['type'])
                                gql_entires.append({field:information})

                        else:
                            field = "{0}_{1}".format(args.prefix,prop)
                            ***REMOVED***HRT aux schema has some inconcsistency with 'title' instead of 'description'
                            desc = data['properties'][prop]['description'] if 'description' in data['properties'][prop] else data['properties'][prop]['title']
                            information = build_information_dict(field,desc,data['properties'][prop]['type'])
                            gql_entires.append({field:information})


    with open(args.outfile,'w') as out:
        for entry in gql_entires: ***REMOVED***iterate over a list of dicts
            for field,info in entry.items():
                out.write("gql_map['{0}'] = {{\n".format(field))
                ***REMOVED***Print out the JSON but trim the beginning '{' since that is 
                ***REMOVED***accounted for in the previous line
                out.write("{0}\n".format(json.dumps(info,indent=4).replace('{\n','')))

***REMOVED***Function to build the information necessary to structure the data for the
***REMOVED***autocomplete_map.py data store. 
def build_information_dict(field,desc,attr_type):

    str_set = {'boolean','string'}

    info = collections.OrderedDict()

    info["description"] = desc
    info["doc_type"] = "cases" ***REMOVED***relic from GDC
    info["field"] = field.replace("_",".",1)
    info["full"] = field.replace("_",".",1)
    info["type"] = "string" if attr_type in str_set else "integer"

    return info

if __name__ == '__main__':
    main()