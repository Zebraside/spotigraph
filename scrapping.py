import yaml
import click

from scrapper.scrapper import SpotifyScrapper


@click.command()
@click.option('--initial_artist_id', default="3jOstUTkEu2JkjvRdBA5Gu", help='artist spotify id to start search')
def main(initial_artist_id):
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    scrapper = SpotifyScrapper(config, initial_artist=initial_artist_id)
    scrapper.start()


if __name__ == "__main__":
    main()
