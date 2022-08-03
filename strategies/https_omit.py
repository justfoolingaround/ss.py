import regex
import requests

from .baseclasses import Strategiser, StrategiserMeta

HTTPS_URL_MATCHER = regex.compile(r"^https")


def http_to_https_strategy(session: requests.Session):

    __request__ = session.request

    def request(method, url, *args, **kwargs):

        allow_redirects = kwargs.pop("allow_redirects", True)

        url = HTTPS_URL_MATCHER.sub(lambda _: "http", url)

        if not allow_redirects:
            response = __request__(
                method, url, *args, **kwargs, allow_redirects=allow_redirects
            )

            if response.is_redirect:
                response = __request__(
                    method,
                    response.headers["Location"],
                    *args,
                    **kwargs,
                    allow_redirects=allow_redirects
                )

            return response

        return __request__(method, url, *args, **kwargs)

    session.request = request


class HttpOmittingStrategy(
    Strategiser,
    metaclass=StrategiserMeta,
    setter=None,
    combinable=True,
    strategy=http_to_https_strategy,
):
    priority = 0b01
    goal = "Attempts to convert HTTP to HTTPS before sending the request."

    schemes = ("https",)
