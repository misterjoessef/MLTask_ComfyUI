import requests
from pathlib import Path
import os
import re
import json
from ..Common.Utils import (
    read_json_from_file,
    write_json_to_file,
    mask_string,
    upload_file_to_signed_s3,
    is_image,
    is_gif,
    is_video,
    get_video_duration,
)
from server import PromptServer
from aiohttp import web
import base64
import copy
from ..constants import MLTASK_COMFYUI_API_URL, SOCIAL_MAN_KEYS_FILE

routes = PromptServer.instance.routes


@routes.get("/socialman/token")
async def get_token(request):
    # the_data = await request.post()
    # the_data now holds a dictionary of the values sent
    # SocialManPoster.handle_my_message(the_data)
    # token = os.environ.get("SOCIAL_MAN_TOKEN", "N/A")
    social_man_data = read_json_from_file(SOCIAL_MAN_KEYS_FILE)
    token = social_man_data.get("token", "")
    return web.json_response({"token": mask_string(token)})


@routes.post("/socialman/token")
async def set_token(request):
    data = await request.post()
    token = data["token"]
    write_json_to_file(SOCIAL_MAN_KEYS_FILE, json.loads(token))
    return web.json_response(
        {
            "status": "success",
            "message": "Done",
        },
        status=200,
    )


current_password = ""


@routes.post("/socialman/password")
async def set_token(request):
    global current_password
    data = await request.post()
    password = data["password"]
    if is_valid_password(password) == False:
        return web.json_response(
            {
                "status": "error",
                "message": 'Please set a valid password or click on the "Get New Token" Button',
            },
            status=500,
        )
    current_password = password
    return web.json_response(
        {
            "status": "success",
            "message": "Done",
        },
        status=200,
    )


def is_valid_token(s):
    pattern = r"^[0-9a-f]{32}$"
    return bool(re.match(pattern, s))


def is_valid_password(s):
    pattern = r"^.{4,}$"
    return bool(re.match(pattern, s))


def handle_finalizing_post(postID, social_man_token):
    auth_token = base64.b64encode(
        f"{social_man_token}:{current_password}".encode("utf-8")
    )
    headers = {
        "Authorization": auth_token,
    }
    post_payload = {
        "postID": postID,
    }
    response = requests.post(
        MLTASK_COMFYUI_API_URL + "/complete-post",
        headers=headers,
        json=post_payload,
        timeout=30,
    )

    if response.status_code == 200:
        pass
    elif response.status_code == 500:
        text_json = json.loads(response.text)
        PromptServer.instance.send_sync(
            "comfyui.socialman.error",
            {
                "customError": (
                    text_json["customError"] if "customError" in text_json else ""
                )
            },
        )
        print(f"Error posting: {response.text}")
    else:
        PromptServer.instance.send_sync("comfyui.socialman.error.unknown", {})
        print(f"Error posting: {response.text}")


def handle_uploading_media_files(
    show_status_banner,
    file_path,
    main,
    response_json,
    youtube_data,
    facebook_data,
    instagram_data,
    pinterest_data,
):
    if show_status_banner == True:
        PromptServer.instance.send_sync(
            "comfyui.socialman.status.update", {"status": "Uploading main file"}
        )

    upload_file_to_signed_s3(file_path, main)

    for platform in [
        "youtube",
        "facebook",
        "instagram",
        "pinterest",
    ]:
        platform_data = locals()[f"{platform}_data"]
        if platform in response_json:
            upload_url = response_json[platform]
            if show_status_banner == True:
                PromptServer.instance.send_sync(
                    "comfyui.socialman.status.update",
                    {"status": f"Uploading {platform} thumbnail"},
                )
            upload_file_to_signed_s3(platform_data["thumbnail"], upload_url)


def handle_post_creation_response(
    response,
    show_status_banner,
    file_path,
    social_man_token,
    youtube_data,
    facebook_data,
    instagram_data,
    pinterest_data,
    prepare_only,
):
    if response.status_code == 200:
        response_json = response.json()
        postID = response_json["postID"]
        link = response_json["link"]
        main = response_json["main"]
        handle_uploading_media_files(
            show_status_banner,
            file_path,
            main,
            response_json,
            youtube_data,
            facebook_data,
            instagram_data,
            pinterest_data,
        )
        if show_status_banner == True:
            PromptServer.instance.send_sync(
                "comfyui.socialman.success",
                {"link": link},
            )
        if prepare_only == False:
            handle_finalizing_post(postID, social_man_token)
        return link
    elif response.status_code == 403:
        text_json = json.loads(response.text)
        PromptServer.instance.send_sync(
            "comfyui.socialman.error",
            {
                "customError": (
                    text_json["customError"] if "customError" in text_json else ""
                )
            },
        )
        print(f"Error posting: {response.text}")
    else:
        print(response.text)
        PromptServer.instance.send_sync("comfyui.socialman.error.unknown", {})
        print(f"Error posting: {response.text}")


