from datetime import datetime, timedelta
import pytest

from message.timestamp import TimeStamp


class TestTimeStamp:

  @pytest.fixture
  def current_time(self) -> datetime:
    return datetime.now()

  def test_timezone_name(self):
    assert TimeStamp.timezone_name() == datetime.now().astimezone().tzname()

  def test_timezone_offset(self):
    assert TimeStamp.timezone_offset() == datetime.now().astimezone().utcoffset(
    ) or timedelta(0)

  def test_serialize_time(self, current_time: datetime):
    expected_time = f"{current_time:%Y-%m-%d %H:%M:%S}"
    assert TimeStamp.serialize_time(current_time) == expected_time
    assert f"{TimeStamp.deserialize_time(expected_time)}" == expected_time

  def test_to_local_time(self, current_time: datetime):
    offset = datetime.now().astimezone().utcoffset()
    if offset:
      expected_time = current_time + offset
      assert TimeStamp.to_local_time(current_time, offset) == expected_time


if __name__ == "__main__":
  pytest.main([__file__])
