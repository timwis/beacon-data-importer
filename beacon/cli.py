import click
import petl as etl

from .prepare_contacts import prepare_contacts
from .prepare_calls import prepare_calls

@click.group()
def main():
  pass

main.add_command(prepare_contacts)
main.add_command(prepare_calls)

if __name__ == '__main__':
  main()
