import pytest
from coverage import Coverage    # type: ignore

if __name__ == "__main__":
  cov = Coverage()
  cov.start()
  pytest.main()
  cov.stop()
  cov.save()
  cov.html_report(directory='.htmlcov', omit=["*/tests*"])    # type: ignore
