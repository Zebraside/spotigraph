from spotigraph.scrapper import ArtistSaver


def main():
    saver = ArtistSaver()
    saver.start()


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(e)
