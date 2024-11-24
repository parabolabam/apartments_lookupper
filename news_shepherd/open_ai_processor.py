import json
from typing import Any, Dict
from openai import OpenAI
import os

from news_shepherd.constants import MODEL


class OpenAIProcessor:

    def __init__(
        self,
    ):
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set in the environment")

        self.client = OpenAI(api_key=OPENAI_API_KEY)

    async def create_user_criteria(self, user_description: str) -> Dict[str, Any]:
        """
        Convert a natural language description of preferences into structured criteria.

        Args:
            user_description: e.g. "I'm looking for a 2-bedroom apartment in Vake or Saburtalo,
                             max $1000, must have parking"
        """
        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": """Convert user apartment preferences into structured criteria. 
                     Extract specific requirements for price, rooms, location, amenities, etc.""",
                    },
                    {
                        "role": "user",
                        "content": f"""
                    Convert this apartment search description into JSON criteria:
                    {user_description}
                    
                    Format the response as JSON with these possible fields:
                    - max_price
                    - min_price
                    - min_rooms
                    - max_rooms
                    - districts (array)
                    - must_have (array of required amenities)
                    - nice_to_have (array of preferred but not required amenities)
                    - max_floor
                    - other_requirements (array)
                    """,
                    },
                ],
                response_format={"type": "json_object"},
            )

            return json.loads(response.choices[0].message.content or "")
        except Exception as e:
            print(f"Error creating user criteria with OpenAI: {e}")
            return {}
