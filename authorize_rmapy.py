import sys
import argparse
from utils.remarkable import authorize

def get_args():
    """Command line argument parsing"""

    parser = argparse.ArgumentParser()

    parser.add_argument("--security-code", "-s",
                        type=str,
                        required=True,
                        help="reMarkable security code. Get one here: https://my.remarkable.com/connect/remarkable")

    return parser.parse_args()


def main():
    args = get_args()

    if authorize(args.security_code):
        print("Authorized!")
    else:
        sys.exit("ERROR - Failed to authorize")


if __name__ == "__main__":
    main()
