from dataclasses import dataclass
from typing import Optional
import re

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

def parse_apartment_message(message: str) -> Optional[Apartment]:
    # Регулярные выражения для извлечения данных
    id_match = re.search(r'^\*\*(\d{4}-\d{4})\*\*', message)
    district_match = re.search(r'#([А-Яа-яA-Za-z]+)', message)
    address_match = re.search(r'(?<=\n)([^\n]+)', message)
    rooms_match = re.search(r'\*\*Комнат:\*\* #(\d+)к', message)
    bedrooms_match = re.search(r'\*\*Спален:\*\* (\d+)', message)
    area_match = re.search(r'\*\*Площадь:\*\* (\d+)m²', message)
    floor_match = re.search(r'\*\*Этаж:\*\* ([\d/]+)', message)
    price_match = re.search(r'\*\*Цена\*\*: [~]*(\d+)\$', message)
    features_match = re.findall(r'__- ([^\n]+)', message)
    location_match = re.search(r'\📍\[Локация\]\((.*?)\)', message)

    # Проверка на наличие обязательных данных
    if not (id_match and district_match and address_match and rooms_match and bedrooms_match 
            and area_match and floor_match and price_match and location_match):
        return None  # Пропускаем сообщение, если данные неполные

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
        location_link=location_match.group(1)
    )