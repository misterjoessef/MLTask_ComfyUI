from .SocialMan.SocialManPoster import SocialManPoster
from .SocialMan.PosterData import (
    SocialManPostData,
    TiktokPosterData,
    YoutubePosterData,
    FacebookPosterData,
    InstagramPosterData,
    TwitterPosterData,
    LinkedinPosterData,
    PinterestPosterData,
    SocialManMediaToPoster,
)
from .UtilNodes.TextGenerator import MLTaskUtilsTextImageGenerator


NODE_CLASS_MAPPINGS = {
    "MLTaskUtilsTextImageGenerator": MLTaskUtilsTextImageGenerator,
    "SocialManMediaToPoster": SocialManMediaToPoster,
    "SocialManPostData": SocialManPostData,
    "SocialManPoster": SocialManPoster,
    "TiktokPosterData": TiktokPosterData,
    "YoutubePosterData": YoutubePosterData,
    "FacebookPosterData": FacebookPosterData,
    "InstagramPosterData": InstagramPosterData,
    "TwitterPosterData": TwitterPosterData,
    "LinkedinPosterData": LinkedinPosterData,
    "PinterestPosterData": PinterestPosterData,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "MLTaskUtilsTextImageGenerator": "MLTask Utils Text Image Generator",
    "SocialManMediaToPoster": "SocialMan Media To Poster",
    "SocialManPostData": "SocialMan Post Data",
    "SocialManPoster": "SocialMan Poster",
    "TiktokPosterData": "Tiktok Poster Data",
    "YoutubePosterData": "Youtube Poster Data",
    "FacebookPosterData": "Facebook Poster Data",
    "InstagramPosterData": "Instagram Poster Data",
    "TwitterPosterData": "Twitter Poster Data",
    "LinkedinPosterData": "Linkedin Poster Data",
    "PinterestPosterData": "Pinterest Poster Data",
}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
