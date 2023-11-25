from cat.mad_hatter.decorators import tool, plugin
from pydantic import BaseModel, Field
from enum import Enum
import requests
import json

class ImageSize(Enum):
    quad: str = '1024x1024'
    width: str = '1792x1024'
    height: str = '1024x1792'

class Settings(BaseModel):
    api_key: str = Field(title="API Key", description="The API key for OpenAI's transcription API.", default="")
    image_size: ImageSize = Field(title="Image size", description="The size for the image to generate", default=ImageSize.quad)

@plugin
def settings_schema():   
    return Settings.schema()

@tool(return_direct=True)
def generate_image(tool_input, cat):
    """
    A plugin used to generate an image based on a text.
    The input is the text used as a prompt for the image generation.
    """

    settings = cat.mad_hatter.plugins["meow_art"].load_settings()

    req = requests.post("https://api.openai.com/v1/images/generations", 
                        headers={
                            "Authorization": f"Bearer {settings['api_key']}",
                            "Content-Type": "application/json"
                        }, data=json.dumps({
                            "quality": "hd",
                            "model": "dall-e-3",
                            "prompt": tool_input,
                            "size": settings['image_size']
                        }))
    res = req.json()

    image = res['data'][0]['url']

    size = settings['image_size'].split('x')

    return f"<img src='{image}' style='width: {int(size[0]) / 2}px; height: {int(size[1]) / 2}px;' alt='Generated image' />"
