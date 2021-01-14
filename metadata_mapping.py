import os
from yaml import load, dump, YAMLError
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class MetadataMapping(object):
    #loads metadata mapping
    mapping = None
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'models_metadata.yml')

    with open(filepath, 'r') as stream:
        try:
            mapping = load(stream, Loader=Loader)['metadata_mapping']
        except YAMLError as exc:
            print(exc)


# Initialize the mapping here, and import this in other files when needed
metadata_mapping = MetadataMapping().mapping