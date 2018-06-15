import pandas as pd

from chamber.models import params
from chamber.models import props

results = {'Pressure (Pa)': [], 'Temperature (K)': [], 'Ralative Humidity': [],
           'Dew Point (K)': [], 'Grashof': []}

if __name__=="__main__":
	for p in range(3e4, 1.01325e5, 1e4):
		# Uses the model limit as the upper bound of the loop range
		for t in range(275, int(310*pow(p/101325, 0.09)), 5):
			for rh in (rh_int/100 for rh_int in range(5, 90, 5)):
				t_dp = props.get_tdp(p, t, rh)
				grashof = params.get_grashof(p, t, t_dp)
				results['Pressure (Pa)'].append(p)
				results['Temperature (K)'].append(t)
				results['Ralative Humidity'].append(rh)
				results['Dew Point (K)'].append(rh)
				results['Grashof'].append(grashof)

	df = pd.DataFrame.from_dict(results)
	df[['Pressure (Pa)', 'Temperature (K)', 'Ralative Humidity',
		'Grashof']].to_csv('schmidt_comparison.csv', sep=',')
