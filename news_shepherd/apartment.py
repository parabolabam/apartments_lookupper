from dataclasses import dataclass
from typing import Optional
import re
from .constants import CHANNELS  # Import CHANNEL_NAME from the bot module
from telethon.types import Message

@dataclass
class Apartment:
    id: str
    district: str
    address: str
    rooms: int
    bedrooms: int
    area: float
    floor: str
    price: int
    features: list
    location_link: str
    message_id: Optional[int] = None  # Added message_id
    telegram_link: Optional[str] = None  # Added telegram_link

def parse_apartment_message(message: Message) -> Optional[Apartment]:  # Changed parameter type to dict
    # Регулярные выражения для извлечения данных
    id_match = re.search(r'^\*\*(\d{4}-\d{4})\*\*', message.text)
    district_match = re.search(r'#([А-Яа-яA-Za-z]+)', message.text)
    address_match = re.search(r'(?<=\n)([^\n]+)', message.text)
    rooms_match = re.search(r'\*\*Комнат:\*\* #(\d+)к', message.text)
    bedrooms_match = re.search(r'\*\*Спален:\*\* (\d+)', message.text)
    area_match = re.search(r'\*\*Площадь:\*\* (\d+)m²', message.text)
    floor_match = re.search(r'\*\*Этаж:\*\* ([\d/]+)', message.text)
    price_match = re.search(r'\*\*Цена\*\*: [~]*(\d+)\$', message.text)
    features_match = re.findall(r'__- ([^\n]+)', message.text)
    location_match = re.search(r'\📍\[Локация\]\((.*?)\)', message.text)

    # Проверка на наличие обязательных данных
    if not (id_match and district_match and address_match and rooms_match and bedrooms_match 
            and area_match and floor_match and price_match and location_match):
        return None  # Пропускаем сообщение, если данные неполные

    # Construct the telegram link using the message_id
    telegram_link = f"https://t.me/{message.chat.username}/{message.id}"

    return Apartment(
        id=id_match.group(1),
        district=district_match.group(1),
        address=address_match.group(1).strip(),
        rooms=int(rooms_match.group(1)),
        bedrooms=int(bedrooms_match.group(1)),
        area=float(area_match.group(1)),
        floor=floor_match.group(1),
        price=int(price_match.group(1)),
        features=features_match,
        location_link=location_match.group(1),
        message_id=message.id,  # Added message_id
        telegram_link=telegram_link  # Use the constructed telegram_link
    )