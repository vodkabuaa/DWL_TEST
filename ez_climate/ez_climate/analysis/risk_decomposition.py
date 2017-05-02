from __future__ import division, print_function
import numpy as np
from ez_climate.tools import write_columns_csv, append_to_existing
from ez_climate.storage_tree import BigStorageTree
import tools

class RiskDecomposition(object):

	def __init__(self, utility):
		self.utility = utility
		self.sdf_tree = BigStorageTree(utility.period_len, utility.decision_times)
		self.sdf_tree.set_value(0, np.array([1.0]))

		n = len(self.sdf_tree)
		self.discount_prices = np.zeros(n)
		self.expected_damages = np.zeros(n)
		self.risk_premiums = np.zeros(n)
		self.expected_sdf = np.zeros(n)
		self.cross_sdf_damages = np.zeros(n)
		self.discounted_expected_damages = np.zeros(n)
		self.net_discount_damages = np.zeros(n)
		self.cov_term = np.zeros(n)

		self.discount_prices[0] = 1.0

	def sensitivity_analysis(self, m):
		"""Calculate and save sensitivity analysis based on the optimal mitigation. For every sub-period, i.e. the 
		periods given by the utility calculations, the function calculates and saves:
			
			* discount prices
			* net expected damages
			* expected damages
			* risk premium
			* expected SDF
			* cross SDF & damages
			* discounted expected damages
			* cov term
			* scaled net expected damages
			* scaled risk premiums
		
		into the file  `prefix` + 'sensitivity_output' in the 'data' directory in the current working directory. 

		Furthermore, for every node the function calculates and saves:
		
			* SDF 
			* delta consumption
			* forward marginal utility  
			* up-node marginal utility
			* down-node marginal utility
		
		into the file `prefix` + 'tree' in the 'data' directory in the current working directory. If there is no 'data' 
		directory, one is created. 

		Parameters
		----------
		m : ndarray or list
			array of mitigation
		utility : `Utility` object
			object of utility class
		prefix : str, optional
			prefix to be added to file_name

		"""

		utility_tree, cons_tree, cost_tree, ce_tree = self.utility.utility(m, return_trees=True)
		cost_sum = 0

		self.delta_cons_tree, self.delta_cost_array, delta_utility = tools.delta_consumption(m, self.utility, cons_tree, cost_tree, 0.01)
		mu_0, mu_1, mu_2 = self.utility.marginal_utility(m, utility_tree, cons_tree, cost_tree, ce_tree)
		sub_len = self.sdf_tree.subinterval_len
		i = 1
		for period in self.sdf_tree.periods[1:]:
			node_period = self.sdf_tree.decision_interval(period)
			period_probs = self.utility.tree.get_probs_in_period(node_period)
			expected_damage = np.dot(self.delta_cons_tree[period], period_probs)
			self.expected_damages[i] = expected_damage
			
			if self.sdf_tree.is_information_period(period-self.sdf_tree.subinterval_len):
				total_probs = period_probs[::2] + period_probs[1::2]
				mu_temp = np.zeros(2*len(mu_1[period-sub_len]))
				mu_temp[::2] = mu_1[period-sub_len]
				mu_temp[1::2] = mu_2[period-sub_len]
				sdf = (np.repeat(total_probs, 2) / period_probs) * (mu_temp/np.repeat(mu_0[period-sub_len], 2))
				period_sdf = np.repeat(self.sdf_tree.tree[period-sub_len],2)*sdf 
			else:
				sdf = mu_1[period-sub_len]/mu_0[period-sub_len]
				period_sdf = self.sdf_tree[period-sub_len]*sdf 

			self.expected_sdf[i] = np.dot(period_sdf, period_probs)
			self.cross_sdf_damages[i] = np.dot(period_sdf, self.delta_cons_tree[period]*period_probs)
			self.cov_term[i] = self.cross_sdf_damages[i] - self.expected_sdf[i]*expected_damage

			self.discount_prices[i] = self.expected_sdf[i]
			self.sdf_tree.set_value(period, period_sdf)

			if i < len(self.delta_cost_array):
				self.net_discount_damages[i] = -(expected_damage + self.delta_cost_array[i, 1]) * self.expected_sdf[i] / self.delta_cons_tree[0]
				cost_sum += -self.delta_cost_array[i, 1] * self.expected_sdf[i] / self.delta_cons_tree[0]
			else:
				self.net_discount_damages[i] = -expected_damage * self.expected_sdf[i] / self.delta_cons_tree[0]

			self.risk_premiums[i] = -self.cov_term[i]/self.delta_cons_tree[0]
			self.discounted_expected_damages[i] = -expected_damage * self.expected_sdf[i] / self.delta_cons_tree[0]
			i += 1

	def save_output(self, m, prefix=None):
		
		end_price = tools.find_term_structure(m, self.utility, 0.01)
		perp_yield = tools.perpetuity_yield(end_price, self.sdf_tree.periods[-2])

		damage_scale = self.utility.cost.price(0, m[0], 0) / (self.net_discount_damages.sum()+self.risk_premiums.sum())
		scaled_discounted_ed = self.net_discount_damages * damage_scale
		scaled_risk_premiums = self.risk_premiums * damage_scale

		if prefix is not None:
			prefix += "_" 
		else:
			prefix = ""

		write_columns_csv([self.discount_prices, self.net_discount_damages, self.expected_damages, self.risk_premiums, 
			               self.expected_sdf, self.cross_sdf_damages, self.discounted_expected_damages, self.cov_term, 
			               scaled_discounted_ed, scaled_risk_premiums], prefix + "sensitivity_output",
						   ["Year", "Discount Prices", "Net Expected Damages", "Expected Damages", "Risk Premium",
						    "Expected SDF", "Cross SDF & Damages", "Discounted Expected Damages", "Cov Term", "Scaled Net Expected Damages",
						    "Scaled Risk Premiums"], [self.sdf_tree.periods.astype(int)+2015]) 

		append_to_existing([[end_price], [perp_yield], [scaled_discounted_ed.sum()], [scaled_risk_premiums.sum()], 
			                [self.utility.cost.price(0, m[0], 0)]], prefix+"sensitivity_output",
			                header=["Zero Bound Price", "Perp Yield", "Expected Damages", "Risk Premium", 
							"SCC"], start_char='\n')
		
		tools.store_trees(prefix=prefix, SDF=self.sdf_tree, DeltaConsumption=self.delta_cons_tree)

		