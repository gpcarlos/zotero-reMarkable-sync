import os
import sys
import argparse
import shutil
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

    parser.add_argument('--initialize', '-ini', default=False, action='store_true', required=False)

    parser.add_argument('--quiet', '-q', default=False, action='store_true', required=False)

    return parser.parse_args()


def initialize(zot, rm, dir):
    """
    Initialize the local directory

    Args:
        zot: Zotero instance
        rm: ReMarkable instance
        dir: local directory
    """

    if not os.path.exists(dir):
        os.makedirs(dir)
    else:
        shutil.rmtree(dir)

    if not zot.fetch():
        return False

    if not rm.fetch():
        return False

    zot_paths = [i.path for i in zot.files]
    rm_paths = [i.path for i in rm.files]

    print(Fore.GREEN +
          "Initializing local directory..." +
          Style.RESET_ALL)

    if not zot.pull(zot_paths, []):
        return False

    for file in zot_paths:
        print(Fore.GREEN +
              f"\t Downloaded to local dir: {file}" +
              Style.RESET_ALL)

    if len(rm_paths) == 0:
        print(Fore.GREEN +
              "Initializing reMarkable..." +
              Style.RESET_ALL)

        if not rm.push(zot_paths, []):
            return False

        for file in zot_paths:
            print(Fore.GREEN +
                  f"\t New to reMarkable: {file}" +
                  Style.RESET_ALL)

    else:
        print(f"Found {len(rm_paths)} files in reMarkable {rm.dir_rm} directory.\n" +
              Fore.RED + "IMPORTANT" + Style.RESET_ALL +
              ": The script will assume that reMarkable and Zotero have " +
              "been previously synced.")

    return True


def sync(zot, rm, dir, quiet = False):
    """
    Synchronize Zotero library and reMarkable

    Args:
        zot: Zotero instance
        rm: ReMarkable instance
        dir: local directory
        quiet: quiet mode, no prints
    """

    if not zot.fetch():
        return False

    if not rm.fetch():
        return False

    local_paths = [i[len(dir):] for i in list_local_files(dir)]
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


    if not quiet:
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

    zot = Zotero(dir = local_dir,
                 zot_library_id = args.zot_library_id,
                 zot_api_key = args.zot_api_key)

    rm = ReMarkable(local_dir = local_dir,
                    reMarkable_dir = args.directory)

    if args.initialize:
        if not initialize(zot, rm, local_dir):
            sys.exit("Initialization Error.")

    else:
        if not os.path.exists(local_dir):
            print('Please initialize with --initialize')

        if not sync(zot, rm, local_dir, args.quiet):
            sys.exit("Synchronization Error.")


if __name__ == "__main__":
    main()
