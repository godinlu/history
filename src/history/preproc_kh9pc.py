import os 
import glob
import subprocess
from hipp.tools import points_picker
from hipp.image import read_image_block_grayscale
import pandas as pd
from collections import defaultdict
import pyvips
import math


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


def crop_images(images_directory: str, csv_file: str, output_directory: str, overwrite: bool = False) -> None:
    """
    Crop and rotate .tif images based on coordinates provided in a CSV file.

    For each image in the input directory, this function looks up its corresponding
    cropping points in the CSV file, rotates the image to align the top edge,
    crops it accordingly, and saves the result in the output directory.

    Args:
        images_directory (str): Path to the directory containing input .tif images.
        csv_file (str): Path to the CSV file containing image IDs and cropping coordinates.
                        The CSV must have an 'image_id' index and columns for each corner point:
                        top_left_x, top_left_y, top_right_x, top_right_y, etc.
        output_directory (str): Directory to save the cropped and rotated images.
        overwrite (bool, optional): If False, skip images whose output already exists. Defaults to False.
    """
    # Load the CSV into a DataFrame indexed by image_id
    df = pd.read_csv(csv_file, index_col="image_id")

    os.makedirs(output_directory, exist_ok=True)

    for filename in os.listdir(images_directory):
        if filename.endswith(".tif"):
            image_id = filename.replace(".tif", "")
            input_path = os.path.join(images_directory, filename)
            output_path = os.path.join(output_directory, filename)

            # Skip if output already exists and overwrite is disabled
            if os.path.exists(output_path) and not overwrite:
                print(f"[{image_id}] Skipped: output already exists at '{output_path}'")
                continue

            # Skip if image_id is not in the CSV
            if image_id not in df.index:
                print(f"[{image_id}] No cropping points found in CSV. Please update '{csv_file}'")
                continue

            # Retrieve the four corner points from the CSV and convert to int
            row = df.loc[image_id]
            points = [
                (int(row["top_left_x"]), int(row["top_left_y"])),
                (int(row["top_right_x"]), int(row["top_right_y"])),
                (int(row["bottom_right_x"]), int(row["bottom_right_y"])),
                (int(row["bottom_left_x"]), int(row["bottom_left_y"]))
            ]

            # Print cropping info and perform cropping + rotation
            print(f"[{image_id}] Found cropping points: {points}")
            print(f"[{image_id}] Cropping and rotating '{input_path}' -> '{output_path}'")
            rotate_and_crop_from_interest_points(input_path, output_path, points)
            print(f"[{image_id}] Done.\n")


def rotate_and_crop_from_interest_points(input_path: str, output_path: str, points: list[tuple[float, float]]) -> None:
    angle = angle_from_points(*points[0], *points[1])
    print(f"Rotation angle (degrees): {-angle:.4f}")

    # Load image with sequential access (streaming)
    image = pyvips.Image.new_from_file(input_path, access='sequential')

    # Rotate image by negative angle to align ROI horizontally
    rotated = image.rotate(-angle * math.pi / 180)

    # To rotate points properly, take center of rotation as image center
    cx, cy = image.width / 2, image.height / 2
    rotated_points = [rotate_point(x, y, -angle, cx, cy) for (x,y) in points]

    # Get bounding rectangle of rotated points
    left, top, width, height = bounding_rect(rotated_points)
    print(f"Cropping rectangle on rotated image: left={left}, top={top}, width={width}, height={height}")

    # Crop the rotated image
    cropped = rotated.crop(left, top, width, height)

    # Save the result
    cropped.write_to_file(output_path)
    print(f"Saved cropped rotated image to {output_path}")


def angle_from_points(x1, y1, x2, y2):
    """Calculate angle in degrees between two points relative to horizontal axis"""
    dx = x2 - x1
    dy = y2 - y1
    angle_rad = math.atan2(dy, dx)
    return math.degrees(angle_rad)

def bounding_rect(points):
    """Get bounding rectangle (left, top, width, height) from list of (x,y) points"""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    left = int(min(xs))
    top = int(min(ys))
    width = int(max(xs)) - left
    height = int(max(ys)) - top
    return left, top, width, height

def rotate_point(x, y, angle_deg, cx=0, cy=0):
    """Rotate a point (x,y) around center (cx,cy) by angle_deg degrees"""
    angle_rad = math.radians(angle_deg)
    x_shifted = x - cx
    y_shifted = y - cy
    xr = x_shifted * math.cos(angle_rad) - y_shifted * math.sin(angle_rad)
    yr = x_shifted * math.sin(angle_rad) + y_shifted * math.cos(angle_rad)
    return xr + cx, yr + cy



        

