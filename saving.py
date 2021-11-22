import yaml

from scrapper.saver import ArtistSaver


def main():
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    saver = ArtistSaver(config)
    saver.start()


if __name__ == "__main__":
    main()
