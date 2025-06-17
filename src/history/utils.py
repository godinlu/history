import geopandas as gpd
import pandas as pd
import numpy as np

def generate_camera_model_extrinsics(
        geojson_file: str, 
        csv_output_file: str, 
        id_colname:str = "Entity ID", 
        lon_colname:str = "Center Longitude dec",
        lat_colname:str = "Center Latitude dec") -> None:

    gdf = gpd.read_file(geojson_file)

    df_out = pd.DataFrame()
    df_out["image_file_name"] = gdf[id_colname] 
    df_out["lon"] = gdf[lon_colname]
    df_out["lat"] = gdf[lat_colname]
    df_out["alt"] = np.nan  

    df_out.to_csv(csv_output_file, index=False)
