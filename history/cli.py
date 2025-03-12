"""
Description: module contain the command line interface of history

Last modified: 2025
Author: Luc Godin
"""
import click
import os
import tomlkit
import copy

from .downloader import download_dataset, extract_scenes, ConfigError
from .settings import *


def create_project_worker(name: str) -> None:
    """
    Create the project by copying the config and create some empty folder
    to the current directory
    """
    folder = os.path.join(os.path.abspath("."), name)

    # first test if the project already exist, if it's already exist throw an Exception
    if os.path.exists(folder):
        raise FileExistsError(f"The project '{folder}' already exist")
    
    os.mkdir(folder)

    config_file = os.path.join(folder, CONFIG_NAME)
    copy_config = copy.deepcopy(DEFAULT_CONFIG)


    # update the config
    copy_config["name"] = name
    copy_config["path"]["original_scenes"] = os.path.join(folder, ORIGINAL_SCENES)
    copy_config["path"]["final_dems"] = os.path.join(folder, FINAL_DEMS)
    copy_config["path"]["tgz_scenes"] = os.path.join(folder, TGZ_SCENES)

    os.mkdir(copy_config["path"]["original_scenes"])
    os.mkdir(copy_config["path"]["final_dems"])
    os.mkdir(copy_config["path"]["tgz_scenes"])

    # save it into the config_file path
    with open(config_file, "w", encoding="utf-8") as file:
        file.write(tomlkit.dumps(copy_config))

    return folder

@click.command()
@click.argument("name")
def create_project(name: str):
    """ Create a project """
    try:
        project_folder = create_project_worker(name)
        click.echo(f"\n {BOLD}{GREEN}Project '{name}' has been successfully created!{RESET}\n")
        click.echo(f" Project location: {BLUE}{project_folder}{RESET}\n")
        
        click.echo(" To download the dataset, enter your USGS username and token:\n")
        click.echo(f"   {BOLD}cd {name}{RESET}")
        click.echo(f"   {BOLD}nano config.toml{RESET}\n")
        
        click.echo(" Once configured, start the download with:")
        click.echo(f"   {BOLD}history-download{RESET}\n")
        
    except FileExistsError as e:
        click.echo(f"\n {BOLD}{RED}Error:{RESET} {e}\n")


@click.command()
@click.argument("dataset", type=click.Choice(["pc", "mc"], case_sensitive=False))
def download(dataset: str) -> None:
    """Download the dataset"""
    try:
        download_dataset(dataset)
    except ConfigError as e:
        click.echo(f"\n {BOLD}{RED}Error:{RESET} {e}\n")
    
@click.command()
def extract() -> None:
    """ Extract scenes into the original-scenes folder """
    try:
        extract_scenes()
    except ConfigError as e:
        click.echo(f"\n {BOLD}{RED}Error:{RESET} {e}\n")


if __name__ == "__main__":
    create_project()