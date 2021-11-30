import yaml
import click

from scrapper.scrapper import SpotifyScrapper


@click.command()
@click.option('--initial_artist_id', default="3jOstUTkEu2JkjvRdBA5Gu", help='artist spotify id to start search')
def main(initial_artist_id):
    scrapper = SpotifyScrapper(initial_artist=initial_artist_id)
    scrapper.start()


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(e)
