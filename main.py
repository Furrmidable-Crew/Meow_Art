from cat.mad_hatter.decorators import tool, plugin
from pydantic import BaseModel, Field, model_validator
from cat.log import log
from enum import Enum
import requests
import json

class ImageSize(Enum):
    quad: str = '1024x1024'
    width: str = '1792x1024'
    height: str = '1024x1792'
    medium: str = '512x512'
    low: str = '256x256'

class Quality(Enum):
    hd: str = 'hd'
    standard: str = 'standard'

class Style(Enum):
    natural: str = 'natural'
    vivid: str = 'vivid'

class Model(Enum):
    dalle3: str = 'dall-e-3'
    dalle2: str = 'dall-e-2'

class Settings(BaseModel):
    api_key: str = Field(title="API Key", description="The API key for OpenAI's image generation API.", default=""),
    image_size: ImageSize = Field(title="Image size", description="The size for the image to generate. For dall-e-3 you can choose between '1024x1024', '1792x1024' and '1024x1792' while for dall-e-2 you can choose between '1024x1024', '512x512' and '256x256'", default=ImageSize.quad),
    quality: Quality = Field(title="Image quality", description="The quality for the image to generate. It will be used only with dall-e-3", default=Quality.hd),
    style: Style = Field(title="Image style", description="The style for the image to generate. It will be used only with dall-e-3", default=Style.natural),
    model: Model = Field(title="Model", description="The model to use for the image to generate", default=Model.dalle3)    
    
    @model_validator(mode='after')
    def check_image_size_validator(self) -> 'Settings':
        model = self.model
        threshold = self.image_size
        if  (threshold == ImageSize.width and model == Model.dalle2) or (threshold == ImageSize.height and model == Model.dalle2):
            raise ValueError("Image size not acepted for this model, please select a '1024x1024' or less")
        if  (threshold == ImageSize.medium and model == Model.dalle3) or (threshold == ImageSize.low and model == Model.dalle3):
            raise ValueError("Image size not acepted for this model, please select a '1024x1024' or more")
        return self


    
@plugin
def settings_model():
    return Settings

@tool(return_direct=True)
def generate_image(tool_input, cat):
    """
    Useful to generate an image based on a text.
    The input is the user's requested image.
    """

    settings = cat.mad_hatter.plugins["meow_art"].load_settings()

    if settings == {}:
        log.error("No configuration found for MeowArt")
        return "You did not configure the API key for the image generation API!"

    req = requests.post("https://api.openai.com/v1/images/generations", 
                        headers={
                            "Authorization": f"Bearer {settings['api_key']}",
                            "Content-Type": "application/json"
                        }, data=json.dumps({
                            "quality": settings['quality'],
                            "model": settings['model'],
                            "prompt": tool_input,
                            "style": settings['style'],
                            "size": settings['image_size']
                        }))
    res = req.json()

    image = res['data'][0]['url']

    size = settings['image_size'].split('x')
    # TODO: It would be nice to add a button to download the original quality of the image
    return f"<img src='{image}' style='width: {int(size[0]) / 2}px; height: {int(size[1]) / 2}px;' alt='Generated image' />"
