from datetime import datetime, timedelta


class TimeStamp:

  @staticmethod
  def timezone_name() -> str:
    """Returns the current timezone name."""
    return datetime.now().astimezone().tzname() or ""

  @staticmethod
  def timezone_offset() -> timedelta:
    """Returns the current timezone offset from UTC time."""
    return datetime.now().astimezone().utcoffset() or timedelta(0)

  @staticmethod
  def serialize_time(time: datetime) -> str:
    """Converts a datetime object into ISO formatted time string."""
    return time.isoformat(sep=" ", timespec="seconds")

  @staticmethod
  def deserialize_time(time: str) -> datetime:
    """Converts an ISO formatted time string into a datetime object."""
    return datetime.fromisoformat(time)

  @staticmethod
  def to_local_time(time: datetime, offset: timedelta) -> datetime:
    """Converts a UTC datetime object to local time."""
    offset = offset or TimeStamp.timezone_offset()
    return time + offset
