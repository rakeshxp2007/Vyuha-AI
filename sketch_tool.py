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
        Generates a topper-style academic sketch for UPSC GS-1 using OpenAI DALL-E 3.
        Gracefully handles failures by returning a text placeholder.
        """
        if not prompt:
             return "\n\n*[System: No diagram description provided]*\n\n"

        try:
            # STYLE INJECTION: Forces NCERT look and Legible English
            style_prefix = (
                "Style: NCERT India textbook academic diagram. "
                "Type: Black and white pencil line art on white background. "
                "Constraint: Use ONLY English text for labels. No gibberish. "
                "Layout: Minimalist, clear, high-contrast. "
                "Subject: "
            )
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=style_prefix + prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            # SAFETY CHECK
            if not response.data:
                return "\n\n*[System: Image generation skipped]*\n\n"

            image_url = response.data[0].url
            
            # RESIZING FIX: Use HTML instead of Markdown to force size
            # width="400" creates a manageable box. 'align="center"' centers it.
            html_tag = (
                f'<div align="center">'
                f'<img src="{image_url}" alt="UPSC Sketch" width="400" style="border:1px solid #ccc; padding:5px; margin: 10px;">'
                f'</div>'
            )
            return html_tag

        except Exception as e:
            return f"\n\n*[Image Generation Error: {str(e)}]*\n\n"






# tried using free image generation tool but getting 502 bad gateway error always so trying with paid model

# import random
# import urllib.parse
# from agno.tools import Toolkit

# class PollinationsImageTool(Toolkit):
#     def __init__(self):
#         super().__init__(name="pollinations_image_tool")
#         self.register(self.generate_image)

#     def generate_image(self, prompt: str) -> str:
#         """
#         Generates a topper-style academic sketch for UPSC GS-1 using Pollinations AI.

#         Args:
#             prompt (str): The description of the image.
    
#         Returns:
#             str: A formatted Markdown string containing the image URL.
#         """
#         # 1. Flatten the prompt (Remove all newlines/tabs)
#         clean_text = " ".join(prompt.split())
        
#         # 2. Safety Strip (Remove extensions/params if agent added them)
#         if ".png" in clean_text:
#             clean_text = clean_text.split(".png")[0]
#         if "?" in clean_text:
#             clean_text = clean_text.split("?")[0]
            
#         # 3. URL Encode (safe='' encodes slashes '/' to '%2F' to prevent path errors)
#         encoded_prompt = urllib.parse.quote(clean_text.strip(), safe='')
        
#         # 4. Generate Random Seed
#         seed = random.randint(1, 10000)
        
#         # 5. Construct URL with MODEL Parameter
#         # We add 'model=flux' which is currently more stable/faster than the default
#         image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}.png?seed={seed}&model=flux&nologo=true"
        
#         # 6. Return Clean Markdown
#         return f"\n\n![UPSC_SKETCH]({image_url})\n\n"