#!/usr/bin/env python

# Script to generate content for the Available Properties header in the README.
# Generates a file which can then be copied into the README. Be sure to move this

from autocomplete_map import gql_map
from collections import OrderedDict
import argparse,re

def main():

    parser = argparse.ArgumentParser(description='Script to isolate the properties from the currently active GQL map and put them in the README.')
    parser.add_argument('--app', '-a', type=str, help='Path to app.py which has the /gql/_mapping route.')
    parser.add_argument('--outfile', '-o', type=str, help='Name of the outfile to populate content with.')
    args = parser.parse_args()

    final_dict = {}

    with open(args.app,'r') as app:

        gql_section = False

        for line in app:
            if 'gql = jsonify({' in line:
                gql_section = True
            elif '})' in line:
                break
            elif gql_section:
                vals = map(str.strip,line.split(':'))
                prop = vals[0]
                key = re.search(r"\['([\w+\_+]+)\'\]",vals[1]).group(1)
                final_dict[prop] = gql_map[key]['description']

    
    sorted_dict = OrderedDict(sorted(final_dict.items()))

    with open(args.outfile,'w') as out:
        for k,v in sorted_dict.items():
            out.write("* {0} - {1}\n".format(k.replace('\"','**'),v))


if __name__ == '__main__':
    main()