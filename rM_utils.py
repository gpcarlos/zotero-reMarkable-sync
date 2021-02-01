import os
import sys
from colorama import Fore, Style
from rmapy.api import Client
from rmapy.exceptions import AuthError, ApiError
from rmapy.folder import Folder
from rmapy.document import ZipDocument
from common import File

class ReMarkable():

    def __init__(self, local_dir, reMarkable_dir):
        """

        Initizalize the rmapy instance

        Args:
            dir: local and reMarkable directory

        """

        self.files = []
        self.dir_l = local_dir
        self.dir_rm = reMarkable_dir

        try:
            self.rm = Client()

            self.rm.renew_token()

            if not self.rm.is_auth():
                print(Fore.RED + 'ERROR - reMarkable ' +
                      'API not authorized... Please ' +
                      'run authorize_rmapy.py' +
                      Style.RESET_ALL)
                sys.exit(1)

        except AuthError as ex:
            print(Fore.RED + f'ERROR - {ex} ' +
                  'Please run authorize_rmapy.py' +
                  Style.RESET_ALL)
            sys.exit(1)


    def recursive_fetch(self, item, path = ''):
        """

        Recursively fetch all the .pdf file
        stored in a collection.

        Args:
            item: rmapy meta item
            path: path to the item

        """

        for i in self.rm.get_meta_items().children(item):
            if i.Type == "CollectionType":
                parent = os.path.join(path, i.VissibleName)
                self.recursive_fetch(i, parent)

            elif i.Type == "DocumentType":
                file_path = os.path.join(path,
                            f'{i.VissibleName}.pdf')
                self.files.append(File(file_path, i.ID))


    def fetch(self):
        """

        Fetch all the .pdf file stored in directory self.dir_rm.

        """

        self.files = []

        # Find the <dir_rm> folder
        folder = [ i for i in self.rm.get_meta_items()
                   if i.VissibleName == self.dir_rm ]

        if len(folder) == 1:
            self.recursive_fetch(folder[0])


        elif len(folder) == 0:
            print(Fore.RED +
                  f'ERROR - Did not find a {dir} directory ' +
                  'in reMarkable' + Style.RESET_ALL)

        else:
            print(Fore.RED +
                  f'ERROR - Found more than one {dir} ' +
                  'directory in reMarkable. Only one ' +
                  'directory with that name is allowed' +
                  Style.RESET_ALL)
            sys.exit(1)


    def pull(self, to_add, to_delete):
        """

        Pull from reMarkable the files to
        remove from the local copy

        TODO: Implement pull files to add
        and files with new annotations

        Export pdf with annotations is not
        supported by rmapy yet :( Feb 2021

        Args:
            to_add: list of files to add
            to_delete: list of files to delete

        """
        # print("reMarkable - Pull information")

        # files_to_add = [i for i in self.files if i.path in to_add]
        # for file in files_to_add:
        #     print(Fore.GREEN +
        #           "\t New: " +
        #           file.path + Style.RESET_ALL)

        for file in to_delete:
            file_path = os.path.join(self.dir_l, file)

            if os.path.exists(file_path):
                os.remove(file_path)
                # print(Fore.RED +
                #       f"\t Deleted: {file_path}" +
                #       Style.RESET_ALL)

    def push(self, to_add, to_delete):
        """

        Push to reMarkable the files to add
        and the files to delete

        Args:
            to_add: list of files to add
            to_delete: list of files to delete

        """
        # print("reMarkable - Push information")

        for file in to_add:
            file_path_l = os.path.join(self.dir_l, file)
            file_path_rm = os.path.join(self.dir_rm, file)
            parent = ""
            folder = ""

            # Create the directory in reMarkable
            # if it does not exist
            for p in os.path.dirname(file_path_rm).split("/"):
                folder = [ i for i in self.rm.get_meta_items()
                    if ((i.VissibleName == p) & (i.Parent == parent)) ]
                if len(folder) == 0:
                    new_folder = Folder(VissibleName=p, Parent=parent)
                    rm.create_folder(new_folder)
                    folder = [ i for i in self.rm.get_meta_items()
                        if ((i.VissibleName == p) & (i.Parent == parent)) ]
                parent = folder[0].ID

            # Upload the file to reMarkable
            # if it does not exist
            if [ i for i in self.rm.get_meta_items().children(folder[0])
                if ((i.Type == "DocumentType") &
                    (i.VissibleName == file[:-4])) ]  == []:

                if os.path.exists(file_path_l):
                    rawDocument = ZipDocument(doc=file_path_l)
                    self.rm.upload(rawDocument, folder[0])

                    # print(Fore.GREEN +
                    #       f"\t New: {file_path_rm}" +
                    #       Style.RESET_ALL)

        files_to_delete = [i for i in self.files if i.path in to_delete]
        for file in files_to_delete:
            file_path = os.path.join(self.dir_rm, file.path)
            doc = self.rm.get_doc(file.id)
            self.rm.delete(doc)

            # print(Fore.RED +
            #       f"\t Deleted: {file_path}" +
            #       Style.RESET_ALL)
