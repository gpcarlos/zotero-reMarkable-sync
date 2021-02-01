import os
import sys
from colorama import Fore, Style
from pyzotero import zotero
from pyzotero.zotero_errors import UserNotAuthorised
from common import File

class Zotero():

    def __init__(self, dir, zot_library_id, zot_api_key):
        """

        Initizalize the zotero instance

        Args:
            dir: local directory
            zot_library_id: zotero personal library id
            zot_api_key: zotero API Key

        """

        self.files = []
        self.dir = dir

        try:
            self.zot = zotero.Zotero(zot_library_id, 'user', zot_api_key)
            self.zot.top()

        except UserNotAuthorised as ex:
            print(Fore.RED +
                  "ERROR - Zotero API error... " +
                  "Please run ensure the details are correct\n" +
                  f"Zotero Library ID: {zot_library_id}\n" +
                  f"Zotero API Key: {zot_api_key}" +
                  Style.RESET_ALL)
            sys.exit(1)

    def path_to(self, collectionId):
        """

        Recursively gets the full path to the collection

        Args:
            collectionId: zotero collection ID

        Returns: string path to the collection

        """

        if collectionId:
            c = self.zot.collection(collectionId)
            return f"{self.path_to(c['data']['parentCollection'])}{c['data']['name']}/"
        else:
            return ""

    def fetch(self):
        """

        Fetch all the .pdf file stored in the Zotero library.

        Returns: True is success, False otherwise

        """

        self.files = []

        for c in self.zot.all_collections():
            if c['meta']['numItems'] > 0:
                collection_name = c['data']['name']
                parent_path = self.path_to(c['data']['parentCollection'])
                path = os.path.join(parent_path, collection_name)

                for item in self.zot.collection_items(c['key']):
                    if item['data']['itemType'] == 'attachment':
                        file_name = item['data']['title']

                        if '.pdf' in file_name:
                            file_path = os.path.join(path, file_name)

                            parent = None
                            if 'parentItem' in item['data'].keys():
                                parent = item['data']['parentItem']

                            file = File(file_path, item['key'], parent)
                            self.files.append(file)

        return True


    def pull(self, to_add, to_delete, verbose = False):
        """

        Pull from Zotero the files to add and
        the files to remove from the local copy

        Args:
            to_add: list of files to add
            to_delete: list of files to delete
            verbose: enable print information

        Returns: True is success, False otherwise

        """

        if verbose:
            print("Zotero - Pull information")

        files_to_add = [i for i in self.files if i.path in to_add]
        for file in files_to_add:
            file_path = os.path.join(self.dir, file.path)

            try:
                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))

                with open(file_path, 'wb') as f:
                    f.write(self.zot.file(file.id))

                if verbose:
                    print(Fore.GREEN +
                          f"\t New: {file_path}" +
                          Style.RESET_ALL)

            except Exception as ex:
                print(Fore.RED + f"ERROR - {ex}" + Style.RESET_ALL)
                return False

        for file in to_delete:
            file_path = os.path.join(self.dir, file)

            try:
                os.remove(file_path)

                if verbose:
                    print(Fore.RED +
                          f"\t Deleted: {file_path}" +
                          Style.RESET_ALL)

            except Exception as ex:
                print(Fore.RED + f"ERROR - {ex}" + Style.RESET_ALL)
                return False

        return True



    def push(self, to_add, to_delete, verbose = False):
        """

        Push to Zotero the files to add
        and the files to delete

        TODO: Implement push files to Zotero

        Args:
            to_add: list of files to add
            to_delete: list of files to delete
            verbose: enable print information

        Returns: True is success, False otherwise

        """

        if verbose:
            print("Zotero - Push information")

        # TODO: Push new files to Zotero
        # for file in to_add:
        #     # Push file
        #     if verbose:
        #         print(Fore.GREEN +
        #               "\t New: " +
        #               file.path + Style.RESET_ALL)

        files_to_delete = [i for i in self.files if i.path in to_delete]
        for file in files_to_delete:
            if file.parent:
                id = file.parent
            else:
                id = file.id

            try:
                item = self.zot.item(id)
                self.zot.delete_item(item)

                if verbose:
                    print(Fore.RED +
                          "\t Deleted: {file.path}" +
                          Style.RESET_ALL)

            except Exception as ex:
                print(Fore.RED + f"ERROR - {ex}" + Style.RESET_ALL)
                return False

        return True
