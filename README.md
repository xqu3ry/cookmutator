**CookMutator** - test cookie parameter with different mutations.

**Download:**

```
git clone https://github.com/xqu3ry/cookmutator
```

```
cd cookmutator
```

**Requirements:**

```
pip3 install requests
```

**Usage:**

```
python3 main.py [OPTIONS]
```

**Options:**

```
options:
  -h, --help            show this help message and exit
  -u, --url URL         Target URL (for example, https://site.local/)
  -c, --cookie COOKIE   Cookie, example: session=...; debug=false
  -X, --method {GET,POST}
                        HTTP-Method
  -d, --data DATA       POST-data (if necessary)
  --header HEADER       Additional HTTP-headers (key:value)
  -o, --output OUTPUT   Report file (json)
  -t, --threads THREADS
                        Threads (default is 16)
  -v, --verbose         Verbose mode
  --no-random-ua        Disable random User-Agent
  --ref REF             Set Referer header
  --show-unique         Only show unique responses by content
  --save-raw            Save raw responses to files
  --compare             Show diff with base response
```

**The utility is not perfect, but it will improve over time.**

**In the next versions it is planned to add:**

-More mutations ;
-Another cookie testing techniques ;
-Make smarter detecting module ;
-Add more cookie types.
