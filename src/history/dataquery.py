import os
import shutil
import geopandas as gpd



def get_metadata_directory() -> None:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data","metadata"))



def get_casa_grande_kh9pc_ids() -> list[str]:
    geojson_file = os.path.join(get_metadata_directory(), "casa_grande_kh9pc", "images_footprint.geojson")
    gdf = gpd.read_file(geojson_file)
    return gdf["Entity ID"].to_list()

def get_casa_grande_aerial() -> gpd.GeoDataFrame:
    geojson_file = os.path.join(get_metadata_directory(), "casa_grande_aerial", "images_footprint.geojson")
    return gpd.read_file(geojson_file)

def get_casa_grande_kh9mc() -> gpd.GeoDataFrame:
    geojson_file = os.path.join(get_metadata_directory(), "casa_grande_kh9mc", "images_footprint.geojson")
    return gpd.read_file(geojson_file)


def download_casa_grande_kh9pc_metadata(output_directory: str) -> None:
    metadata_dir = os.path.join(get_metadata_directory(), "casa_grande_kh9pc")
    shutil.copytree(metadata_dir, output_directory, dirs_exist_ok=True)

def download_casa_grande_kh9mc_metadata(output_directory: str) -> None:
    metadata_dir = os.path.join(get_metadata_directory(), "casa_grande_kh9mc")
    shutil.copytree(metadata_dir, output_directory, dirs_exist_ok=True)


def download_iceland_aerial_metadata(output_directory: str) -> None:
    metadata_dir = os.path.join(get_metadata_directory(), "iceland_aerial")
    shutil.copytree(metadata_dir, output_directory, dirs_exist_ok=True)







    
