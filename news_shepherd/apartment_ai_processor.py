import os
from typing import Optional, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
import json
from .constants import MODEL
from .open_ai_processor import OpenAIProcessor

from news_shepherd.apartment import Apartment

load_dotenv()


# Initialize OpenAI client
class ApartmentAIProcessor(OpenAIProcessor):

    async def analyze_listing(
        self,
        text: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze apartment listing text using OpenAI and match against user criteria.

        Args:
            text: The apartment listing text
            user_criteria: Dictionary containing user preferences like:
                {
                    "max_price": 1000,
                    "min_rooms": 2,
                    "districts": ["Vake", "Saburtalo"],
                    "must_have": ["parking", "elevator"],
                    "max_floor": 10
                }
        """
        try:
            criteria_str = "\n".join(
                f"- {k}: {v}" for k, v in self.user_criteria.items()
            )

            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an AI assistant that analyzes apartment listings 
                     and determines if they match user criteria. Extract key information and provide a clear 
                     match/no match decision with explanation. Explanation must be reasoned, you must got through all criteria and explain why the match.""",
                    },
                    {
                        "role": "user",
                        "content": f"""
                    User is looking for an apartment with these criteria:
                    {criteria_str}
                    
                    Please analyze this listing and return a JSON response:
                    {text}
                    
                    Format your response as a JSON with these fields:
                    - matches_criteria (boolean)
                    - explanation (string)
                    - extracted_info (object with price, rooms, location, etc.)
                    - missing_criteria (array of criteria that couldn't be determined)
                    """,
                    },
                ],
                response_format={"type": "json_object"},
            )

            return json.loads(response.choices[0].message.content or "")
        except Exception as e:
            print(f"Error processing message with OpenAI: {e}")
            return None

    async def analyze_listing_batch(
        self, apartments: list[Apartment], user_criteria: Dict[str, Any]
    ) -> Optional[list[Dict[str, Any]]]:
        """
        Analyze multiple apartment listings using OpenAI and match against user criteria.

        Args:
            texts: List of apartment listing texts
            user_criteria: Dictionary containing user preferences
        Returns:
            List of analysis results, one for each input listing
        """
        try:
            criteria_str = "\n".join(f"- {k}: {v}" for k, v in user_criteria.items())

            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an AI assistant that analyzes multiple apartment listings 
                     and determines if they match user criteria. For each listing, extract key information and provide 
                     a clear match/no match decision with explanation.""",
                    },
                    {
                        "role": "user",
                        "content": f"""
                    User is looking for an apartment with these criteria:
                    {criteria_str}
                    
                    Please analyze these listings and return a JSON response with an array of results.
                    Listings to analyze:
                    {[f"Listing {i+1}: {text}" for i, text in enumerate(apartments)]}
                    
                    Format your response as a JSON with an array of objects, each containing:
                    - matches_criteria (boolean)
                    - thorough_explanation (string)
                    - extracted_info (object with price, rooms, location, link to original telegram message and link to location on maps)
                    - missing_criteria (array of criteria that couldn't be determined)
                    """,
                    },
                ],
                response_format={"type": "json_object"},
            )

            return json.loads(response.choices[0].message.content or "")
        except Exception as e:
            print(f"Error processing batch with OpenAI: {e}")
            return None
