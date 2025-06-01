import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from mutations import mutate_cookie_value
from http_client import send_request
from analyzer import analyze_response
from utils import parse_cookies, smart_headers, colorize

def do_test(mut_id, cookies, method, url, headers, data, base_text=None):
    status, text, resp_headers, rtt = send_request(method, url, cookies, headers, data)
    findings = analyze_response(status, text, resp_headers, mut_id, cookies, base_text=base_text)
    snippet = text[:300] if text else ""
    return {
        "mutation": mut_id,
        "cookies": cookies,
        "status": status,
        "findings": findings,
        "snippet": snippet,
        "length": len(text) if text else 0,
        "rtt": rtt,
    }

def banner():
    print(colorize("""
  
      Cookie Mutation Tester v0.1 — by xqu3ry      
        
   
""", "cyan"))

def main():
    banner()
    parser = argparse.ArgumentParser(
        description="Cookie Mutation Tester — testing cookie parameter with different mutations"
    )
    parser.add_argument("-u", "--url", required=True, help="Target URL (for example, https://site.local/)")
    parser.add_argument("-c", "--cookie", required=True, help="Cookie, example: session=...; debug=false")
    parser.add_argument("-X", "--method", default="GET", choices=["GET", "POST"], help="HTTP-Method")
    parser.add_argument("-d", "--data", default=None, help="POST-data (if necessary)")
    parser.add_argument("--header", action="append", default=[], help="Additional HTTP-headers (key:value)")
    parser.add_argument("-o", "--output", help="Report file (json)")
    parser.add_argument("-t", "--threads", type=int, default=8, help="Threads (default is 16)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
    parser.add_argument("--no-random-ua", action="store_true", help="Disable random User-Agent")
    parser.add_argument("--ref", help="Set Referer header")
    parser.add_argument("--show-unique", action="store_true", help="Only show unique responses by content")
    parser.add_argument("--save-raw", action="store_true", help="Save raw responses to files")
    parser.add_argument("--compare", action="store_true", help="Show diff with base response")

    args = parser.parse_args()
    base_cookies = parse_cookies(args.cookie)
    headers = smart_headers(args.header, random_ua=not args.no_random_ua)
    if args.ref: headers["Referer"] = args.ref
    data = args.data

    # Basic response for comparing
    base_status, base_text, base_headers, base_rtt = send_request(args.method, args.url, base_cookies, headers, data)
    print(colorize(f"\nBase request: HTTP {base_status} ({len(base_text) if base_text else 0} bytes, {base_rtt} ms)", "yellow"))

    # Mutations generation
    all_mutated = {}
    for cname, cval in base_cookies.items():
        muts = mutate_cookie_value(cval)
        for mkey, mval in muts.items():
            mut_cookies = base_cookies.copy()
            mut_cookies[cname] = mval
            all_mutated[f"{cname}_{mkey}"] = mut_cookies

    print(colorize(f"\nMutations loaded: {len(all_mutated)} (Threads using: {args.threads})\n", "yellow"))
    results = []
    seen_hashes = set()
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {
            executor.submit(
                do_test, mut_id, cookies, args.method, args.url, headers, data, base_text
            ): mut_id for mut_id, cookies in all_mutated.items()
        }
        for future in as_completed(futures):
            entry = future.result()
            results.append(entry)
            mut_id = entry["mutation"]
            findings = entry["findings"]
            status = entry["status"]
            snippet = entry["snippet"]
            resp_hash = hash(entry["snippet"])
            show = True
            if args.show_unique and resp_hash in seen_hashes:
                show = False
            if args.show_unique:
                seen_hashes.add(resp_hash)
            if findings and show:
                print(colorize(f"[{mut_id}] HTTP {status} | Findings: {findings} | Δ {entry['length']}b | {entry['rtt']}ms", "green"))
                if snippet:
                    print(colorize(f"  -> {snippet.replace(chr(10),' ')[:120]}...", "yellow"))
            elif args.verbose and show:
                print(colorize(f"[{mut_id}] HTTP {status} | No findings | {entry['length']}b | {entry['rtt']}ms", "cyan"))
                if snippet:
                    print(colorize(f"  -> {snippet.replace(chr(10),' ')[:120]}...", "yellow"))
            if args.save_raw:
                with open(f"raw_{mut_id}.txt", "w", encoding="utf-8") as f:
                    f.write(entry["snippet"])
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(colorize(f"\nReport saved to {args.output}", "yellow"))
    else:
        print(colorize("\nUse -o report.json to save full report.", "yellow"))

if __name__ == "__main__":
    main()
