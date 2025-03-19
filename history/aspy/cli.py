"""
Description: module contain the CLI for start the aspy preproc pipeline

Last modified: 2025
Author: Luc Godin
"""
import os
import click
import tomlkit
import subprocess

from history.config import Config, ConfigError

GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

#------------------------------------------------------------------------------------------------------
#                                       FUNCTION
#------------------------------------------------------------------------------------------------------


def fill_aspy_config(history_config: tomlkit.TOMLDocument) -> tomlkit.TOMLDocument:
    """
    Fill the aspy config file at .aspy/aspy-config.toml
    """
    aspy_config_path = os.path.join("aspy", "aspy-config.toml")
    with open(aspy_config_path, "rb") as file:
        aspy_config = tomlkit.load(file)
    
    project_folder = os.path.abspath(".")
    aspy_folder = os.path.join(project_folder, "aspy")

    aspy_config["IDfile"] = os.path.join(aspy_folder, "scenes_id.txt")
    aspy_config["outDir"] = os.path.join(aspy_folder, "output")
    aspy_config["dataDir"] = os.path.abspath(history_config["path"]["original_scenes"]) 
    aspy_config["browse_path"] = os.path.join(aspy_folder, "browse")
    aspy_config["metadata_file"] = os.path.join(aspy_folder, "metadata.gpkg")

    with open(aspy_config_path, "w", encoding="utf-8") as file:
        file.write(tomlkit.dumps(aspy_config))

    click.echo(f"update aspy config at '{os.path.abspath(aspy_config_path)}' : {BOLD}{GREEN}SUCCESS{RESET}'")

    return aspy_config


def dl_aspy_files(history_config: tomlkit.TOMLDocument, aspy_config: tomlkit.TOMLDocument) -> None:
    """
    download with usgsxplore:
    - scenes ids in a text file
    - the metadata of scenes in a gpkg
    - browse image in the browse path directory 
    """
    username = history_config["usgsxplore"]["username"]
    token = history_config["usgsxplore"]["token"]
    options = history_config["usgsxplore"]["mc"]

    
    # download scenes ids in a texte file
    click.echo(f"Downloading scenes ids at '{aspy_config['IDfile']}' : ", nl=False)
    search_cmd = ["usgsxplore", "search", options["dataset"],
                   "--username", username, "--token", token,
                   "--output", aspy_config["IDfile"],
                   "--bbox"] + list(map(str, options["bbox"])) + [
                    "--interval-date", options["date"], options["date"], "--filter", options["filter"]
    ]
    subprocess.check_call(search_cmd)
    click.echo(f"{BOLD}{GREEN}SUCCESS{RESET}")

    # download the gpkg
    click.echo(f"Downloading the metadata file at '{aspy_config['metadata_file']}' : ", nl=False)
    search_cmd = ["usgsxplore", "search", options["dataset"],
                   "--username", username, "--token", token,
                   "--output", aspy_config["metadata_file"],
                   "--bbox"] + list(map(str, options["bbox"])) + [
                    "--interval-date", options["date"], options["date"], "--filter", options["filter"]
    ]
    subprocess.check_call(search_cmd)
    click.echo(f"{BOLD}{GREEN}SUCCESS{RESET}")

    # download all browse image 
    click.echo(f"Downloading browse images at '{aspy_config['browse_path']}' : ")
    dl_browse_cmd = ["usgsxplore", "download-browse", aspy_config["metadata_file"], "--output-dir", aspy_config["browse_path"]]
    subprocess.check_call(dl_browse_cmd)
    click.echo(f"Downloading browse images at '{aspy_config['browse_path']}' : {BOLD}{GREEN}SUCCESS{RESET}\n")

#------------------------------------------------------------------------------------------------------
#                                       CLI PART
#------------------------------------------------------------------------------------------------------

@click.group()
def aspy():
    """ CLI for the aspy preproc pipeline """


@click.command("create")
def create_aspy_project() -> None:
    """ Create the scaffold for the KH9 MC preprocessing """
    # the first step is too open the config 
    try:
        config = Config()
    except ConfigError as e:
        click.echo(f"\n {BOLD}{RED}Error:{RESET} {e}\n")
        return

    # then create an folder name aspy to put all aspy stuff
    os.makedirs("aspy", exist_ok=True)
    os.makedirs(os.path.join("aspy", "output"), exist_ok=True)
    os.makedirs(os.path.join("aspy", "browse"), exist_ok=True)

    # download the aspy librairie
    # TODO

    # create the config file of aspy in the aspy directory
    cli_command = ["aspy-config", "create", "--config-name", "aspy-config"]
    subprocess.run(["conda", "run", "-n", "aspy"] + cli_command, check=True, cwd="aspy")

    # fill up the aspy config file
    aspy_config = fill_aspy_config(config)

    # create the ids_text_file, the metadata_file and download browse_path
    dl_aspy_files(config, aspy_config)

    click.echo(f"To start the aspy preprocessing run :\n {BLUE}cd aspy\nconda activate aspy\naspy-preproc aspy-config.toml{RESET}")


@click.command("run")
def run_aspy_preproc() -> None:
    """ Run the preprocessing of aspy """
    # the first step is too open the config just to verifiy
    try:
        Config()
    except ConfigError as e:
        click.echo(f"\n {BOLD}{RED}Error:{RESET} {e}\n")
        return
    
    aspy_config_file = os.path.join("aspy", "aspy-config.toml")
    if not os.path.exists(aspy_config_file):
        click.echo(f"\n {BOLD}{RED}Error:{RESET} aspy project not found, please run {BOLD}histo aspy create{RESET} first.\n")

    # run the aspy-preproc command 
    cli_command = ["aspy-preproc", "aspy-config.toml"]
    subprocess.run(["conda", "run", "-n", "aspy"] + cli_command, check=True, cwd="aspy", capture_output=False)
    


aspy.add_command(create_aspy_project)
aspy.add_command(run_aspy_preproc)