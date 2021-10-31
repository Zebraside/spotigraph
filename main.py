import sqlite3
import click


@click.group()
def cli():
    pass

@cli.command()
def initdb():
    click.echo('Initialized the database')

@cli.command()
def dropdb():
    click.echo('Dropped the database')

# # Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     cli()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
