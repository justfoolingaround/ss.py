from .baseclasses import StrategyException
from .header_strategy import (
    CapitalisedHeaderStrategy,
    OrderedHeaderStrategy,
    RefererStrategy,
    UserAgentStrategy,
    XHRStrategy,
)
from .https_omit import HttpOmittingStrategy

all_strategies = {
    OrderedHeaderStrategy,
    CapitalisedHeaderStrategy,
    RefererStrategy,
    XHRStrategy,
    UserAgentStrategy,
    HttpOmittingStrategy,
}
