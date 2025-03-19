"""
Description: module contain the config class

Last modified: 2025
Author: Luc Godin
"""
import tomlkit
import os
import copy
import click

CONFIG_NAME = "config.toml"

DEFAULT_CONFIG = {
    'name': 'my-project',
    'path': {
        'original_scenes': './original-scenes',
        'final_dems': './final-dems',
        'tgz_scenes': './tgz-scenes'
    },
    'usgsxplore': {
        'username': 'my-username',
        'token': 'my-token',
        'mc': {
            'dataset': 'declassii',
            'bbox': [-25.7520, 63.0960, -12.7441, 67.3070],
            'filter': 'camera=L & DOWNLOAD_AVAILABLE=Y',
            'date': '1980-08-22'
        },
        'pc': {
            'dataset': 'declassiii',
            'bbox': [-25.7520, 63.0960, -12.7441, 67.3070],
            'filter': 'camera_resol=2 to 4 Feet & DOWNLOAD_AVAILABLE=Y',
            'date': '1980-08-22'
        }
    }
}

class ConfigError(Exception):
    """ Exception raise by the `Config` class """

class Config:
    def __init__(self, project_dir: str = "."):
        self.config_file = os.path.join(project_dir, CONFIG_NAME) 

        if not os.path.exists(self.config_file):
            raise ConfigError(f"You must be in a history project")
        
        with open(self.config_file, "rb") as file:
            self.config = tomlkit.load(file)

        self.verify_config()

    def __getitem__(self, key):
        return self.config[key]
    
    def verify_config(self) -> None:
        """ Verify config an throw an ConfigError if somethings is wrong """

        if not all(key in self.config.keys() for key in DEFAULT_CONFIG.keys()):
            raise ConfigError(f"The config is not valid, please recreate a project")
        
        if self.config["usgsxplore"]["username"] == "my-username":
            raise ConfigError(f"You need to enter your USGS username into the config file at '{self.config_file}'")
        if self.config["usgsxplore"]["token"] == "my-token":
            raise ConfigError(f"You need to enter your USGS token into the config file at '{self.config_file}'")
        
    @staticmethod
    def create_project(name: str) -> None:
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

        #
        if "USGS_USERNAME" in os.environ and "USGS_TOKEN" in os.environ:
            confirm = click.confirm("USGS logs are found in your environment variables. Do you want to use them?", default=True)
            if confirm:
                copy_config["usgsxplore"]["username"] = os.getenv("USGS_USERNAME")
                copy_config["usgsxplore"]["token"] = os.getenv("USGS_TOKEN")

        os.mkdir(os.path.join(folder, copy_config["path"]["original_scenes"]))
        os.mkdir(os.path.join(folder, copy_config["path"]["final_dems"]))
        os.mkdir(os.path.join(folder, copy_config["path"]["tgz_scenes"]))

        # save it into the config_file path
        with open(config_file, "w", encoding="utf-8") as file:
            file.write(tomlkit.dumps(copy_config))



        