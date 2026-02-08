import os
from typing import Optional
from agno.tools import Toolkit
from openai import OpenAI

class OpenAIDalleTool(Toolkit):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="openai_dalle_tool")
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.register(self.generate_image)

    def generate_image(self, prompt: str = "") -> str:
        """
        Generates a UPSC diagram and returns it as a resizing HTML tag.
        """
        if not prompt:
             return ""

        try:
            # STYLE LOCK: Forces "Schematic" look to reduce clutter/gibberish
            TOPPER_STYLE = (
                "UPSC Technical Diagram: Black and white line art on white paper. "
                "Style: Minimalist, academic, 2D schematic. "
                "No 3D shading. No artistic backgrounds. "
                "Clearly labeled with legible English text. "
                "Subject: "
            )
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=TOPPER_STYLE + prompt,
                size="1024x1792", # Landscape mode (Fits answer sheet better)
                quality="standard",
                n=1,
            )

            if not response.data:
                return ""

            image_url = response.data[0].url
            
            # THE FIX: Return HTML with fixed width="400"
            # This forces the image to be small (approx 1/3rd of page width)
            html_tag = (
                f'<div align="center">'
                f'<figure>'
                f'<img src="{image_url}" alt="UPSC Sketch" width="200" style="border:1px solid #ccc; margin: 10px;">'
                f'<figcaption style="font-size: 12px; color: #555;"><i>Fig: Generated Diagram</i></figcaption>'
                f'</figure>'
                f'</div>'
            )
            return html_tag

        except Exception as e:
            print(f"❌ DALL-E Error: {str(e)}")
            return ""


# Inside PollinationsImageTool
# def generate_image(self, prompt: str) -> str:
#     # ... previous setup ...
    
#     # CRITICAL FIX: Truncate prompt to 200 chars to prevent 502 Errors
#     safe_prompt = prompt[:200] 
    
#     encoded_prompt = urllib.parse.quote(safe_prompt)
#     image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={seed}&model=flux&width=1200&height=800&nologo=true"
    
#     return f"![Sketch]({image_url})"