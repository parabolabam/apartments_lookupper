import os
from typing import Optional, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()


# Initialize OpenAI client
class ApartmentAIProcessor:
    def __init__(self):
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set in the environment")

        self.client = OpenAI(api_key=OPENAI_API_KEY)

    async def process_message_with_openai(self, text):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes apartment listings."},
                    {"role": "user", "content": f"Please analyze this apartment listing and extract key information: {text}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error processing message with OpenAI: {e}")
            return None

    async def analyze_listing(self, text: str, user_criteria: Dict[str, Any]) -> Optional[Dict[str, Any]]:
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
            criteria_str = "\n".join(f"- {k}: {v}" for k, v in user_criteria.items())
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are an AI assistant that analyzes apartment listings 
                     and determines if they match user criteria. Extract key information and provide a clear 
                     match/no match decision with explanation."""},
                    {"role": "user", "content": f"""
                    User is looking for an apartment with these criteria:
                    {criteria_str}
                    
                    Please analyze this listing and return a JSON response:
                    {text}
                    
                    Format your response as a JSON with these fields:
                    - matches_criteria (boolean)
                    - explanation (string)
                    - extracted_info (object with price, rooms, location, etc.)
                    - missing_criteria (array of criteria that couldn't be determined)
                    """}
                ],
                response_format={ "type": "json_object" }
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error processing message with OpenAI: {e}")
            return None

    async def create_user_criteria(self, user_description: str) -> Dict[str, Any]:
        """
        Convert a natural language description of preferences into structured criteria.
        
        Args:
            user_description: e.g. "I'm looking for a 2-bedroom apartment in Vake or Saburtalo, 
                             max $1000, must have parking"
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """Convert user apartment preferences into structured criteria. 
                     Extract specific requirements for price, rooms, location, amenities, etc."""},
                    {"role": "user", "content": f"""
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
                    """}
                ],
                response_format={ "type": "json_object" }
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error creating user criteria with OpenAI: {e}")
            return None