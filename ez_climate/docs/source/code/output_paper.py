from ez_climate.tree import TreeModel

t = TreeModel(decision_times=[0, 15, 45, 85, 185, 285, 385])

from ez_climate.bau import DLWBusinessAsUsual

bau_default_model = DLWBusinessAsUsual()
bau_default_model.bau_emissions_setup(tree=t)

from ez_climate.cost import DLWCost

c = DLWCost(tree=t, emit_at_0=bau_default_model.emit_level[0], g=92.08, a=3.413, join_price=2000.0,
            max_price=2500.0, tech_const=1.5, tech_scale=0.0, cons_at_0=30460.0)

from ez_climate.damage import DLWDamage

df = DLWDamage(tree=t, bau=bau_default_model, cons_growth=0.015, ghg_levels=[450, 650, 1000], subinterval_len=5)
df.damage_simulation(draws=4000000, peak_temp=6.0, disaster_tail=18.0, tip_on=True, 
                     temp_map=1, temp_dist_params=None, maxh=100.0, cons_growth=0.015)

from ez_climate.utility import EZUtility

u = EZUtility(tree=t, damage=df, cost=c, period_len=5.0, eis=1.11, ra=0.9, time_pref=0.005)


from ez_climate.optimization import GeneticAlgorithm, GradientSearch

ga_model = GeneticAlgorithm(pop_amount=150, num_generations=150, cx_prob=0.8, mut_prob=0.5, 
                            bound=2.0, num_feature=63, utility=u, print_progress=True)
gs_model = GradientSearch(learning_rate=0.001, var_nums=63, utility=u, accuracy=1e-8, 
                          iterations=200, print_progress=True)

final_pop, fitness = ga_model.run()
sort_pop = final_pop[np.argsort(fitness)][::-1]
m_opt, u_opt = gs_model.run(initial_point_list=sort_pop, topk=1)

print("SCC: ", c.price(0, m[0], 0))



def base_case():
	from ez_climate.tree import TreeModel
	from ez_climate.bau import DLWBusinessAsUsual
	from ez_climate.cost import DLWCost
	from ez_climate.damage import DLWDamage
	from ez_climate.utility import EZUtility
	from ez_climate.optimization import GeneticAlgorithm, GradientSearch

	t = TreeModel(decision_times=[0, 15, 45, 85, 185, 285, 385])

	bau_default_model = DLWBusinessAsUsual()
	bau_default_model.bau_emissions_setup(tree=t)

	c = DLWCost(tree=t, emit_at_0=bau_default_model.emit_level[0], g=92.08, a=3.413, join_price=2000.0,
                max_price=2500.0, tech_const=1.5, tech_scale=0.0, cons_at_0=30460.0)

	df = DLWDamage(tree=t, bau=bau_default_model, cons_growth=0.015, ghg_levels=[450, 650, 1000], subinterval_len=5)
	df.damage_simulation(draws=4000000, peak_temp=6.0, disaster_tail=18.0, tip_on=True, 
	                     temp_map=1, temp_dist_params=None, maxh=100.0, cons_growth=0.015)

	u = EZUtility(tree=t, damage=df, cost=c, period_len=5.0, eis=1.11, ra=0.9, time_pref=0.005)

	ga_model = GeneticAlgorithm(pop_amount=150, num_generations=150, cx_prob=0.8, mut_prob=0.5, 
	                            bound=2.0, num_feature=63, utility=u, print_progress=True)
	gs_model = GradientSearch(learning_rate=0.001, var_nums=63, utility=u, accuracy=1e-8, 
	                          iterations=200, print_progress=True)

	final_pop, fitness = ga_model.run()
	sort_pop = final_pop[np.argsort(fitness)][::-1]
	m_opt, u_opt = gs_model.run(initial_point_list=sort_pop, topk=1)

	print("SCC: ", c.price(0, m[0], 0))

if __name__ == "__main__":
	base_case()