import pandas as pd

from chamber.models import params
from chamber.models import props

results = {'Pressure (Pa)': [], 'Temperature (K)': [], 'Ralative Humidity': [],
           'Dew Point (K)': [], 'Schmidt Mills': [], 'Schmidt Marrero': []}

if __name__=="__main__":
	for p in range(3e4, 1.01325e5, 1e4):
		# Uses the model limit as the upper bound of the loop range
		for t in range(275, int(310*pow(p/101325, 0.09)), 5):
			for rh in (rh_int/100 for rh_int in range(5, 90, 5)):
				# relative humidity should be a fraction between 0 and 1
				t_dp = props.get_tdp(p, t, rh)
				schmidt_mills = params.get_schmidt(p, t, t_dp, 'Mills')
				schmidt_marrero = params.get_schmidt(p, t, t_dp, 'Marrero')
				results['Pressure (Pa)'].append(p)
				results['Temperature (K)'].append(t)
				results['Ralative Humidity'].append(rh)
				results['Dew Point (K)'].append(rh)
				results['Schmidt Mills'].append(schmidt_mills)
				results['Schmidt Marrero'].append(schmidt_marrero)

	df = pd.DataFrame.from_dict(results)
	df[['Pressure (Pa)', 'Temperature (K)', 'Ralative Humidity', 'Schmidt Mills',
	    'Schmidt Marrero']].to_csv('schmidt_comparison.csv', sep=',')
