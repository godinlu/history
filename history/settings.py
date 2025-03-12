"""
Description: module contain all settings of history

Last modified: 2025
Author: Luc Godin
"""

GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

CONFIG_NAME = "config.toml"

ORIGINAL_SCENES = "original-scenes"
TGZ_SCENES = "tgz-scenes"
FINAL_DEMS = "final-dems"

DEFAULT_CONFIG = {
    'name': 'my-project',
    'path': {
        'original_scenes': '',
        'final_dems': '',
        'tgz_scenes': ''
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

