import click
import regex

KV_PAIR_MATCHER = regex.compile(r"((?:\\=|.)+?)=(.+)")


class KeyValuePair(click.ParamType):
    name = "key-value-pair"

    def convert(self, value, param, ctx):

        if value is None:
            return None

        match = KV_PAIR_MATCHER.fullmatch(value)

        if match is None:
            self.fail("'%s' is not a valid key-value pair" % value, param, ctx)

        return match.groups()


class StringOrPipe(click.ParamType):
    name = "string-or-pipe"

    def convert(self, value, param, ctx):
        if value == "-":
            return click.get_text_stream("stdin").read()
        return value


def request_cli():
    def __inner__(f):

        opts = (
            click.argument(
                "url",
                required=True,
                type=click.STRING,
            ),
            click.option(
                "-p",
                "--params",
                type=KeyValuePair(),
                multiple=True,
                required=False,
                help="The parameters to add with the URL.",
            ),
            click.option(
                "--headers",
                required=False,
                type=KeyValuePair(),
                multiple=True,
                help="The headers to add to the request.",
            ),
            click.option(
                "--method",
                "-m",
                required=False,
                type=click.Choice(
                    (
                        "GET",
                        "POST",
                        "PUT",
                        "DELETE",
                        "PATCH",
                        "HEAD",
                        "OPTIONS",
                        "TRACE",
                    ),
                    case_sensitive=False,
                ),
                default="GET",
                help="The method to use for the request.",
            ),
            click.option(
                "--data",
                "-d",
                required=False,
                type=StringOrPipe(),
                help="The data to send with the request; changes method to POST if method isn't POST or PATCH.",
            ),
            click.option(
                "--timeout",
                "-t",
                required=False,
                type=click.INT,
                help="The timeout for the request.",
            ),
            click.option(
                "--no-verify",
                "-nv",
                is_flag=True,
                help="Don't verify the SSL certificate.",
            ),
            click.option(
                "--disallow-redirects",
                is_flag=True,
                help="Disallow redirects.",
            ),
        )

        for opt in opts:
            f = opt(f)

        return f

    return __inner__
