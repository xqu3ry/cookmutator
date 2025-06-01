import re
from difflib import SequenceMatcher

INTERESTING_PATTERNS = [
    re.compile(r"(sql syntax|mysql|syntax error|sqlstate|odbc|pdoexception|pg_query|unclosed quotation mark)", re.I),
    re.compile(r"(exception|traceback|runtime error|fatal error|undefined|stack trace)", re.I),
    re.compile(r"(root:|superuser|uid=0|gid=0|sudoers)", re.I),
    re.compile(r"(token|auth|session|access[_\-]?token|api[_\-]?key|secret)", re.I),
    re.compile(r"(set-cookie)", re.I),
    re.compile(r"(admin|administrator|superadmin)", re.I),
    re.compile(r"(debug|dev mode|development build)", re.I),
    re.compile(r"(path: /.+/|in /[a-z0-9_\-/]+\.php|at /[a-z0-9_\-/]+\.(js|py|rb|java|go|dll|so))", re.I),
    re.compile(r"(password|pass:|pwd=)", re.I),
    re.compile(r"(not\s+authorized|not\s+allowed|access\s+denied)", re.I),
    re.compile(r"(csrf|xsrf|cross[-_ ]site)", re.I),
    re.compile(r"(jwt|bearer\s+[a-z0-9\-_.]+)", re.I),
]

def get_diff(a, b, maxlen=80):
    s = SequenceMatcher(None, a or "", b or "")
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag != "equal":
            return f"Δ: [{a[i1:i2]}] → [{b[j1:j2]}]"
    return ""

def analyze_response(status, text, headers, mutation, cookies, base_text=None):
    findings = []
    textlow = text.lower() if text else ""
    # Detect interesting patterns
    for pat in INTERESTING_PATTERNS:
        if pat.search(textlow):
            findings.append(f"Pattern: {pat.pattern}")

    # HTTP status
    if status == 200:
        if "admin" in textlow and "user" not in mutation.lower():
            findings.append("Response contains 'admin'")
        if "debug" in textlow or "dev" in textlow:
            findings.append("Response contains dev/debug-artifact")
        if "error" in textlow or "exception" in textlow or "traceback" in textlow:
            findings.append("Response contains error/exception")
        if "set-cookie" in (h.lower() for h in headers.keys()):
            findings.append("Response contains 'Set-Cookie'")
        if "root" in textlow or "superuser" in textlow:
            findings.append("Response contains root/superuser")
    else:
        if status and (status >= 400 or status < 200 or status > 308):
            findings.append(f"Unusual HTTP status: {status}")
    if status in (401, 403):
        findings.append("Access limited (401/403)")
    if status in (301, 302, 307, 308):
        location = headers.get("Location") or headers.get("location")
        if location:
            findings.append(f"Redirect to: {location}")
        else:
            findings.append("Redirect — check Location")
    if "debug" in cookies or "dev" in cookies:
        if cookies.get("debug") == "true" or cookies.get("dev") == "true":
            if "debug" in textlow or "dev" in textlow:
                findings.append("Enabled debug/dev cookie influences the answer")
    if base_text is not None and text and text != base_text:
        delta = get_diff(base_text, text, maxlen=80)
        findings.append(f"Diff with base: {delta}")
        if abs(len(text) - len(base_text)) > 80:
            findings.append(f"Response length changed: {len(base_text)} → {len(text)}")
    return findings
