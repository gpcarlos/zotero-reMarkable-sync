import os
import sys
import argparse
from colorama import Fore, Style
from utils.common import list_local_files, compare
from utils.zotero import Zotero
from utils.remarkable import ReMarkable

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


def sync(zot, rm, local_dir, verbose = False):
    """
    Synchronize Zotero library and

    Args:
        zot: Zotero instance
        rm: ReMarkable instance
        dir: local directory
    """

    if not zot.fetch():
        return False

    if not rm.fetch():
        return False

    local_paths = [i[len(local_dir):] for i in list_local_files(local_dir)]
    zot_paths = [i.path for i in zot.files]
    rm_paths = [i.path for i in rm.files]

    # Compare Zotero and reMarkable to the local folder
    # to check if there are changes in any of the ends
    to_add_zot, to_delete_zot = compare(zot_paths, local_paths)
    to_add_rm, to_delete_rm = compare(rm_paths, local_paths)

    if ((len(to_add_zot) == 0) &
        (len(to_delete_zot) == 0) &
        (len(to_add_rm) == 0) &
        (len(to_delete_rm) == 0)):
        print('Up to date.')
        return True

    if ((len(to_add_zot) != 0) |
        (len(to_delete_zot) != 0)):

        if not zot.pull(to_add_zot, to_delete_zot):
            return False

        if not rm.push(to_add_zot, to_delete_zot):
            return False

    if ((len(to_add_rm) != 0) |
        (len(to_delete_rm) != 0)):

        if not rm.pull(to_add_rm, to_delete_rm):
            return False

        if not zot.push(to_add_rm, to_delete_rm):
            return False


    if verbose:
        for file in to_add_zot:
            print(Fore.GREEN +
                  f"\t New to reMarkable: {file}" +
                  Style.RESET_ALL)

        for file in to_add_rm:
            print(Fore.GREEN +
                  f"\t New to Zotero: {file}" +
                  Style.RESET_ALL)

        for file in to_delete_zot:
            print(Fore.RED +
                  f"\t Deleted in reMarkable: {file}" +
                  Style.RESET_ALL)

        for file in to_delete_rm:
            print(Fore.RED +
                  f"\t Deleted in Zotero: {file}" +
                  Style.RESET_ALL)

    print(Fore.GREEN +
          f"{len(to_add_zot) + len(to_add_rm)} new files." +
          Style.RESET_ALL)

    print(Fore.RED +
          f"{len(to_delete_zot) + len(to_delete_rm)} deleted files." +
          Style.RESET_ALL)

    return True



def main():
    args = get_args()

    local_dir = os.path.join(os.path.expanduser('~'),
                    '.zot_rm_sync', args.directory)

    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    zot = Zotero(dir = local_dir,
                 zot_library_id = args.zot_library_id,
                 zot_api_key = args.zot_api_key)

    rm = ReMarkable(local_dir = local_dir,
                    reMarkable_dir = args.directory)

    if not sync(zot, rm, local_dir, args.verbose):
        sys.exit("Synchronization Error.")

if __name__ == "__main__":
    main()
