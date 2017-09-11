#!/usr/bin/env python

# Script to generate content for three files:
# README - Available Properties section
# ac_schema.py - Content for both preloading and dynamic aggregations
# Also can be toggled to generate models of the Aggregations GQL object. 
# Generates content in a file can then be migrated over to one of those two locs.

from autocomplete_map import gql_map
import argparse

def main():

    parser = argparse.ArgumentParser(description='Script to isolate the properties from the currently active GQL map and put them in the README.')
    parser.add_argument('--which_file', type=str, help='Specify "readme" / "gql" / "ac" to generate content for that file.')
    parser.add_argument('--outfile', type=str, help='Name of the outfile to populate content with.')
    args = parser.parse_args()


    with open(args.outfile,'w') as out:
        if args.which_file == 'readme':
            for k in sorted(gql_map):
                out.write("* {} - {}\n".format(k.replace('\"','**'),gql_map[k]['description']))
        
        elif args.which_file == 'gql':
            for k in sorted(gql_map):
                out.write('{0} = graphene.Field(BucketCounter, name="{0}")\n'.format(k))

        elif args.which_file == 'ac':

            # first generate the top content
            rename_us = {
                'project': ['project_','PS.project_'],
                'sample': ['sample_','VSS.'],
                'study': ['study_','VSS.study_'],
                'subject': ['subject_','PS.'],
                'visit': ['visit_','VSS.visit_'],
                'file': ['file_','F.'],
                'tag': ['tag_','T.']
            }

            for k in sorted(gql_map):
                renamed_vals = k
                if not k.startswith('file') and not k.startswith('tag'): # outside of file
                    eles = k.split('_')
                    renamed_vals = k.split('_')[0][:3]+'_'+('_').join(k.split('_')[1:])  

                cypher = ""

                for ke,va in rename_us.items():

                    if k.startswith(ke):
                        cypher = k.replace(va[0],va[1],1)
                        break    

                out.write('{} = get_buckets("{}","no","")\n'.format(renamed_vals,cypher))         

            out.write('\n\nBREAK\n\n')

            # now print out the content to go in the resolve_aggregations
            for k in sorted(gql_map):
                renamed_vals = k
                if not k.startswith('file') and not k.startswith('tag'): # outside of file
                    eles = k.split('_')
                    renamed_vals = k.split('_')[0][:3]+'_'+('_').join(k.split('_')[1:]) 
                
                # subject is a bit of an exception and uses these for ID/UUID
                if k == 'subject_id':
                    renamed_vals = 'sub_rand_subject_id'
                elif k == 'subject_uuid':
                    renamed_vals = 'sub_id'

                out.write('{}={},\n'.format(k,renamed_vals))


if __name__ == '__main__':
    main()