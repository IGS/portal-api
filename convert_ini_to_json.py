#! /usr/bin/python
"""
Converts config.ini to config.json. Also brings in facets.yml.

"""
import ConfigParser
import json
import os, sys
import uuid

from yaml import load, dump, YAMLError
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

# These will be set as the main sections of the final config JSON
# For the most part, these are organized by UI components and are pulled out by
# each component as needed 
# UI components - navbar, home, projects, search, cart
#   site-wide - originated from the IGDCConfig in portal-ui/app.ts
JSON_SECTIONS = [
    'site-wide',
    'navbar',
    'home',
    'projects',
    'search',
    'cart',
    'cloud-options',
    'cases-page',
    'files-page',
    'search-advanced-query-page'
]

# List of keys whose values will not be copied over into the json output file
KEY_VALUES_TO_SCRUB = [
    'aws-api-key',
    'aws-secret-key',
    'aws-bucket-name',
    'aws-running-on-ec2'
]

def run(config_filepath):
    #Build filepaths
    dir_path = os.path.dirname(os.path.realpath(__file__))
    facets_filepath = os.path.join(dir_path, 'facets.yml')
    output_filepath = os.path.join(dir_path, 'config.json')

    # Read in file
    config = ConfigParser.ConfigParser()
    config.read(config_filepath)

    #Create main sections within json
    json_object = dict()
    for section in JSON_SECTIONS:
        json_object[section] = dict()

    sections = config.sections()

    for section in sections:
        if section in JSON_SECTIONS:
            key_vals = format_key_val_pairs( config.items(section) )

            if section == 'cart':
                #vals need split into a list
                key_vals['piechart-order'] = key_vals['piechart-order'].split(",")

            if section == 'site-wide':
                key_vals['subject-excluded-fields'] = key_vals['subject-excluded-fields'].split(',')
                key_vals['sample-excluded-fields'] = key_vals['sample-excluded-fields'].split(',')
                key_vals['file-excluded-fields'] = key_vals['file-excluded-fields'].split(',')
            
            json_object = add_key_vals_to_json_section(json_object, section, key_vals)

        elif 'home-summary-stat' in section:
            key_vals = format_key_val_pairs( config.items(section) )
            if 'summary-stat' not in json_object['home']:
                json_object['home']['summary-stat'] = list() 
            json_object['home']['summary-stat'].append(key_vals)

        elif 'home-example-query' in section:
            key_vals = format_key_val_pairs( config.items(section) )
            if 'example-queries' not in json_object['home']:
                json_object['home']['example-queries'] = list() 
            json_object['home']['example-queries'].append(key_vals)

        elif 'projects-table' in section:
            if 'projects-table' not in json_object['projects']:
                json_object['projects']['projects-table'] = dict()
                key_vals = format_key_val_pairs( config.items(section) )
                json_object['projects'] = add_key_vals_to_json_section(json_object['projects'], section, key_vals)

            if 'heading' in section:
                if 'headings' not in json_object['projects']['projects-table']:
                    json_object['projects']['projects-table']['headings'] = list()
                key_vals = format_key_val_pairs( config.items(section) )
                json_object['projects']['projects-table']['headings'].append(key_vals)
            
        elif 'projects-piechart' in section:
            if 'config' in section:
                if 'piechart-configs' not in json_object['projects']:
                    json_object['projects']['piechart-configs'] = list()

                key_vals = format_key_val_pairs( config.items(section) )
                json_object['projects']['piechart-configs'].append(key_vals)
            
        elif 'cases-table' in section:
            if 'cases-table' not in json_object['search']:
                json_object['search']['cases-table'] = dict()
                key_vals = format_key_val_pairs( config.items(section) )
                json_object['search'] = add_key_vals_to_json_section(json_object['search'], section, key_vals)

            if 'heading' in section:
                if 'headings' not in json_object['search']['cases-table']:
                    json_object['search']['cases-table']['headings'] = list()
                key_vals = format_key_val_pairs( config.items(section) )
                json_object['search']['cases-table']['headings'].append(key_vals)
                
        elif 'files-table' in section:
            if 'files-table' not in json_object['search']:
                json_object['search']['files-table'] = dict()
                key_vals = format_key_val_pairs( config.items(section) )
                json_object['search'] = add_key_vals_to_json_section(json_object['search'], section, key_vals)

            if 'heading' in section:
                if 'headings' not in json_object['search']['files-table']:
                    json_object['search']['files-table']['headings'] = list()
                key_vals = format_key_val_pairs( config.items(section) )
                json_object['search']['files-table']['headings'].append(key_vals)

        elif 'search-barchart-config' in section:
            key_vals = format_key_val_pairs( config.items(section) )
            json_object['search'] = add_key_vals_to_json_section(json_object['search'], 'barchart-config', key_vals)
            
        elif 'search-piechart' in section:
            if 'api' in section:
                key_vals = format_key_val_pairs( config.items(section) )
                
                #vals need split into a list
                key_vals['chart-order'] = key_vals['chart-order'].split(",")

                json_object['search'] = add_key_vals_to_json_section(json_object['search'], 'piechart-api', key_vals)

            elif 'count-queries' in section:
                key_vals = format_key_val_pairs( config.items(section) )
                json_object['search']['piechart-api'] = add_key_vals_to_json_section(json_object['search']['piechart-api'], 'count-queries', key_vals)
                
            elif 'config' in section:
                if 'piechart-configs' not in json_object['search']:
                    json_object['search']['piechart-configs'] = list()

                key_vals = format_key_val_pairs( config.items(section) )
                json_object['search']['piechart-configs'].append(key_vals)
                
        elif 'manifest-download' in section or 'metadata-download' in section:
            section_name = section.split('-col')[0]
            section_name_col = section_name + "-col"
            if section_name not in json_object['cart']:
                json_object['cart'][section_name] = dict()
                #key_vals = format_key_val_pairs( config.items(section) )
                #json_object['cart'] = add_key_vals_to_json_section(json_object['cart'], section, key_vals)
                
            if section_name_col in section:
                if 'cols' not in json_object['cart'][section_name]:
                    json_object['cart'][section_name]['cols'] = list()
                key_vals = format_key_val_pairs( config.items(section) )
                json_object['cart'][section_name]['cols'].append(key_vals)

        elif 'cases-page' in section or 'files-page' in section:
            if section.startswith('cases'):
                config_section = 'cases-page'
                subsection = section.split("cases-page-")[1]
            elif section.startswith('files'):
                config_section = 'files-page'
                subsection = section.split("files-page-")[1]

            # if 'properties-table' in section or 'data-information-table' in section:
            if 'table' in section:
                key_vals = format_key_val_pairs( config.items(section) )
                
                #vals need split into a list
                key_vals['human-readable'] = key_vals['human-readable'].split(",")
                key_vals['property-names'] = key_vals['property-names'].split(",")

                properties = list()
                for (field, prop) in zip(key_vals['human-readable'], key_vals['property-names']):
                    properties.append({'field': field, 'property': prop})

                json_object[config_section].update({subsection: properties})
            

    # Bring in the facets config
    facet_config = None
    with open(facets_filepath, 'r') as stream:
        try:
            facet_config = load(stream, Loader=Loader)
        except YAMLError as exc:
            print(exc)
    
    for section in facet_config:
        if section.startswith('projects'):
            json_object['projects'].update({ section: facet_config[section] })
        else:
            json_object['search'].update({ section: facet_config[section] })
    
    # Convert ident to uuid string
    ident_length = int(json_object['site-wide']['ident'])
    json_object['site-wide']['ident'] = str(uuid.uuid4())[ 0:ident_length ]

    # Get corresponding piechart-configs for cart
    cart_piechart_names = list()
    json_object['cart']['piechart-configs'] = list()
    for piechart in json_object['cart']['piechart-order']:
        key_vals = format_key_val_pairs(config.items(piechart))

        chart_index = int(piechart.rsplit("-", 1)[1]) - 1
        cart_piechart_names.append("chart" + str(chart_index))
        json_object['cart']['piechart-configs'].append(key_vals)

    #Overwrite piechart-order using names from Piecharts in models.py (chart3)
    json_object['cart']['piechart-order'] = cart_piechart_names

    # Convert to string and replace python booleans with javscript ones
    config_stringified = stringify_config(json_object)
    # print(json.dumps(config_stringified, indent=2))

    # Write config to JSON file
    with open(output_filepath, 'w') as of:
        json.dump(config_stringified, of, indent=2)


def format_key_val_pairs(key_vals):
    # key_vals = [('key', 'value'), ...]
    formatted_key_vals = dict()

    for pair in key_vals:
        formatted_key_vals[pair[0]] = pair[1]

    return formatted_key_vals

def add_key_vals_to_json_section(json_obj, section, key_vals):
    if section not in json_obj:
        json_obj[section] = dict()
    for key, val in key_vals.iteritems():
        json_obj[section][key] = val if key not in KEY_VALUES_TO_SCRUB else "" 
    
    return json_obj

def stringify_config(config=None):
    config_str = json.dumps(config, indent=2, sort_keys=True,)

    # Replace python booleans with javscript ones
    config_str = config_str.replace('None', 'null')
    config_str = config_str.replace('"False"', 'false').replace("'False", "false")
    config_str = config_str.replace('"True"', 'true').replace("'True", "true")
    config_str = config_str.replace("\\\\t", "\\t") #remove the extra backslash in tabs \t file headers 

    return json.loads(config_str)
