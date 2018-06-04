import sys
sys.path.insert(0,'../chamber/models')

from CoolProp import HumidAirProp as hap
import pandas as pd

import props


results = {'Pressure (Pa)': [], 'Temperature (K)': [],
					'Ralative Humidity': [], 'Schmidt Mills': [],
					'Schmidt Marrero': []}


# Gets relevant values and calculates Schmidt number
def get_schmidt(p, t, rh):
	mills = props.get_d_12(p, t, 'Mills')
	marrero = props.get_d_12(p, t, 'Marrero')

	# Sometimes errors arise with coolprop from high relative humidities
	try:
		rho = 1/hap.HAPropsSI('Vha', 'P', p, 'T', t, 'RH', rh)
	except ValueError:
		return False, False

	mu = props.get_mu(p, t, rh)
	schmidt_mills = mu/(rho*mills)
	schmidt_marrero = mu/(rho*marrero)

	return schmidt_mills, schmidt_marrero


if __name__=="__main__":
	for press in range(30000,100001,10000):
		# Uses a line approximating the model limit curve to limit the upper range
		for temp in range(275, int(press*0.0005+261), 5):
			for rh in range(10, 81, 10):
				schmidt_mills, schmidt_marrero = get_schmidt(press, temp, rh)
				if schmidt_mills and schmidt_marrero:
					results['Pressure (Pa)'].append(press)
					results['Temperature (K)'].append(temp)
					results['Ralative Humidity'].append(rh)
					results['Schmidt Mills'].append(schmidt_mills)
					results['Schmidt Marrero'].append(schmidt_marrero)

	df = pd.DataFrame.from_dict(results)
	df[['Pressure (Pa)', 'Temperature (K)', 'Ralative Humidity', 'Schmidt Mills',
	    'Schmidt Marrero']].to_csv('schmidt_comparison.csv', sep=',')
