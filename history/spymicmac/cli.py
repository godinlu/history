"""
Description: module contain the cli of the spymicmac preprocessing

Last modified: 2025
Author: Luc Godin
"""
import subprocess
import click

from history.settings import *

def install_package(package: str) -> None:
    """ Install the package `package` via conda """
    click.echo(f"Installation of {BLUE}{package}{RESET} : ", nl=False)
    subprocess.check_call(['conda', 'install','-c','conda-forge', package, '-y'], stdout=subprocess.DEVNULL)
    click.echo(f"{GREEN}{BOLD}SUCCES{RESET}")

@click.group()
def spymicmac() -> None:
    """ CLI of spymicmac preprocessing """

@click.command("create")
def create_spymicmac_project() -> None:
    """ Create the scaffold of the spymicmac preprocessing pipeline """

    # the first step is too install the spymicmac package via conda
    # and scikit-learn and rtree which are needed
    try:
        install_package("spymicmac")
        install_package("scikit-learn")
        install_package("rtree")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'installation de spymicmac: {e}")
        return
    

    
    
@click.command("clean")
def clean_spymicmac_project() -> None:
    """ Clean all scaffold and package of spymicmac """
    confirm = click.confirm("Are you sure to delete your spymicmac project", default=False)

    if confirm:
        try:
            subprocess.check_call(['conda', 'remove', 'rtree', 'scikit-learn', 'spymicmac', '-y'])
        except subprocess.CalledProcessError as e:
            print(f"Removing package error: {e}")
            return
    else:
        click.echo("Cleaning abort.")



spymicmac.add_command(create_spymicmac_project)
spymicmac.add_command(clean_spymicmac_project)


