import json
import folder_paths
import os
import requests
import base64
import traceback
import mimetypes
from PIL import Image, ImageSequence, ImageOps
import numpy as np
import imghdr
import mimetypes
import subprocess
import torch
import node_helpers
from matplotlib import font_manager

chunk_size = 5 * 1024 * 1024  # 1MB chunks


def get_system_font_files():
    font_files = []
    for font in font_manager.fontManager.ttflist:
        font_file = os.path.basename(font.fname)
        font_files.append(font_file)
    return font_files


def is_image(file_path):
    # Check if it's a common image type
    if imghdr.what(file_path) is not None:
        return True
    # Additional check for SVG files
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type is not None and mime_type.startswith("image")


def is_video(file_path):
    video_extensions = [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"]
    _, extension = os.path.splitext(file_path.lower())
    mime_type, _ = mimetypes.guess_type(file_path)
    return extension in video_extensions or (
        mime_type is not None and mime_type.startswith("video")
    )


def is_gif(file_path):
    return imghdr.what(file_path) == "gif"


def get_video_duration(file_path):
    if not is_video(file_path):
        return None

    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                file_path,
            ],
            capture_output=True,
            text=True,
        )

        data = json.loads(result.stdout)
        duration = float(data["format"]["duration"])
        return duration
    except (subprocess.SubprocessError, KeyError, json.JSONDecodeError):
        return None


def images_file_to_tensor(image):
    image_path = folder_paths.get_annotated_filepath(image)
    img = node_helpers.pillow(Image.open, image_path)
    return images_data_to_tensor(img)


def images_data_to_tensor(img):

    output_images = []
    output_masks = []
    w, h = None, None

    excluded_formats = ["MPO"]

    for i in ImageSequence.Iterator(img):
        i = node_helpers.pillow(ImageOps.exif_transpose, i)

        if i.mode == "I":
            i = i.point(lambda i: i * (1 / 255))
        image = i.convert("RGB")

        if len(output_images) == 0:
            w = image.size[0]
            h = image.size[1]

        if image.size[0] != w or image.size[1] != h:
            continue

        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        if "A" in i.getbands():
            mask = np.array(i.getchannel("A")).astype(np.float32) / 255.0
            mask = 1.0 - torch.from_numpy(mask)
        else:
            mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")
        output_images.append(image)
        output_masks.append(mask.unsqueeze(0))

    if len(output_images) > 1 and img.format not in excluded_formats:
        output_image = torch.cat(output_images, dim=0)
        output_mask = torch.cat(output_masks, dim=0)
    else:
        output_image = output_images[0]
        output_mask = output_masks[0]

    return (output_image, output_mask)


def images_tensor_to_file(images, output_dir, compress_level, extension="png"):
    filename_prefix = "socialman"
    full_output_folder, filename, counter, subfolder, filename_prefix = (
        folder_paths.get_save_image_path(
            filename_prefix, output_dir, images[0].shape[1], images[0].shape[0]
        )
    )
    results = list()
    for batch_number, image in enumerate(images):
        i = 255.0 * image.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

        filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
        file = f"{filename_with_batch_num}_{counter:05}_.{extension}"
        img.save(
            os.path.join(full_output_folder, file),
            compress_level=compress_level,
        )
        results.append(f"{folder_paths.get_output_directory()}/{file}")
        counter += 1
    return results


def get_file_base64(file_path):
    with open(file_path, "rb") as file:
        content = file.read()
    file_content_base64 = base64.b64encode(content).decode("utf-8")
    return file_content_base64


def upload_file_to_signed_s3(file_path, presigned_url):
    # Check if file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = "application/octet-stream"
    # Get file size
    file_size = os.path.getsize(file_path)

    # Open file in binary mode
    with open(file_path, "rb") as file:
        # Use requests to PUT the file to the pre-signed URL
        response = requests.put(
            presigned_url,
            data=file,
            headers={"Content-Length": str(file_size), "Content-Type": content_type},
        )

    # Check if the upload was successful
    if response.status_code == 200:
        print(f"File {file_path} uploaded successfully.")
    else:
        print(f"Failed to upload file. Status code: {response.status_code}")
        print(f"Response: {response.text}")


def upload_file(file_path, api_base_url, auth_token):
    try:
        # Initiate upload
        headers = {"Authorization": auth_token}
        total_chunks = calculate_total_chunks(file_path)

        print(f"Initiating upload for file: {file_path}")
        init_response = requests.post(
            f"{api_base_url}/initiate-upload",
            headers=headers,
            json={
                "fileName": os.path.basename(file_path),
                "totalChunks": total_chunks,
            },
        )
        init_response.raise_for_status()
        print(f"Initiation response: {init_response.text}")

        upload_id = init_response.json()["uploadId"]
        print(f"Upload ID: {upload_id}")

        # Read file in chunks and upload

        chunk_number = 1

        with open(file_path, "rb") as f:
            while chunk_number <= total_chunks:
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                upload_url = f"{api_base_url}/upload-chunk/{upload_id}/{chunk_number}"
                print(f"upload_url: {upload_url}")
                print(f"Upload ID: {upload_id}")
                print(f"Uploading chunk {chunk_number}/{total_chunks}")
                response = requests.put(
                    upload_url, headers=headers, files={"file": chunk}
                )
                # response.raise_for_status()
                print(f"Chunk {chunk_number} upload response: {response.text}")

                chunk_number += 1

        # Complete upload
        complete_url = f"{api_base_url}/complete-upload/{upload_id}"
        print("Completing upload")
        complete_response = requests.post(complete_url, headers=headers)
        complete_response.raise_for_status()
        print(f"Complete upload response: {complete_response.text}")

        return upload_id

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        print(
            f"Response content: {e.response.content if e.response else 'No response'}"
        )
        print(f"Traceback: {traceback.format_exc()}")
        raise

    except Exception as e:
        print(f"Unexpected error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise


def calculate_total_chunks(file_path):
    file_size = os.path.getsize(file_path)
    return -(-file_size // chunk_size)  # Ceiling division


def image_files_only():
    image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp")
    input_dir = folder_paths.get_input_directory()
    return [
        f
        for f in os.listdir(input_dir)
        if os.path.isfile(os.path.join(input_dir, f))
        and f.lower().endswith(image_extensions)
    ]


def mask_string(input_string):
    # Ensure the input is a string
    input_string = str(input_string)

    # If the string is 5 characters or longer
    if len(input_string) >= 5:
        return "***" + input_string[-5:]
    # If the string is shorter than 5 characters
    else:
        return "***" + input_string


def write_json_to_file(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def read_json_from_file(filename):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"error": "File not found."}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in file."}


def update_json_file(filename, new_data):
    old_data = read_json_from_file(filename)
    old_data.update(new_data)
    with open(filename, "w") as file:
        json.dump(old_data, file, indent=4)
