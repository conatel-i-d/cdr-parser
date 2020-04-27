import pandas as pd

from .cdr_panda_base import CDRPandaBase
from .constants import STANDARD_RECORD_TYPE

class CDRPanda(CDRPandaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def queue_calls_behaviour(self, 
        queue_number=None,
        pre_attendant_number=None,
        originating_number_regex=None,
        calls_summary_file_path=None,
        freq='6h'
    ):
        if queue_number is None or pre_attendant_number is None or originating_number_regex is None:
            print('Invalid parameters')
            return
        if self.record_type != STANDARD_RECORD_TYPE:
            print(f'Only valid for {STANDARD_RECORD_TYPE} records')
            return
        print('Creating the queue calls DataFrame...')
        queue_df = self.df.loc[
            (self.df['terminating_number'] == queue_number) &
            (self.df['originating_number'] != pre_attendant_number) &
            (self.df['originating_number'].str.contains(originating_number_regex, regex=True) == False)
        ].copy().groupby([pd.Grouper(key='start_time', freq=freq, base=3), 'originating_number'])['duration_of_call'].sum()
        print('Creating the calls_lost Series...')
        calls_lost = queue_df[queue_df == 0].copy().groupby(level='start_time').count()
        calls_lost.rename('calls_lost')
        print('Creating the calls_attended Series...')
        calls_attended = queue_df[queue_df > 0].copy().groupby(level='start_time').count()
        calls_attended.rename('calls_attended')
        print('Creating the calls_summary DataFrame...')
        calls_summary = pd.DataFrame(dict(calls_lost=calls_lost, calls_attended=calls_attended))
        calls_summary['calls_lost'].fillna(0, inplace=True)
        calls_summary['calls_attended'].fillna(0, inplace=True)
        calls_summary.to_csv(calls_summary_file_path, header=True)

