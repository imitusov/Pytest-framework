import datetime
from typing import List, Tuple
import pytest

def split_into_smaller_intervals(
        start_date: str, end_date: str, days_per_interval: int = 30
        ) -> List[Tuple[datetime.date, datetime.date]]:
    """
    Split time interval into a list of non-overlapping adjacent
    smaller intervals.
    This can be beneficial for decreasing memory consumption at
    ClickHouse.

    :param start_date:
        start date (inclusively) of initial interval in a 'YYYY-MM-DD'
        format
    :param end_date:
        end date (inclusively) of initial interval in a 'YYYY-MM-DD'
        format
    :param days_per_interval:
        maximum number of days per any of final intervals, the last
        interval can contain less days
    :return:
        list of intervals represented by their inclusive ends
    """
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    size_in_days = (end_date - start_date).days
    size_in_intervals = size_in_days // days_per_interval + 1
    smaller_intervals = [
        (
            start_date + datetime.timedelta(days=i * days_per_interval),
            start_date + datetime.timedelta(days=(i+1) * days_per_interval - 1)
        )
        for i in range(size_in_intervals)
    ]
    last_date = min(smaller_intervals[-1][1], end_date)
    smaller_intervals[-1] = (smaller_intervals[-1][0], last_date)
    return smaller_intervals

@pytest.fixture(scope='module')
def create_intervals():
    def _create_intervals(start, end):
        return split_into_smaller_intervals(start, end)
        
    return _create_intervals

@pytest.fixture(scope='module', 
                params=[99, 101])
def same_interval_category(request):
    splitted = split_into_smaller_intervals('2017-08-29', '2018-08-29', request.param)
    yield splitted