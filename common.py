import os

class File():
    def __init__(self, path, item_id = None, parent_id = None):
        """
        Initizalize the file information

        Args:
            dir: reMarkable directory
        """

        self.path = path
        self.id = item_id
        self.parent = parent_id

def list_local_files(directory):
    """
    List all the files in a local directory

    Args:
        directory: local directory

    Returns: list of files in the local directory
    """

    list_of_files = []

    for path, dir, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(*path.split('/'), file)
            list_of_files.append(file_path)

    return list_of_files

def compare(a, b):
    """
    Compare two lists

    Args:
        a: list a
        b: list b

    Returns: list of values stored
             only in the list a and
             only in the list b
    """

    return (list(set(a) - set(b)), list(set(b) - set(a)))
