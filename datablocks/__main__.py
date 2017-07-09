import click
from .orchestration import *


@click.group()
def cli():
    pass


@click.command()
def init():
    click.echo('Initialized the database')
    configure(init=True)


cli.add_command(init)

# @click.command()
# # @click.option('--count', default=1, help='Number of greetings.')
# # @click.option('--name', prompt='Your name',
# #               help='The person to greet.')
# def init():
#     """Simple program that greets NAME for a total of COUNT times."""
#     for x in range(5):
#         click.echo('Hello %s!' % x)

if __name__ == '__main__':
    cli()