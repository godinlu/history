import os 
import glob
import subprocess
from hipp.tools import points_picker
from hipp.image import read_image_block_grayscale
import pandas as pd
from collections import defaultdict


def join_images(images_directory: str, output_directory: str, overwrite: bool = False, threads: int = 0) -> None:
    """
    Joins multiple subscene `.tif` image tiles (e.g., *_a.tif, *_b.tif, ..., *_k.tif) into a single mosaic.

    Args:
        images_directory (str): Path to the directory containing subscene `.tif` image tiles.
        output_directory (str): Directory where the output mosaicked images will be stored.
        overwrite (bool): Whether to overwrite existing mosaics.
        threads (int): Number of threads to use in `image_mosaic`.
    """
    os.makedirs(output_directory, exist_ok=True)

    # Group files by scene base name (everything before the last underscore + letter)
    scene_tiles = defaultdict(list)
    for filepath in glob.glob(os.path.join(images_directory, "*.tif")):
        filename = os.path.basename(filepath)
        if "_" not in filename:
            continue
        scene_prefix = "_".join(filename.split("_")[:-1])
        scene_tiles[scene_prefix].append(filepath)

    for scene, files in scene_tiles.items():
        output_file = os.path.join(output_directory, f"{scene}.tif")
        if os.path.exists(output_file) and not overwrite:
            print(f"Skipping {scene}: output already exists.")
            continue

        print(f"Mosaicking {scene} with {len(files)} tiles...")

        cmd = [
            "image_mosaic",
            *sorted(files),  # sorted for reproducibility
            "--ot", "byte",
            "--overlap-width", "3000",
            "--threads", str(threads),
            "-o", output_file
        ]

        print(" ".join(cmd))
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error while processing {scene}: {e}")

        # Clean up aux/log files (optional, safe to comment)
        for f in glob.glob("joined_images/*.aux.xml") + glob.glob("joined_images/*-log-image_mosaic-*.txt"):
            os.remove(f)


def clicking_on_corner(images_directory: str, csv_file: str) -> None:
    """
    Allows the user to manually select the four corner points (top-left, top-right, bottom-right, bottom-left) 
    for each image tile in a directory. These points are picked interactively and stored in a CSV file.

    For each image, if corner points are missing or not already saved, the user is prompted to pick them manually.
    If the user skips a point, np.nan is stored in the CSV.

    Args:
        images_directory (str): Path to the folder containing `.tif` images.
        csv_file (str): Path to the CSV file where corner coordinates will be stored.

    Returns:
        None
    """

    # Coordinates are grid indices (row, column) in a 7x7 layout
    corners = {
        "top_left" : [0, 0],
        "top_right" : [0, 6],
        "bottom_right" : [6, 6],
        "bottom_left" : [6, 0]
    }

    # Charger les données existantes si le fichier existe
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        done_images = set(df["image_id"])
        records = df.to_dict("records")
    else:
        done_images = set()
        records = []

    for filename in sorted(os.listdir(images_directory)):
        if not filename.endswith(".tif") or filename.replace(".tif","") in done_images:
            continue

        image_path = os.path.join(images_directory, filename)
        coords = {"image_id": filename.replace(".tif","")}

        for key in corners:
            image_bloc, (offset_x, offset_y) = read_image_block_grayscale(image_path, *corners[key], grid_size=7)
            points = points_picker(image_bloc)
            if points:
                x, y = points[0]
                coords[f"{key}_x"] = x + offset_x
                coords[f"{key}_y"] = y + offset_y
            else:
                # Enregistrer les données existantes avant d'interrompre
                df_out = pd.DataFrame(records)
                if not df_out.empty:
                    df_out.to_csv(csv_file, index=False)
                return  # Abandon propre si sélection annulée

        # Ajouter la nouvelle ligne
        records.append(coords)

        # Sauvegarde continue
        df_out = pd.DataFrame(records)
        df_out.to_csv(csv_file, index=False)


        
        

