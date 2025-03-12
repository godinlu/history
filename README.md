# Description

The **history** package offers a command-line tool to download KH9 satellite scenes of islands.

# installation

```bash
# first clone the repository
git clone https://github.com/godinlu/history.git

# go to the repo
cd history

# create a conda environment and activate it
conda env create -f environment.yml
conda activate history

# install the package
pip install .
```

# Usage

Once installed, you can run the first command to create a project.
It will create some folder and file to download scenes.
```bash
history-create project_name
```
This command will generate the following structure:
```
📁 project_name/
├── 📁 final-dems/
├── 📁 original-scenes/
├── 📁 tgz-scenes/
├── config.toml
```

Before downloading, add your USGS login and token to the `config.toml` file:

```toml
[usgsxplore]
username = "my-username"
token = "my-token"
```

Now, you're ready to download KH9 scenes from the USGS API.
Navigate to your project folder and run:
```bash
history-download pc # contain 40 scenes (~200 Go)
# or
history-download mc # contain 6 scenes of (~13 Go)
```
This command will download all scenes in `.tgz` and put them into `tgz-scenes` directory. Once the download is complete, extract the scenes using:

```bash
history-extract
```
This command moves the extracted scenes from `tgz-scenes/` to `original-scenes/`.