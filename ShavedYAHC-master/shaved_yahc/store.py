# vim: set tw=99:

import json
import os

class YAHCStore:
    '''Represents a file system based data store.

    User Attributes:
        store_location -- str
            Absolute path to the store directory on the file system.
    '''

    def __init__(self, store_location):
        self.store_location = store_location
        os.makedirs(store_location)

    def get_path(self, name):
        '''Get the path to an item in the data store.

        Parameters:
            name -- str
                A file system safe item name.

        Returns -- str
            The path to the item in the file system.
        '''
        return os.path.join(self.store_location, name)

    def add_store(self, name):
        '''Add a nested sub-store to this data store.

        Parameters:
            name -- str
                A file system safe item name.

        Returns -- YAHCStore
            The new nested sub-store.
        '''
        return YAHCStore(self.get_path(name))

    def add_blob(self, name, mode='b', encoding=None):
        '''Add a blob to this data store.

        Parameters:
            name -- str
                A file system safe item name.
            mode -- str
                File mode; e.g., 'b' for binary, 't' for text.
            encoding -- str or None
                Text encoding; e.g., 'utf-8'.

        Returns -- file
            An opened file for the new blob.
        '''
        return open(self.get_path(name), 'x{}'.format(mode), encoding=encoding)

    def add_binary_blob(self, name, buf):
        '''Add a binary blob to this data store.

        Parameters:
            name -- str
                A file system safe item name.
            buf -- bytes
                Bytes to write to the blob.
        '''
        with self.add_blob(name) as blob_file:
            blob_file.write(buf)

    def add_text_blob(self, name, text):
        '''Add a text blob to this data store.

        Parameters:
            name -- str
                A file system safe item name.
            text -- str
                Text to write to the blob.
        '''
        with self.add_blob(name, mode='t', encoding='utf-8') as blob_file:
            blob_file.write(text)

    def add_json_blob(self, name, value):
        '''Add a JSON blob to this data store.

        Parameters:
            name -- str
                A file system safe item name.
            value -- any JSON-encodable value
                Value to write as JSON to the blob.
        '''
        with self.add_blob(name, mode='t', encoding='utf-8') as blob_file:
            json.dump(value, blob_file)
