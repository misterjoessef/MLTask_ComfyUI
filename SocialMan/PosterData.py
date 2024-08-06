from ..Common.Utils import read_json_from_file, image_files_only, images_tensor_to_file
import folder_paths
import os
from ..constants import SOCIAL_MAN_KEYS_FILE


def get_account_id(network, account_name, social_data, account_key, account_id_key):
    for account in social_data.get(network, []):
        if account.get(account_key) == account_name:
            return account.get(account_id_key)
    return None


class SocialManMediaToPoster:
    def __init__(self):
        self.type = "output"
        self.output_dir = folder_paths.get_output_directory()
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [
            f
            for f in os.listdir(input_dir)
            if os.path.isfile(os.path.join(input_dir, f))
        ]
        return {
            "optional": {
                "media_file": (sorted(files),),
                "images": ("IMAGE",),
                "video_combine_filenames": ("VHS_FILENAMES",),
            },
        }

    FUNCTION = "pass_data"
    CATEGORY = "MLTask/SocialMan"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("image_path",)

    def pass_data(
        self,
        media_file=None,
        images=None,
        video_combine_filenames=None,
    ):

        if video_combine_filenames is not None and images is not None:
            raise Exception(
                "Only images or video_combine_filenames should be connected but not both"
            )

        if video_combine_filenames is None and images is None:
            return ([f"{folder_paths.get_input_directory()}/{media_file}"],)

        if images is not None:
            return (
                images_tensor_to_file(
                    images, self.output_dir, self.compress_level, "jpeg"
                ),
            )
        # print("-=---")
        save_output, output_files = video_combine_filenames
        # print(output_files[-1])
        # print("-=---")
        return ([output_files[-1]],)


class SocialManPostData:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "title": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "post title",
                    },
                ),
                "description": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "post description",
                    },
                ),
            },
        }

    FUNCTION = "pass_data"
    CATEGORY = "MLTask/SocialMan"
    RETURN_TYPES = ("MLT_SM_POST_DATA",)
    RETURN_NAMES = ("social_man_data",)

    def pass_data(self, title, description):
        return ({"title": title, "description": description},)


class TiktokPosterData:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "caption": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "tiktok caption",
                    },
                ),
                "photo_title": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "Title (for photo posts only)",
                    },
                ),
                "video_cover_timestamp_percent_from_0_to_1": (
                    "FLOAT",
                    {
                        "default": 0,
                    },
                ),
                "privacy": (
                    [
                        "FOLLOWER_OF_CREATOR",
                        "MUTUAL_FOLLOW_FRIENDS",
                        "PUBLIC_TO_EVERYONE",
                        "SELF_ONLY",
                    ],
                    {
                        "default": "PUBLIC_TO_EVERYONE",
                    },
                ),
                "users_can_comment": ("BOOLEAN", {"default": True}),
                "users_can_duet": ("BOOLEAN", {"default": True}),
                "users_can_stitch": ("BOOLEAN", {"default": True}),
                "content_disclosure_enabled": ("BOOLEAN", {"default": False}),
                "content_disclosure_branded_content": ("BOOLEAN", {"default": False}),
                "content_disclosure_your_brand": ("BOOLEAN", {"default": False}),
            },
        }

    FUNCTION = "pass_data"
    CATEGORY = "MLTask/SocialMan"
    RETURN_TYPES = ("MLT_SM_TIKTOK_DATA",)
    RETURN_NAMES = ("tiktok_data",)

    def pass_data(
        self,
        caption,
        photo_title,
        video_cover_timestamp_percent_from_0_to_1,
        privacy,
        users_can_comment,
        users_can_duet,
        users_can_stitch,
        content_disclosure_enabled,
        content_disclosure_branded_content,
        content_disclosure_your_brand,
    ):
        if not 0 <= video_cover_timestamp_percent_from_0_to_1 <= 1:
            raise ValueError(
                "video_cover_timestamp_percent_from_0_to_1 must be between 0 and 1 inclusive"
            )
        return (
            {
                "caption": caption,
                "photo_title": photo_title,
                "video_cover_timestamp_percent_from_0_to_1": video_cover_timestamp_percent_from_0_to_1,
                "privacy": privacy,
                "users_can_comment": users_can_comment,
                "users_can_duet": users_can_duet,
                "users_can_stitch": users_can_stitch,
                "content_disclosure_enabled": content_disclosure_enabled,
                "content_disclosure_branded_content": content_disclosure_branded_content,
                "content_disclosure_your_brand": content_disclosure_your_brand,
            },
        )


