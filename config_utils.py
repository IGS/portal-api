import ConfigParser
import json
import os

def load_config(file_name=None):

    """
    Loads a config file from it's INI or JSON format.

    If file_name = 'config.json'
     - Compares age of config json to age of config.ini and facets.yml.
        If config.ini or facets.yml has been more recently modified than 
        config.json, a new config.json will be generated.
     - Returns config as a json object.

    If file_name = 'config.ini'
     - Reads the config.ini.
     - Returns config as a ConfigParser object.
    """
    config = None

    # Get this script's current path to build paths of other config files
    dir_path = os.path.dirname(os.path.realpath(__file__))

    config_name = file_name.split(".")[0] 
    config_type = file_name.split(".")[1]

    ini_filepath = os.path.join(dir_path, config_name + '.ini')
    json_filepath = os.path.join(dir_path, config_name + '.json')
    facets_filepath = os.path.join(dir_path, 'facets.yml')
    
    if config_type == 'json':
        # Compares the ages of the json and ini files.
        #  Writes a new json if the ini was more recently modified
        #  Then reads the json and returns it as json object
        config_json_age = 0
        config_ini_age = float(os.path.getmtime(ini_filepath))
        facet_config_age = float(os.path.getmtime(facets_filepath))

        if os.path.exists(json_filepath): #json might not exist yet.
            config_json_age = float(os.path.getmtime(json_filepath))

        # Compare age of json to config.ini and facets.yml
        #   bigger number = older = most recently modified
        if config_ini_age > config_json_age or \
        facet_config_age > config_json_age:

            #Create new config.json file
            import convert_ini_to_json as ini2json
            ini2json.run(ini_filepath)

        # Read the custom config.json file
        with open(json_filepath) as f:
            config = json.load(f)

    elif config_type == 'ini':
        # Reads ini file and returns it as a ConfigParser Object
        config = ConfigParser.ConfigParser()
        config.read(ini_filepath)

    return config