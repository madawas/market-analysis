import enum


class DataSources(enum.Enum):
    IEX_CLOUD = 0
    ALPHA_VANTAGE = 1
    RAPID_API_YF = 2
    YAHOO_FINANCE = 3


DEFAULT_DATA_SOURCE_FALLBACK_ORDER = [DataSources.IEX_CLOUD, DataSources.ALPHA_VANTAGE, DataSources.RAPID_API_YF,
                                      DataSources.YAHOO_FINANCE]
