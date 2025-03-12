"""
Description: module contain the project part

Last modified: 2025
Author: Luc Godin
"""
import tomlkit
import os
import click
import tarfile

from usgsxplore.api import API
from usgsxplore.filter import SceneFilter


from .settings import *

class ConfigError(Exception):
    """Exception raise from a problem of config"""

def download_dataset(kh9_type: str):
    # first thing first get and check the config
    config = get_config()

    click.echo(f"\n{BOLD}{GREEN} Config Check ! {RESET}\n\n Connection to the API...")
    # then check the connection to the api
    api = API(config["usgsxplore"]["username"], token = config["usgsxplore"]["token"])

    click.echo(f"{BOLD}{GREEN} Connection Successfull ! {RESET}\n\n Searching KH9 {kh9_type.upper()} scenes...")
    # create the scene filter
    scene_filter = SceneFilter.from_args(
        bbox=config["usgsxplore"][kh9_type]["bbox"],
        meta_filter=config["usgsxplore"][kh9_type]["filter"],
        date_interval=(config["usgsxplore"][kh9_type]["date"], config["usgsxplore"][kh9_type]["date"])
    )

    # then get from the api all entity ids of scenes wanted
    iterator = api.batch_search(config["usgsxplore"][kh9_type]["dataset"], scene_filter, metadata_type=None, use_tqdm=False)
    scenes_id = [scene["entityId"] for batch_scenes in iterator for scene in batch_scenes]

    click.echo(f"{BOLD}{GREEN} {len(scenes_id)} scenes founds ! {RESET}\n\n Downloading scenes...")

    api.download(
        config["usgsxplore"][kh9_type]["dataset"], 
        scenes_id, 
        config["path"]["tgz_scenes"],
        5, False, 2)
    
    click.echo(f"{BOLD}{GREEN} Downloading finish !\n{RESET}")
    api.logout()


def extract_scenes() -> None:
    """
    Extract all scenes from the tgz-scenes folder into the original-scenes
    """
    config = get_config()

    nb_scenes = sum(1 for file_name in os.listdir(config["path"]["tgz_scenes"]) if file_name.endswith(".tgz"))
    click.echo(f"\n{BOLD} {nb_scenes} scenes found to extract !\n{RESET}")

    for file_name in os.listdir(config["path"]["tgz_scenes"]):
        if file_name.endswith(".tgz"):
            file_path = os.path.join(config["path"]["tgz_scenes"], file_name)
            click.echo(f"Extracting : {file_name}")

            # Extraction
            with tarfile.open(file_path, "r:gz") as tar:
                tar.extractall(path=config["path"]["original_scenes"])

    click.echo(f"\n{GREEN}{BOLD} Extraction complete!\n{RESET}")


def get_config() -> tomlkit.TOMLDocument:
    """
    return the config if the config is valid else throw ConfigError
    """
    config_file = os.path.join(".", CONFIG_NAME)
    if not os.path.exists(config_file):
        raise ConfigError(f"You must be in a history project")

    with open(config_file, "rb") as file:
        config = tomlkit.load(file)

    if config["usgsxplore"]["username"] == "my-username":
        raise ConfigError(f"You need to enter your USGS username into the config file at '{config_file}'")
    if config["usgsxplore"]["token"] == "my-token":
        raise ConfigError(f"You need to enter your USGS token into the config file at '{config_file}'")
    return config


