from decimal import Decimal
from passlib.context import CryptContext
import re
from datetime import datetime
import random
import string
from rapidfuzz import process, fuzz


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def div_ceil(nominator, denominator):
    a = nominator // denominator
    b = 1 if nominator % denominator > 0 else 0
    return a + b

def generate_random_code(length: int = 10) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def map_fields(headers, expected_fields):
    mapped_fields = {}
    for header in headers:
        match_data = process.extractOne(header, expected_fields.keys(), scorer=fuzz.partial_ratio)
        if match_data:  # Ensure match_data is not None
            match, score, _ = match_data
            if score > 80:  # If the similarity score is above a threshold
                mapped_fields[header] = expected_fields[match]
            else:
                mapped_fields[header] = header
        else:
            mapped_fields[header] = header
    return mapped_fields