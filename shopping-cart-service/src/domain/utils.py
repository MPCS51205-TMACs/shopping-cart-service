import pytz
import datetime

TIME_ZONE = pytz.timezone("UTC")
TIME_PARSE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

def toSQLTimestamp6Repr(aDatetime: datetime.datetime) -> str:
    return aDatetime.strftime(TIME_PARSE_FORMAT)

def toDatetimeFromStr(aStrDatetime: str) -> datetime.datetime:
    return TIME_ZONE.localize(datetime.datetime.strptime(aStrDatetime,TIME_PARSE_FORMAT))

def localize(aDatetime: datetime.datetime) -> datetime.datetime:
    return TIME_ZONE.localize(aDatetime)

# def prettify(aDatetime: datetime.datetime) -> str: pass

def to_fancy_dollars(cents: int) -> str:
    return  f'${cents/100:,.2f}'

def short_str(letters: str, limit : int = 6) -> str:
    return (letters[:limit] + '..') if len(letters) > limit else letters