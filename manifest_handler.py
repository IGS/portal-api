from abc import ABCMeta, abstractmethod
import os

class ManifestHandler(object):
    """
    Parent class containing abstract methods for handling metadata and manifest files.

    Arguments:
    file_to_retrieve - required. 'manifest' or 'metadata'. The file to be handled.

    file_name - optional. The name that will be assigned to the manifest/metadata file.
                    By default, this is found in config.ini.
    """

    __metaclass__ = ABCMeta

    def __init__(self, file_to_retrieve=None, file_name=None):
        # Build filepath to config file
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config_filepath = os.path.join(dir_path, 'config.ini')

        self.file_to_retrieve = file_to_retrieve
        self.file_name = file_name

        if self.file_to_retrieve is None:
            raise Exception('Error: No file given to retrieve. Choose: "manifest" or "metadata"')

        if self.file_to_retrieve == 'manifest' and self.file_name is None:
            import ConfigParser
            config = ConfigParser.ConfigParser()
            config.read(config_filepath)
            self.file_name = config.get('cart', 'manifest-filename')

        if self.file_to_retrieve == 'metadata' and self.file_name is None:
            import ConfigParser
            config = ConfigParser.ConfigParser()
            config.read(config_filepath)
            self.file_name = config.get('cart', 'metadata-filename')


    @abstractmethod
    def handle_manifest(self):
        #defined in child class
        pass

    @abstractmethod
    def handle_metadata(self):
        #defined in child class
        pass
