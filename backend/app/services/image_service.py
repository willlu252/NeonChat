# app/services/image_service.py
from typing import Dict, Any
from openai import AsyncOpenAI
from ..utils.config_utils import get_api_key

class ImageService:
    """Service for handling image generation operations."""
    
    def __init__(self):
        self.openai_api_key = get_api_key("openai")
    
    async def generate_image(self, prompt: str, size: str = "1024x1024", quality: str = "standard", style: str = "vivid") -> Dict[str, Any]:
        """
        Generate an image using OpenAI's DALL-E 3 API
        
        Args:
            prompt: The text prompt to generate an image from
            size: Image size - "1024x1024", "1792x1024", or "1024x1792"
            quality: Image quality - "standard" or "hd"
            style: Image style - "vivid" or "natural"
            
        Returns:
            Dictionary containing the generated image data or error
        """
        if not self.openai_api_key:
            print("ERROR: OpenAI API key not found in configuration.")
            return {"error": "API key not configured"}
        
        try:
            client = AsyncOpenAI(api_key=self.openai_api_key)
            response = await client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                style=style,
                n=1
            )
            
            # Return the image URL or base64 data
            return {
                "url": response.data[0].url,
                "revised_prompt": response.data[0].revised_prompt
            }
        except Exception as e:
            print(f"ERROR: Image generation failed: {str(e)}")
            return {"error": str(e)}

# Create a global service instance
image_service = ImageService()
