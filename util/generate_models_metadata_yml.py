
from py2neo import Graph # Using py2neo v3 not v2
import sys, os
# To included parent dir with conf.py in it
sys.path.append(os.path.dirname(os.getcwd()))

from conf import neo4j_ip, neo4j_bolt, neo4j_http, neo4j_un, neo4j_pw

###############
# NEO4J SETUP #
###############

# Get all these values from the conf
neo4j_bolt = int(neo4j_bolt)
neo4j_http = int(neo4j_http)
cypher_conn = Graph(host=neo4j_ip,bolt_port=neo4j_bolt,http_port=neo4j_http,user=neo4j_un,password=neo4j_pw)



def get_all_property_keys_for_node_type(node_type):
    
    print("Getting keys...")
    keys = cypher_conn.run("MATCH (n:" + node_type + ") UNWIND keys(n) AS key RETURN collect(distinct key) as key_list").data()
    
    #keys is something like: [{u'key_list': [u'database', u'sample_accession', u'id', u'study_name', u'sample_accession_db']}]
    return keys[0]['key_list']
    
def get_node_labels():
    labels = cypher_conn.run("call db.labels()").data()
    label_list = [ subdict['label'] for subdict in labels ]
    return label_list

if __name__ == '__main__':
    
    header_line = ("# THIS FILE CAN BE AUTO-GENERATED (minus descriptions) USING util/generated_models_metadata_yml.py"
                  "" + os.linesep + os.linesep +
                  "metadata_mapping:" + os.linesep +
                  "# This section configures the following areas:" + os.linesep +
                  "# 1) UI - The autocomplete mapping for adding facets on the search page" + os.linesep + 
                  "# 2) API - Fields for Aggregations class in models.py" + os.linesep +
                  "# 3) API - Converting UI facet/field names to Neo4j cypher" + os.linesep
                  )
    
    
    """# Project props
       project_name: 
           cypher_field: "PS.project_name"
           description: "The name of the project within which the sequencing was organized"
           doc_type: "cases"
           field: "project_name"
           full: "project.name"
           type: "string"
    """
    
    yaml = "models_metadata.yml"
    try:
        yaml_file = open(yaml, 'w')
        yaml_file.write(header_line)
        
        node_types = get_node_labels()
        
        for label in node_types:
            yaml_file.write(os.linesep + "  # " + label + " props" + os.linesep)
            
            props = get_all_property_keys_for_node_type(label)
            if label == "sample" or label == "subject":
                doc = "cases"
            else:
                doc = "file"
            for prop in props:
                yaml_file.write("  " + prop + ":" + os.linesep)
                yaml_file.write('      cypher_field: "' + label + "." + prop + '"' + os.linesep)
                yaml_file.write('      description: ""' + os.linesep)
                yaml_file.write('      doc_type: "' + doc + '"' + os.linesep)
                yaml_file.write('      field: "' + label + "." + prop + '"' + os.linesep)
                yaml_file.write('      full: "' + prop + '"' + os.linesep)
                yaml_file.write('      type: "string"' + os.linesep + os.linesep)
                #print(label + " : " + str(props))
    finally:
        if yaml_file:
            yaml_file.close()
            
            
            
            
            
