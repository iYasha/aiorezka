import argparse
from aiorezka import __version__


def cli():
    parser = argparse.ArgumentParser(description='Aiorezka CLI')
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument('-u', '--url', type=str, required=True,
                        help='URL of the movie or TV series to download')
    parser.add_argument('-p', '--path', default='.', type=str,
                        help='Path to save downloaded files (default: current directory)')
    parser.add_argument('-s', '--season', type=int,
                        help='Season number for TV series (default: 1)')
    parser.add_argument('-a', '--audio-track', type=str,
                        help='Preferred audio track for TV series')
    args = parser.parse_args()
    print(args)


if __name__ == '__main__':
    cli()

