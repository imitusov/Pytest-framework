import datetime
import pytest
import sys
from typing import List, Tuple

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

@pytest.fixture(scope='class')
def intervals():
    ''' 
    fix one year s for a split_into_smaller_intervals function 
    '''    
    return split_into_smaller_intervals('2017-08-29', '2018-08-29')

@pytest.fixture(scope='class')
def intervals_two():
    '''
    fix one week for a split_into_smaller_intervals function 
    '''
    return split_into_smaller_intervals('2018-08-23', '2018-08-29', 3)

@pytest.fixture(scope='class')
def intervals_three():
    '''
    Same period as intervals_two but with 4 days per interval 
    '''
    return split_into_smaller_intervals('2018-08-23', '2018-08-29', 4)

@pytest.mark.skipif(sys.platform == 'darwin',
                    reason='does not run on MacOS')

class TestClass:
    def test_start_date_and_end_date_are_correct(self):
        '''
        Testing whether both start and end dates are correct
        '''
        assert intervals()[0][0] == datetime.datetime.strptime(
            '2017-08-29', "%Y-%m-%d").date(),'Wrong start date'
        assert intervals()[-1][1] == datetime.datetime.strptime(
            '2018-08-29', "%Y-%m-%d").date(),'Wrong end date'

    def test_return_is_list(self):
        '''
        Testing whether functions return is in list format
        '''
        assert type(intervals()) == list, 'list format is expected'
        
    def test_list_components_are_tuples(self):
        '''
        Testing whether all lists' components are tuples
        '''
        assert all(isinstance(x, tuple) for x in intervals())
        
    def test_tuples_components_are_datetime_date_format(self):
        '''
        Testing whether all components in tuples are datetime.date format
        '''
        assert all(True in (isinstance(dat, datetime.date) 
        for dat in tup) for tup in intervals())
        
    def test_first_date_of_interval_is_earlier(self):
        '''
        Testing whether first date of an interval is earlier than second
        '''
        assert all((tup[0] <= tup[1]) for tup in intervals()) 

    def test_previous_equal_next(self):
        '''
        Testing first date of a period is equal to a last date + 1 
        of a previous period
        '''
        last_date = [x[1] for x in intervals()[:-1]]
        first_date = [x[0] for x in intervals()[1:]]
        assert [x + datetime.timedelta(1) for x in last_date] == first_date

    def test_tuple_len(self):
        '''
        Testing that tuples have exactly 2 elements
        '''
        assert all((len(tup) == 2) for tup in intervals())
        
    def test_datetime_yyyy_is_digit(self):
        '''
        Testing YYYY in YYYY-MM-DD is digit  
        '''
        assert True in (True in (f'{year:%Y-%m-%d}'[0:4].isdigit() 
            for year in tup) for tup in intervals())
        
    def test_datetime_mm_is_digit(self):
        '''
        Testing MM in YYYY-MM-DD is digit  
        '''
        assert True in (True in (f'{month:%Y-%m-%d}'[5:7].isdigit() 
            for month in tup) for tup in intervals())

    def test_datetime_dd_is_digit(self):
        '''
        Testing DD in YYYY-MM-DD is digit  
        '''
        assert True in (True in (f'{day:%Y-%m-%d}'[8:10].isdigit() 
            for day in tup) for tup in intervals())

    def test_calcs_are_correct(self):
        '''
        Check correctness of calculations  
        '''
        assert intervals_two() == [(datetime.date(2018, 8, 23),
                                    datetime.date(2018, 8, 25)),
                                    (datetime.date(2018, 8, 26),
                                    datetime.date(2018, 8, 28)),
                                    (datetime.date(2018, 8, 29), 
                                    datetime.date(2018, 8, 29))]

    def test_last_period_can_be_smaller(self):
        '''
        Checking last period length can be smaller than others
        '''
        assert intervals_two()[-1] == (datetime.date(2018, 8, 29),
                                       datetime.date(2018, 8, 29))

    def test_sets_for_dif_int_len(self):
        '''
        Different inteval lenght provide different sets of outputs
        '''     
        assert set(intervals_two()) != set(intervals_three())
    
    def test_stable_calulcation(self, create_intervals):
        '''
        Calculation are stable: same result for the same input
        '''
        int_one = create_intervals('2017-08-29', '2018-08-29')
        int_two = create_intervals('2017-08-29', '2018-08-29')
        assert int_one == int_two
    
    def test_same_output_length(self, same_interval_category):
        '''
        Same output length
        '''
        assert len(same_interval_category) == 4
    
    @pytest.mark.parametrize(
        ('start', 'end', 'expected'),
        [
            ('2018-08-23',
            '2018-08-29',
            [(datetime.date(2018, 8, 23), datetime.date(2018, 8, 29))]),
            ('2018-07-23',
            '2018-08-29',
            [(datetime.date(2018, 7, 23), datetime.date(2018, 8, 21)),
            (datetime.date(2018, 8, 22), datetime.date(2018, 8, 29))]),
            pytest.param(
                '2018-08-23',
                '2018-08-29',
                [(datetime.date(2018, 7, 23), datetime.date(2018, 8, 21)),
                (datetime.date(2018, 8, 22), datetime.date(2018, 8, 29))], 
                marks=pytest.mark.xfail(reason='incorrect input')
            )
        ]
    )
    def test_params_function(self, create_intervals, start, end, expected):
        '''
        pytest.mark.parametrize check
        '''
        assert create_intervals(start, end) == expected
    
TestClass()