class YoutubePosterData:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        social_man_data = read_json_from_file(SOCIAL_MAN_KEYS_FILE)
        channels = [
            channel.get("channel_name")
            for channel in social_man_data.get("youtube", [])
        ]
        image_files = image_files_only()

        return {
            "required": {
                "target_channel": (
                    channels,
                    {
                        "default": (
                            channels[0] if channels else "Refresh or set the token"
                        ),
                    },
                ),
            },
            "optional": {
                "title": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "youtube title",
                    },
                ),
                "description": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "youtube description",
                    },
                ),
                "tags": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "tag1, tag2",
                    },
                ),
                "privacy": (
                    ["public", "private", "protected"],
                    {
                        "default": "public",
                    },
                ),
                "category": (
                    [
                        "Film & Animation",
                        "Autos & Vehicles",
                        "Music",
                        "Pets & Animals",
                        "Sports",
                        "Travel & Events",
                        "Gaming",
                        "People & Blogs",
                        "Comedy",
                        "Entertainment",
                        "News & Politics",
                        "Howto & Style",
                        "Education",
                        "Science & Technology",
                        "Nonprofits & Activism",
                    ],
                    {
                        "default": "Entertainment",
                    },
                ),
                "yt_thumbnail": ("IMAGE",),
                # "yt_thumbnail": (sorted(image_files), {"image_show": True}),
            },
        }

    FUNCTION = "pass_data"
    CATEGORY = "MLTask/SocialMan"
    RETURN_TYPES = ("MLT_SM_YOUTUBE_DATA",)
    RETURN_NAMES = ("youtube_data",)

    def pass_data(
        self,
        target_channel,
        title,
        description,
        tags,
        privacy,
        category,
        yt_thumbnail=None,
    ):
        social_man_data = read_json_from_file(SOCIAL_MAN_KEYS_FILE)
        target_channel_id = get_account_id(
            "youtube", target_channel, social_man_data, "channel_name", "channel_id"
        )
        ret = {
            "target_channel": target_channel_id,
            "title": title,
            "description": description,
            "tags": tags,
            "privacy": privacy,
            "category": category,
        }
        if yt_thumbnail is not None:
            ret["thumbnail"] = images_tensor_to_file(
                yt_thumbnail, folder_paths.get_output_directory(), 4
            )[0]
        return (ret,)


class FacebookPosterData:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        social_man_data = read_json_from_file(SOCIAL_MAN_KEYS_FILE)
        accounts = [
            channel.get("account_name")
            for channel in social_man_data.get("facebook", [])
        ]

        image_files = image_files_only()
        return {
            "required": {
                "target_account": (
                    accounts,
                    {
                        "default": (
                            accounts[0] if accounts else "Refresh or set the token"
                        ),
                    },
                ),
            },
            "optional": {
                "caption": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "facebook caption",
                    },
                ),
                "post_to_story": ("BOOLEAN", {"default": True}),
                "fb_thumbnail": ("IMAGE",),
                # "fb_thumbnail": (sorted(image_files), {"image_show": True}),
            },
        }

    FUNCTION = "pass_data"
    CATEGORY = "MLTask/SocialMan"
    RETURN_TYPES = ("MLT_SM_FACEBOOK_DATA",)
    RETURN_NAMES = ("facebook_data",)

    def pass_data(self, target_account, caption, post_to_story, fb_thumbnail=None):
        social_man_data = read_json_from_file(SOCIAL_MAN_KEYS_FILE)
        target_account_id = get_account_id(
            "facebook", target_account, social_man_data, "account_name", "account_id"
        )
        ret = {
            "target_account": target_account_id,
            "caption": caption,
            "post_to_story": post_to_story,
        }
        if fb_thumbnail is not None:
            ret["thumbnail"] = images_tensor_to_file(
                fb_thumbnail, folder_paths.get_output_directory(), 4
            )[0]

        return (ret,)


