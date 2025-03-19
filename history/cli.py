"""
Description: module contain the command line interface of history

Last modified: 2025
Author: Luc Godin
"""

import os
import tarfile
import copy
import tomlkit
import click
from usgsxplore.api import API
from usgsxplore.filter import SceneFilter

from .config import Config, ConfigError
from .aspy.cli import aspy

GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


@click.group()
def history():
    """ CLI of history """

@click.command("create")
@click.argument("name")
def create_project(name: str):
    """ Create a history project """
    try:
        Config.create_project(name)
        project_location = os.path.abspath(f"./{name}")
        click.echo(f"\n {BOLD}{GREEN}Project '{name}' has been successfully created!{RESET}\n")
        click.echo(f" Project location: {BLUE}{project_location}{RESET}\n")
        
        click.echo(" To download the dataset, enter your USGS username and token:\n")
        click.echo(f"   {BOLD}cd {name}{RESET}")
        click.echo(f"   {BOLD}nano config.toml{RESET}\n")
        
        click.echo(" Once configured, start the download with:")
        click.echo(f"   {BOLD}history-download{RESET}\n")
        
    except FileExistsError as e:
        click.echo(f"\n {BOLD}{RED}Error:{RESET} {e}\n")


@click.command("download")
@click.argument("dataset", type=click.Choice(["pc", "mc"], case_sensitive=False))
def download_dataset(dataset: str) -> None:
    """Download the dataset"""
    # first thing first get and check the config
    try:
        config = Config()
    except ConfigError as e:
        click.echo(f"\n {BOLD}{RED}Error:{RESET} {e}\n")
        return
        
    click.echo(f"\n{BOLD}{GREEN} Config Check ! {RESET}\n\n Connection to the API...")
    # then check the connection to the api
    api = API(config["usgsxplore"]["username"], token = config["usgsxplore"]["token"])

    click.echo(f"{BOLD}{GREEN} Connection Successfull ! {RESET}\n\n Searching KH9 {dataset.upper()} scenes...")
    # create the scene filter
    scene_filter = SceneFilter.from_args(
        bbox=config["usgsxplore"][dataset]["bbox"],
        meta_filter=config["usgsxplore"][dataset]["filter"],
        date_interval=(config["usgsxplore"][dataset]["date"], config["usgsxplore"][dataset]["date"])
    )

    # then get from the api all entity ids of scenes wanted
    iterator = api.batch_search(config["usgsxplore"][dataset]["dataset"], scene_filter, metadata_type=None, use_tqdm=False)
    scenes_id = [scene["entityId"] for batch_scenes in iterator for scene in batch_scenes]

    click.echo(f"{BOLD}{GREEN} {len(scenes_id)} scenes founds ! {RESET}\n\n Downloading scenes...")

    api.download(
        config["usgsxplore"][dataset]["dataset"], 
        scenes_id, 
        config["path"]["tgz_scenes"],
        5, False, 2)
    
    click.echo(f"{BOLD}{GREEN} Downloading finish !\n{RESET}")
    api.logout()
    
    
@click.command("extract")
@click.option(
    "--keep-tgz",
    is_flag=True,
    help="Keep tgz scenes after extract",
)
def extract_scenes(keep_tgz: bool) -> None:
    """ Extract scenes into the original-scenes folder """
    try:
        config = Config()
    except ConfigError as e:
        click.echo(f"\n {BOLD}{RED}Error:{RESET} {e}\n")
        return

    nb_scenes = sum(1 for file_name in os.listdir(config["path"]["tgz_scenes"]) if file_name.endswith(".tgz"))
    click.echo(f"\n{BOLD} {nb_scenes} scenes found to extract !\n{RESET}")

    for file_name in os.listdir(config["path"]["tgz_scenes"]):
        if file_name.endswith(".tgz"):
            file_path = os.path.join(config["path"]["tgz_scenes"], file_name)
            click.echo(f"Extracting : {file_name}")

            # Extraction
            with tarfile.open(file_path, "r:gz") as tar:
                tar.extractall(path=config["path"]["original_scenes"])

    click.echo(f"\n{GREEN}{BOLD} Extraction complete !\n{RESET}")

    # remove all tgz_file if not keep_tgz
    if not keep_tgz:
        click.echo(f"Removing tgz-file...\n")
        for file_name in os.listdir(config["path"]["tgz_scenes"]):
            if file_name.endswith(".tgz"):
                file_path = os.path.join(config["path"]["tgz_scenes"], file_name)
                click.echo(f"Removing : {file_name}")
                os.remove(file_path)

        click.echo(f"\n{GREEN}{BOLD} Remove tgz-scenes complete !\n{RESET}")


history.add_command(create_project)
history.add_command(download_dataset)
history.add_command(extract_scenes)
history.add_command(aspy)

if __name__ == "__main__":
    create_project()