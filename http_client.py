import requests
import time

def send_request(method, url, cookies, headers, data=None, timeout=7):
    start = time.time()
    try:
        if method.upper() == "GET":
            resp = requests.get(url, cookies=cookies, headers=headers, timeout=timeout, allow_redirects=True)
        elif method.upper() == "POST":
            resp = requests.post(url, cookies=cookies, headers=headers, data=data, timeout=timeout, allow_redirects=True)
        else:
            raise Exception(f"Unsupported HTTP method: {method}")
        rtt = int((time.time() - start) * 1000)
        return resp.status_code, resp.text, resp.headers, rtt
    except Exception as e:
        rtt = int((time.time() - start) * 1000)
        return None, f"Error: {e}", {}, rtt