class InstagramPosterData:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        social_man_data = read_json_from_file(SOCIAL_MAN_KEYS_FILE)
        accounts = [
            channel.get("account_name")
            for channel in social_man_data.get("instagram", [])
        ]
        image_files = image_files_only()
        return {
            "required": {
                "target_account": (
                    accounts,
                    {
                        "default": (
                            accounts[0] if accounts else "Refresh or set the token"
                        ),
                    },
                ),
            },
            "optional": {
                "caption": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "instagram caption",
                    },
                ),
                "post_to_story": ("BOOLEAN", {"default": True}),
                "insta_thumbnail": ("IMAGE",),
                # "insta_thumbnail": (sorted(image_files), {"image_show": True}),
            },
        }

    FUNCTION = "pass_data"
    CATEGORY = "MLTask/SocialMan"
    RETURN_TYPES = ("MLT_SM_INSTAGRAM_DATA",)
    RETURN_NAMES = ("instagram_data",)

    def pass_data(self, target_account, caption, post_to_story, insta_thumbnail=None):
        social_man_data = read_json_from_file(SOCIAL_MAN_KEYS_FILE)
        target_account_id = get_account_id(
            "instagram", target_account, social_man_data, "account_name", "account_id"
        )
        ret = {
            "target_account": target_account_id,
            "caption": caption,
            "post_to_story": post_to_story,
        }

        if insta_thumbnail is not None:
            ret["thumbnail"] = images_tensor_to_file(
                insta_thumbnail, folder_paths.get_output_directory(), 4
            )[0]

        return (ret,)


class TwitterPosterData:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "caption": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "twitter caption",
                    },
                ),
            },
        }

    FUNCTION = "pass_data"
    CATEGORY = "MLTask/SocialMan"
    RETURN_TYPES = ("MLT_SM_TWITTER_DATA",)
    RETURN_NAMES = ("twitter_data",)

    def pass_data(self, caption):
        return ({"caption": caption},)


class LinkedinPosterData:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "caption": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "linkedin caption",
                    },
                ),
            },
        }

    FUNCTION = "pass_data"
    CATEGORY = "MLTask/SocialMan"
    RETURN_TYPES = ("MLT_SM_LINKEDIN_DATA",)
    RETURN_NAMES = ("linkedin_data",)

    def pass_data(self, caption):
        return ({"caption": caption},)


class PinterestPosterData:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        social_man_data = read_json_from_file(SOCIAL_MAN_KEYS_FILE)

        boards = [
            channel.get("board_name")
            for channel in social_man_data.get("pinterest", [])
        ]

        image_files = image_files_only()
        return {
            "required": {
                "target_board": (
                    boards,
                    {
                        "default": (
                            boards[0] if boards else "Refresh or set the token"
                        ),
                    },
                ),
            },
            "optional": {
                "title": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "Pinterest Title",
                    },
                ),
                "description": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "Pinterest Description",
                    },
                ),
                "link": (
                    "STRING",
                    {
                        "multiline": False,
                        "default": "",
                    },
                ),
                "pin_thumbnail": ("IMAGE",),
                # "pin_thumbnail": (sorted(image_files), {"image_show": True}),
            },
        }

    FUNCTION = "pass_data"
    CATEGORY = "MLTask/SocialMan"
    RETURN_TYPES = ("MLT_SM_PINTEREST_DATA",)
    RETURN_NAMES = ("pinterest_data",)

    def pass_data(self, target_board, title, description, link, pin_thumbnail=None):
        social_man_data = read_json_from_file(SOCIAL_MAN_KEYS_FILE)
        target_board_id = get_account_id(
            "pinterest", target_board, social_man_data, "board_name", "board_id"
        )
        ret = {
            "target_board": target_board_id,
            "title": title,
            "description": description,
            "link": link,
        }
        if pin_thumbnail is not None:
            ret["thumbnail"] = images_tensor_to_file(
                pin_thumbnail, folder_paths.get_output_directory(), 4
            )[0]
        return (ret,)
