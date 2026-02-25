# uidlib.py
import re
import uuid

UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}$"
)

UID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}-"
    r"[0-9a-fA-F]$"
)

def checksum_char_from_uuid(uuid36: str) -> str:
    """
    UUID 36 символов (8-4-4-4-12) -> контрольный символ (1 hex)
    Алгоритм: убрать дефисы, hex->dec, веса 1..10 циклично, sum, mod 16, hex.
    """
    if not UUID_RE.match(uuid36):
        raise ValueError("Некорректный UUID: ожидается формат 8-4-4-4-12 (hex).")

    hex32 = uuid36.replace("-", "").lower()
    digits = [int(ch, 16) for ch in hex32]  # a-f -> 10..15

    total = 0
    weight = 1
    for d in digits:
        total += d * weight
        weight += 1
        if weight == 11:
            weight = 1

    rem = total % 16
    return format(rem, "x")  # 0-9a-f

def generate_uid() -> str:
    u = str(uuid.uuid4()).lower()
    c = checksum_char_from_uuid(u)
    return f"{u}-{c}"

def validate_uid(uid38: str) -> bool:
    if not UID_RE.match(uid38):
        return False
    uuid36, c = uid38.rsplit("-", 1)
    try:
        expected = checksum_char_from_uuid(uuid36)
    except ValueError:
        return False
    return expected.lower() == c.lower()