def create_post(
    file_path,
    social_man_token,
    post_data,
    tiktok_data,
    youtube_data,
    facebook_data,
    instagram_data,
    twitter_data,
    linkedin_data,
    pinterest_data,
    show_status_banner,
    prepare_only,
):
    if is_gif(file_path):
        raise Exception("Gif files not supported at the moment")

    tiktok_data = copy.deepcopy(tiktok_data)
    youtube_data = copy.deepcopy(youtube_data)
    facebook_data = copy.deepcopy(facebook_data)
    instagram_data = copy.deepcopy(instagram_data)
    twitter_data = copy.deepcopy(twitter_data)
    linkedin_data = copy.deepcopy(linkedin_data)
    pinterest_data = copy.deepcopy(pinterest_data)

    if tiktok_data is not None:
        tiktok_data["video_cover_timestamp_ms"] = 0
        if is_video(file_path):
            video_duration = get_video_duration(file_path)
            tiktok_data["video_cover_timestamp_ms"] = (
                tiktok_data["video_cover_timestamp_percent_from_0_to_1"]
                * video_duration
                * 1000
            )

    if is_image(file_path):
        # youtube doesnt support community image posting through api at the moment
        youtube_data = {}
        if facebook_data and "thumbnail" in facebook_data:
            del facebook_data["thumbnail"]
        if instagram_data and "thumbnail" in instagram_data:
            del instagram_data["thumbnail"]
        if pinterest_data and "thumbnail" in pinterest_data:
            del pinterest_data["thumbnail"]

    auth_token = base64.b64encode(
        f"{social_man_token}:{current_password}".encode("utf-8")
    )
    # Prepare post data
    post_payload = {
        "mainFilename": file_path,
        "postData": post_data if post_data is not None else {},
    }

    # Handle platform-specific data and thumbnails
    for platform in [
        "tiktok",
        "youtube",
        "facebook",
        "instagram",
        "twitter",
        "linkedin",
        "pinterest",
    ]:
        platform_data = locals()[f"{platform}_data"]
        if platform_data:
            post_payload[f"{platform}Data"] = platform_data

    headers = {
        "Authorization": auth_token,
    }

    response = requests.post(
        MLTASK_COMFYUI_API_URL + "/create-post",
        headers=headers,
        json=post_payload,
        timeout=30,
    )

    return handle_post_creation_response(
        response,
        show_status_banner,
        file_path,
        social_man_token,
        youtube_data,
        facebook_data,
        instagram_data,
        pinterest_data,
        prepare_only,
    )


class SocialManPoster:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "token": (
                    "SM_TOKEN",
                    {"default": "put your token here and DO NOT SHARE IT WITH ANYONE"},
                ),
            },
            "optional": {
                "media_file_path": (
                    "STRING",
                    {"default": "use media to poster node", "forceInput": True},
                ),
                "post_data": ("MLT_SM_POST_DATA", {"forceInput": True}),
                "tiktok_data": ("MLT_SM_TIKTOK_DATA", {"forceInput": True}),
                "youtube_data": ("MLT_SM_YOUTUBE_DATA", {"forceInput": True}),
                "facebook_data": ("MLT_SM_FACEBOOK_DATA", {"forceInput": True}),
                "instagram_data": ("MLT_SM_INSTAGRAM_DATA", {"forceInput": True}),
                "twitter_data": ("MLT_SM_TWITTER_DATA", {"forceInput": True}),
                "linkedin_data": ("MLT_SM_LINKEDIN_DATA", {"forceInput": True}),
                "pinterest_data": ("MLT_SM_PINTEREST_DATA", {"forceInput": True}),
                "show_status_banner": ("BOOLEAN", {"default": False}),
                "prepare_only": ("BOOLEAN", {"default": False}),
                # "display_message": ("DISPLAY_MSG",),
            },
        }

    FUNCTION = "post_everwhere"
    OUTPUT_NODE = True

    CATEGORY = "MLTask/SocialMan"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("post_link",)

    def post_everwhere(
        self,
        token,
        media_file_path,
        post_data=None,
        tiktok_data=None,
        youtube_data=None,
        facebook_data=None,
        instagram_data=None,
        twitter_data=None,
        linkedin_data=None,
        pinterest_data=None,
        show_status_banner=False,
        prepare_only=False,
        # display_message=None,
    ):
        if len(current_password) == 0:
            PromptServer.instance.send_sync(
                "comfyui.socialman.error",
                {"customError": "no_password_set"},
            )
            return ()

        social_man_data = read_json_from_file(SOCIAL_MAN_KEYS_FILE)
        if "token" not in social_man_data:
            PromptServer.instance.send_sync(
                "comfyui.socialman.error",
                {"customError": "no_token"},
            )
            return ()
        social_man_token = social_man_data["token"]
        if is_valid_token(social_man_token) == False:
            PromptServer.instance.send_sync(
                "comfyui.socialman.error",
                {"customError": "invalid_token"},
            )
            return ()
        post_url = create_post(
            media_file_path[0],
            social_man_token,
            post_data,
            tiktok_data,
            youtube_data,
            facebook_data,
            instagram_data,
            twitter_data,
            linkedin_data,
            pinterest_data,
            show_status_banner,
            prepare_only,
        )

        return (post_url,)
