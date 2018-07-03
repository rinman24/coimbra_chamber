import sys

import pandas as pd
import pathlib

from chamber.models import params
from chamber.models import props


def range_analysis():
    print('Starting analysis...')
    df = pd.DataFrame()
    for p in range(int(3e4), int(1.01325e5), int(1e4)):
        # Uses the model limit as the upper bound of the loop range
        for t in range(275, int(310*pow(p/101325, 0.09)), 5):
            for t_s in (t_int/2 for t_int in range(2 * t, 2 * t + 5)):
                for rh in (rh_int/100 for rh_int in range(5, 90, 5)):
                    t_dp = props.get_tdp(p, t, rh)
                    grashof = params.get_grashof(p, t, t_dp, t_s)
                    df = df.append({
                        'Pressure (Pa)': p, 'Environment Temp (K)': t,
                        'Surface Temp (K)': t_s, 'Dew Point (K)': t_dp,
                        'Ralative Humidity': rh, 'Grashof': grashof
                        }, ignore_index=True)
    print('Anslysis complete')
    return df


def df_to_csv(df, file_path):
    print('Saving results tp {}...'.format(file_path))
    df[['Pressure (Pa)', 'Environment Temp (K)', 'Surface Temp (K)',
        'Dew Point (K)', 'Ralative Humidity', 'Grashof']].to_csv(file_path)
    print('Results saved.')


def grashof_comparison():
    print('Setting up analysis...')
    file_path = pathlib.Path('.') / 'chamber' / 'scripts' / 'grashof_comparison.csv'
    print('Set up complete.')

    df = range_analysis()
    df_to_csv(df, file_path)


grashof_comparison()
