<h1 align="center"><sup><b>S</b>trategised</sup><sub><b>S</b>craping</sub>.py</h1>

A command-line utility that attempts to get a good response from a URL by utilising scraper disguising strategies.

<h2>Usage</h2>

```
Usage: run.py [OPTIONS] URL

Options:
  --disallow-redirects            Disallow redirects.
  -nv, --no-verify                Don't verify the SSL certificate.
  -t, --timeout INTEGER           The timeout for the request.
  -d, --data STRING-OR-PIPE       The data to send with the request; changes
                                  method to POST if method isn't POST or
                                  PATCH.
  -m, --method [GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|TRACE]
                                  The method to use for the request.
  --headers KEY-VALUE-PAIR        The headers to add to the request.
  -p, --params KEY-VALUE-PAIR     The parameters to add with the URL.
  --help                          Show this message and exit.
```


<h3>Currently supported strategies</h3>

- Sorted and ordered headers [strategy](https://stackoverflow.com/a/62687390)

    Use `collections.abc.OrderedDict` & `sorted`.

- Title-cased headers [strategy](https://stackoverflow.com/a/62816482)

    Use `regex.sub` with `(?<=^|[-\s]+)([a-z])` and a `match.group(1).upper()` function. Note that normal `re.sub` will **not** work: It requires a constant string length in the `+ve lookaround`.

- Referer, User-Agent and XHR headers strategy

    Use `https://www.google.com/` as `Referer`, `justfoolingaround/1.0` as `User-Agent` and `XMLHttpRequest` as `X-Requested-With`.


- HTTPS omitting strategy

    Use `http` scheme with a single redirect: if that redirect is available.

<h3>Mechanism</h3>

The internal strategiser mechanism uses combinations of the above strategies alongside a easy and robust strategy defining framework.

The strategy-less request does not give an `User-Agent` to the server. It does, however, send the general headers that almost all HTTP clients send.

```json
{
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "*/*",
    "Connection": "keep-alive"
}
```

Please read the outputs properly and make changes to your existing scrapers accordingly.

We use `requests.Session` as the fresh session class for **each** combination.

<h2>What this is not</h2>

This isn't a CSP bypass utility; it cannot bypass Cloudflare protections. This project just makes sure you get the same response from a URL between your browser and your scraper. In some cases, where Cloudflare's IUAM **only** triggers with a scraper, this will probably work.

<h3>Instances of valuable results</h3>

```sh
$ py run.py "https://www.crunchyroll.com/"
...
Obtained <Response [200]> after using 'HttpOmittingStrategy' strategy(s).
Response HTTP/1.1 200 OK
...
$ py run.py "https://www.animixplay.to/"
...
Obtained <Response [200]> after using 'UserAgentStrategy' strategy(s).
Response HTTP/1.1 200 OK
...
```
