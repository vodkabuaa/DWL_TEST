
import numpy as np
from tree import TreeModel
from bau import DLWBusinessAsUsual
from cost import DLWCost
from damage import DLWDamage
from utility import EZUtility
from analysis import RiskDecomposition, ClimateOutput, ConstraintAnalysis
from tools import *
from optimization import  GeneticAlgorithm, GradientSearch

m = np.array([  4.95862950e-01,3.75171168e-01,2.82054879e-01,4.92800734e-01
,8.02777260e-01,7.18381188e-01,1.42867164e+00,6.52239326e-01
,1.87274993e-01,5.11068788e-01,1.57327373e-01,2.20423405e-01
,1.22917879e+00,1.01964929e+00,1.40567374e+00,4.07183232e-01
,8.50937458e-01,6.79718330e-01,3.23332193e-01,1.00000000e-05
,1.01807396e+00,2.96735560e-01,3.08202234e-01,4.32025988e-01
,1.33593243e+00,1.00000000e-05,1.36128214e+00,1.14149359e+00
,8.95794681e-01,1.09285819e+00,1.91786252e+00,9.21097518e-01
,1.07479006e+00,5.21714055e-01,2.53589544e-01,9.67027732e-01
,9.96698019e-01,1.00000000e-05,3.24869220e-01,6.42854845e-02
,4.62322432e-01,8.12764521e-01,6.87168705e-02,3.73700132e-01
,1.42998391e+00,1.09851262e+00,6.78039172e-01,1.00000000e-05
,1.40466046e+00,1.06682082e+00,1.10484752e+00,3.75286122e-01
,1.13283753e+00,8.17033075e-01,2.98964205e-02,1.00000000e-05
,5.27566442e-02,9.35442380e-01,9.78987100e-01,1.34563569e+00
,7.94440869e-01,1.98551043e-01,3.11913249e-01])

if __name__ == "__main__":
	header, indices, data = import_csv("DLW_research_runs", indices=2)
	for i in range(23, 24):
		name = indices[i][1]
		a, ra, eis, pref, temp, tail, growth, tech_chg, tech_scale, joinp, maxp, on, maps = data[i]
		print(name, ra, eis)
		if on == 1.0:
			on = True
		else:
			on = False
		maps = int(maps)
		t = TreeModel(decision_times=[0, 15, 45, 85, 185, 285, 385], prob_scale=1.0)
		bau_default_model = DLWBusinessAsUsual()
		bau_default_model.bau_emissions_setup(t)
		c = DLWCost(t, bau_default_model.emit_level[0], g=92.08, a=3.413, join_price=joinp, max_price=maxp,
					tech_const=tech_chg, tech_scale=tech_scale, cons_at_0=30460.0)

		df = DLWDamage(tree=t, bau=bau_default_model, cons_growth=growth, ghg_levels=[450, 650, 1000], subinterval_len=5)
		#df.damage_simulation(draws=4000000, peak_temp=temp, disaster_tail=tail, tip_on=on, 
		#					 temp_map=maps, temp_dist_params=None, maxh=100.0, cons_growth=growth)
		df.import_damages()

		u = EZUtility(tree=t, damage=df, cost=c, period_len=5.0, eis=eis, ra=ra, time_pref=pref)
"""
		if a <= 2.0:
			ga_model = GeneticAlgorithm(pop_amount=150, num_generations=75, cx_prob=0.8, mut_prob=0.5, 
								bound=1.5, num_feature=63, utility=u, print_progress=True)
			
			gs_model = GradientSearch(var_nums=63, utility=u, accuracy=1e-8, 
							  iterations=250, print_progress=True)
	
			final_pop, fitness, u_hist = ga_model.run()
			sort_pop = final_pop[np.argsort(fitness)][::-1]
			
			m_opt, u_opt = gs_model.run(initial_point_list=sort_pop, topk=1)
			rd = RiskDecomposition(u)
			rd.sensitivity_analysis(m_opt)
			rd.save_output(m_opt, prefix="(280, 0.10)_2_"+name)

			co = ClimateOutput(u)
			co.calculate_output(m_opt)
			co.save_output(m_opt, prefix="(280, 0.10)_2_"+name)

			

		# Constraint first period mitigation to 0. NEEDS TO BE FIZED FOR NEW STRUCTURE
		else:
			cfp_m = constraint_first_period(u, 0.0, t.num_decision_nodes)
			cfp_utility_t, cfp_cons_t, cfp_cost_t, cfp_ce_t = u.utility(m_opt, return_trees=True)
			save_output(cfp_m, u, cfp_utility_t, cfp_cons_t, cfp_cost_t, cfp_ce_t, prefix="CFP_"+name)
			delta_utility = save_sensitivity_analysis(cfp_m, u, cfp_utility_t, cfp_cons_t, cfp_cost_t, cfp_ce_t,
												    "CFP_"+name, return_delta_utility=True)
			delta_utility_x = delta_utility - cfp_utility_t[0]
			save_constraint_analysis(cfp_m, u, delta_utility_x, prefix="CFP_"+name)

m_arr = []
names = []
files = ["test_0.2_1.0_2Eps-Zin(10)_node_period_output", "test_0.2_1.0_2base_case_node_period_output",
"test_0.2_1.0_2Eps-Zin(5)_node_period_output"]
for f in files:
	name = f[14:]
	m = import_csv(f, header=True, indices=1)[2][:, 0]
	m_arr.append(m)
	names.append(name)


u = EZUtility(tree=t, damage=df, cost=c, period_len=5.0, eis=eis, ra=ra, time_pref=pref,
					  add_penalty_cost=True, max_penalty=0.2, penalty_scale=1.0)
cd = CoordinateDescent(u, 63, iterations=1)
cd.run(m_arr[7])
ghg_level = df.ghg_level(m_arr[7], 6)
write_columns_to_existing([ghg_level], "test_ghg_levels_penalty", header=[names[7]])

"""
