from cases.NorthSea_helpers.read_input_data import *
import numpy as np

from src.model_configuration import ModelConfiguration
from src.energyhub import EnergyHub
from cases.NorthSea_helpers.utilities import *

# General Settings
settings = SimpleNamespace()
settings.year = 2030
settings.scenario = 'GA'
settings.climate_year = 2009
settings.start_date = '01-01 00:00'
settings.end_date = '02-01 23:00'
settings.data_path = r'./cases/NorthSea_v3'
# settings.save_path = '//ad.geo.uu.nl/Users/StaffUsers/6574114/EhubResults/MES NorthSea/20230609/MES_NS_Baseline'
settings.save_path = './user_data/test'

# Network Settings
settings.networks = SimpleNamespace()
settings.networks.existing_electricity = 1
settings.networks.new_electricityAC = 0
settings.networks.new_electricityDC = 0
settings.networks.new_hydrogen = 0

# Node aggregation
settings.node_aggregation_type = {
    'onshore': ['onNL_C', 'onOther', 'onNL_NE', 'onNL_SW', 'onNL_NW'],
    'offshore': []}
settings.node_aggregation = {
    'onNL_C': ['onNL_SE', 'onNL_CE', 'onNL_E'],
    'onNL_NE': ['onNL_NE', 'ofNL_GE_A', 'ofNL_GE_B'],
    'onNL_SW': ['onNL_SW', 'ofNL_BO_A', 'ofNL_BO_B'],
    'onNL_NW': ['onNL_NW', 'ofNL_LU', 'ofNL_PA'],
    'onOther': ['onBE', 'onDE', 'onDKW', 'onNOS']}

# Configuration
configuration = ModelConfiguration()
configuration.solveroptions.solver = 'gurobi_persistent'
configuration.solveroptions.mipgap = 0.01
configuration.solveroptions.lpwarmstart = 1
configuration.solveroptions.numericfocus = 3
configuration.optimization.save_log_files = 1
configuration.optimization.monte_carlo.on = 0
configuration.optimization.monte_carlo.N = 5
configuration.optimization.typicaldays = 0

# Set Data
nodes = read_nodes(settings)
topology = define_topology(settings, nodes)
topology = define_installed_capacities(settings, nodes, topology)
topology = define_networks(settings, topology)
topology = define_new_technologies(settings, nodes, topology)

data = define_data_handle(topology, nodes)
data = define_generic_production(settings, nodes, data)
data = define_hydro_inflow(settings, nodes, data)
data = define_demand(settings, nodes, data)
data = define_imports(settings, nodes, data)

# Read data
tec_data_path = settings.data_path + '/Technology_Data/'
write_to_technology_data(tec_data_path, settings.year)
data.read_technology_data(path =tec_data_path)
data.read_network_data()
data = define_charging_efficiencies(settings, nodes, data)


# Have different emission limits
emissions = []

# Read data
configuration.optimization.objective = 'costs'
energyhub = EnergyHub(data, configuration)
results = energyhub.quick_solve()

emissions.append(energyhub.model.var_emissions_net.value)


# CONFIGURATION EMISSIONS
energyhub.configuration.optimization.objective = 'emissions_minC'

energyhub.solve()

emissions.append(energyhub.model.var_emissions_net.value)

results.write_excel(settings.save_path)
