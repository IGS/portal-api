#!/usr/bin/env python

"""
    Script to generate content for the controlled vocabulary table in the README.md.
    Uses dictionaries that are used to harmonize values during the conversion of 
    OSDF documents to their Neo4j representation. Requires to be in the same location
    as https://github.com/jmatsumura/HMP_database_builder/blob/master/accs_for_couchdb2neo4j.py
    in order to take in these dicts and parse them to generate a map of the 
    values as they go from OSDF to Neo4j.  

    Author: James Matsumura
    Contact: jmatsumura@som.umaryland.edu
"""

import argparse
from collections import defaultdict
from accs_for_couchdb2neo4j import fma_free_body_site_dict, study_name_dict

def main():

    parser = argparse.ArgumentParser(description='Script to isolate the properties from the currently active GQL map and put them in the README.')
    parser.add_argument('--outfile', '-o', type=str, help='Name of the outfile to populate content with.')
    args = parser.parse_args()

    with open(args.outfile,'w') as output:

        study,body_site = (defaultdict(list) for i in range(2))
        for k,v in study_name_dict.items():
            study[v].append(k) 

        for k,v in fma_free_body_site_dict.items():
            study[v].append(k) 

        for k in sorted(study):
            output.write('| {} | {} |\n'.format(k,(',').join(study[k])))

        for k in sorted(body_site):
            output.write('| {} | {} |\n'.format(k,(',').join(study[k])))


if __name__ == '__main__':
    main()