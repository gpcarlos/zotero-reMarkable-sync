import os
import sys
import argparse
from colorama import Fore, Style
from rmapy.api import Client
from rmapy.exceptions import AuthError
from rmapy.folder import Folder
from rmapy.document import ZipDocument
from pyzotero import zotero, zotero_errors

def get_args():
    """Command line argument parsing"""

    parser = argparse.ArgumentParser()

    parser.add_argument('--zot-library-id', '-l',
                        type=str,
                        required=True,
                        help='Zotero personal library id.')

    parser.add_argument('--zot-api-key', '-k',
                        type=str,
                        required=True,
                        help='Zotero API Key.')

    parser.add_argument('--directory', '-d',
                        type=str,
                        required=True,
                        help='Folder in reMarkable root that will sync')

    parser.add_argument('--verbose', '-v', default=False, action='store_true', required=False)

    return parser.parse_args()

def zotero_instance(zot_library_id, zot_api_key):
    """

    Initizalize the zotero instance

    Args:
        zot_library_id: zotero personal library id
        zot_api_key: zotero API Key

    Returns: zotero instance

    """
    try:
        zot = zotero.Zotero(zot_library_id, 'user', zot_api_key)
        zot.top()
        return zot

    except zotero_errors.UserNotAuthorised as ex:
        print(Fore.RED +
              "ERROR - Zotero API error... " +
              "Please run ensure the details are correct\n" +
              f"Zotero Library ID: {zot_library_id}\n" +
              f"Zotero API Key: {zot_api_key}" +
              Style.RESET_ALL)
        sys.exit(1)

def rm_instance():
    """

    Initizalize the rmapy instance

    Returns: rmapy instance

    """

    try:
        rm = Client()

        rm.renew_token()

        if not rm.is_auth():
            print(Fore.RED +
                  "ERROR - reMarkable API not authorized... " +
                  "Please run authorize_rmapy.py" +
                  Style.RESET_ALL)
            sys.exit(1)

        return rm

    except AuthError as ex:
        print(Fore.RED +
              f"ERROR - {ex} " +
              "Please run authorize_rmapy.py" +
              Style.RESET_ALL)
        sys.exit(1)


def path_to(zot, collectionId):
    """

    Recursively gets the full path to the collection

    Args:
        zot: zotero instance
        collectionId: zotero collection ID

    Returns: string path to the collection

    """

    if collectionId:
        c = zot.collection(collectionId)
        return f"{path_to(zot, c['data']['parentCollection'])}{c['data']['name']}/"
    else:
        return ""


def download_files_from_zotero(zot, directory, verbose = False):
    """

    Download all the .pdf files from the Zotero library that
    have not been downloaded yet

    Args:
        zot: zotero instance
        directory: local directory where the data will be downloaded to

    """

    count = 0

    for c in zot.all_collections():
        if c['meta']['numItems'] > 0:
            c_name = c['data']['name']
            c_path = os.path.join(path_to(zot, c['data']['parentCollection']), c_name)

            for item in zot.collection_items(c['key']):
                if item['data']['itemType'] == 'attachment':
                    file_name = item['data']['title']
                    if '.pdf' in file_name:
                        file_dir = os.path.join(directory, c_path)

                        if not os.path.exists(os.path.join(file_dir, file_name)):
                            if not os.path.exists(file_dir):
                                os.makedirs(file_dir)

                            with open(os.path.join(file_dir, file_name), 'wb') as f:
                                f.write(zot.file(item['data']['key']))

                            print(Fore.GREEN +
                                  "NEW FILE TO DOWNLOAD: " +
                                  os.path.join(file_dir, file_name) +
                                  Style.RESET_ALL)

                            count = count + 1
                        elif verbose:
                            print("File exists locally: " +
                                  os.path.join(file_dir, file_name))

    if count:
        print(f'Downloaded {count} new files from Zotero')
    else:
        print(f'No new files to download from Zotero')


def upload_files_to_remarkable(rm, directory, verbose=False):
    """

    Uploads to reMarkable all files located in "directory" that
    have not been uploaded to the same folder name "directory"
    in the reMarkable root level.
    It keeps the same folder structure.

    Args:
        rm: rmapy instance
        directory: local directory where the data is located

    """


    collection = rm.get_meta_items()

    count = 0

    for path, dir, files in os.walk(directory):
        for file in files:
            parent = ""
            folder = ""

            # Create the directory in reMarkable
            # if it does not exist
            for p in path.split("/"):
                folder = [ i for i in rm.get_meta_items()
                    if ((i.VissibleName == p) & (i.Parent == parent)) ]
                if folder == []:
                    new_folder = Folder(VissibleName=p, Parent=parent)
                    rm.create_folder(new_folder)
                    folder = [ i for i in rm.get_meta_items()
                        if ((i.VissibleName == p) & (i.Parent == parent)) ]
                parent = folder[0].ID

            # Upload the file to reMarkable
            # if it does not exist
            if [ i for i in collection.children(folder[0])
                if ((i.Type == "DocumentType") &
                    (i.VissibleName == file[:-4])) ]  == []:
                rawDocument = ZipDocument(doc=os.path.join(path, file))

                if rm.upload(rawDocument, folder[0]):
                    print(Fore.GREEN +
                        "NEW FILE TO UPLOAD: " +
                        os.path.join(path, file) +
                        Style.RESET_ALL)

                    count = count + 1

            elif verbose:
                print("File exists in rM: " +
                      os.path.join(path, file))

    if count:
        print(f'Uploaded {count} new files to reMarkable')
    else:
        print(f'No new files to upload to reMarkable')


def main():

    args = get_args()

    zot = zotero_instance(zot_library_id = args.zot_library_id,
                              zot_api_key = args.zot_api_key)
    rm = rm_instance()


    download_files_from_zotero(zot = zot,
                               directory = args.directory,
                               verbose = args.verbose)

    upload_files_to_remarkable(rm = rm,
                               directory = args.directory,
                               verbose = args.verbose)


if __name__ == "__main__":
    main()



#
