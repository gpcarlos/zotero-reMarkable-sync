import sys
import argparse
from colorama import Fore, Style
from rmapy.api import Client
from rmapy.exceptions import AuthError


def get_args():
    """Command line argument parsing"""
    parser = argparse.ArgumentParser()

    parser.add_argument("--security-code", "-s",
                        type=str,
                        required=True,
                        help="reMarkable security code. Get one here: https://my.remarkable.com/connect/remarkable")

    return parser.parse_args()


def authorize(security_code):
    """

    Authorize rmapy to comunicate to our reMarkable device

    Args:
        x: security code

    Returns: True is authorized, False otherwise

    """
    rma = Client()

    try:
        rma.register_device(security_code)

        rma.renew_token()
    except AuthError as ex:
        print(Fore.RED +
              f"ERROR - {ex}" +
              Style.RESET_ALL)
        sys.exit(1)

    return rma.is_auth()

def main():
    args = get_args()

    if authorize(args.security_code):
        print(Fore.GREEN +
              "Authorized!" +
              Style.RESET_ALL)
    else:
        print(Fore.RED +
              "ERROR - Failed to authorize" +
              Style.RESET_ALL)


if __name__ == "__main__":
    main()



#
