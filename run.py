import itertools
import math

import click
import regex
import requests
import rich
from rich.progress import Progress

from decorators import request_cli
from strategies import all_strategies
from strategies.baseclasses import StrategyException

SCHEME_REGEX = regex.compile(r"^(.+?)://")


def usability_check(strategy, *args, **kwargs):

    if hasattr(strategy, "header_key"):
        headers = kwargs.pop("headers", [])

        if any(
            header_key.lower() == strategy.header_key.lower() for header_key in headers
        ):
            return False

    if hasattr(strategy, "schemes"):
        url = kwargs.pop("url")

        scheme = SCHEME_REGEX.match(url)

        if scheme is None:
            raise RuntimeError(
                f"URL {url!r} does not have a scheme; provide a scheme [http/https]."
            )

        if scheme.group(1) not in strategy.schemes:
            return False

    return True


def iter_explanation_lines(response: requests.Response):

    yield f"Response HTTP/1.1 {response.status_code} {response.reason}"

    for header, value in response.headers.items():
        yield f"\t{header!r}: {value!r}"

    yield f"Request [{response.request.method} {response.url}]"

    for header, value in response.request.headers.items():
        yield f"\t{header!r}: {value!r}"

    yield f"\tTime elapsed: {response.elapsed.total_seconds():.02f}s"


@click.command()
@request_cli()
def content_access_strategies(
    url,
    params,
    headers,
    method,
    data,
    timeout,
    no_verify,
    disallow_redirects,
):

    console = rich.get_console()

    if data and method not in ("POST", "PUT", "PATCH"):
        method = "POST"

    usable_strategies = set(
        _
        for _ in all_strategies
        if usability_check(
            _,
            headers=headers,
            url=url,
            method=method,
            data=data,
            params=params,
            timeout=timeout,
            no_verify=no_verify,
            disallow_redirects=disallow_redirects,
        )
    )

    combinables = set(_ for _ in (usable_strategies) if _.combinable)
    uncombinables = usable_strategies - combinables

    combinations_iterator = itertools.chain(
        *tuple(
            itertools.combinations(combinables, n) for n in range(len(combinables) + 1)
        )
    )

    def session_manager(session_cls: "type[requests.Session]" = requests.Session):
        session = session_cls()
        session.verify = not no_verify
        session.timeout = timeout
        session.allow_redirects = not disallow_redirects
        session.headers.pop("User-Agent", None)
        session.headers.update(dict(headers))

        def executor():
            return session.request(method, url, params=dict(params), data=data)

        return session, executor

    with Progress(console=console) as progress:

        total_strategies = sum(
            math.comb(len(combinables), n) for n in range(len(combinables) + 1)
        ) + len(uncombinables)

        strategiser_task = progress.add_task(
            "Running strategies", total=total_strategies
        )

        for count, strategies in enumerate(
            itertools.chain(combinations_iterator, ((_,) for _ in uncombinables)), 1
        ):

            console.print(f"On combination {count}:")

            priority_sorted = sorted(strategies, key=lambda _: _.priority)

            suffix = f" using {', '.join(repr(_.__name__) for _ in strategies) or 'no'} strategy(s)."
            console.print(f"\t[yellow]Running[/]" + suffix)

            used_strategies = set()

            session, executor = session_manager()

            for strategy in priority_sorted:
                console.print(
                    f"\t\tExecuting {strategy.__name__!r}, goal: {strategy.goal}"
                )
                try:
                    strategy(session).execute()
                    used_strategies.add(strategy)
                except StrategyException as strategy_exception:
                    console.print(
                        f"\t\t{strategy.__name__} failed due to {strategy_exception!r}"
                    )

            response = executor()

            after_suffix = f" after using {', '.join(repr(_.__name__) for _ in used_strategies) or 'no'} strategy(s)."

            if response.ok:
                console.print(f"[green]Obtained[/] {response!r}" + after_suffix)

                for line in iter_explanation_lines(response):
                    console.print(line)

                progress.update(
                    strategiser_task,
                    completed=total_strategies,
                    description="Strategies complete",
                )
                return

            console.print(
                f"\t[red]Failed[/] to obtain valid response ({response!r})"
                + after_suffix,
            )
            del session

            progress.update(strategiser_task, advance=1)

        progress.update(
            strategiser_task,
            completed=total_strategies,
            description="All strategies failed",
        )

    console.print(
        "[red]Nothing worked :/.[/]",
    )


if __name__ == "__main__":
    content_access_strategies()
