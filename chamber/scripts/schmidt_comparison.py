import sys

import pandas as pd
import pathlib

from chamber.models import props
from chamber.models import params

print('Setting up analysis')
RES_FILEPATH = pathlib.Path('.') / 'chamber' / 'scripts' / 'schmidt_comparison.csv'
DF = pd.DataFrame()

print('Starting analysis')
for p in range(int(3e4), int(1.01325e5), int(1e4)):
    # Uses the model limit as the upper bound of the loop range
    for t in range(275, int(310*pow(p/101325, 0.09)), 5):
        for rh in (rh_int/100 for rh_int in range(5, 90, 5)):
            t_dp = props.get_tdp(p, t, rh)
            schmidt_mills = params.get_schmidt(p, t, t_dp, 'Mills')
            schmidt_marrero = params.get_schmidt(p, t, t_dp, 'Marrero')
            DF = DF.append({
                'Pressure (Pa)': p, 'Temperature (K)': t,
                'Dew Point (K)': t_dp, 'Ralative Humidity': rh,
                'Schmidt Mills': schmidt_mills,
                'Schmidt Marrero': schmidt_marrero
                }, ignore_index=True)
print('Anslysis complete')

print('Saving Results')
DF[['Pressure (Pa)', 'Temperature (K)', 'Dew Point (K)','Ralative Humidity',
    'Schmidt Mills', 'Schmidt Marrero']].to_csv(RES_FILEPATH)
print('Results saved')

print('Success')
