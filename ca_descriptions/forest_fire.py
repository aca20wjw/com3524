# Name: forest_fire
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
import numpy as np
import copy
import random as rnd
this_file_loc = (inspect.stack ()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, randomise2d
import capyle.utils as utils

dimensions = (20,20)
fuel_cap = 100



def setup(args):
    """Set up the config object used to interact with the GUI"""
    config_path = args[0]
    config = utils.load(config_path)
    # -- THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED --
    config.title = "forest_fire"
    config.dimensions = 2
    config.states = (0,1,2)
    # -------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    config.state_colors = [(0,0,0),(1,1,1),(0.5,0.5,0.5)]
    config.grid_dims = dimensions
    # ----------------------------------------------------------------------

    # the GUI calls this to pass the user defined config
    # into the main system with an extra argument
    # do not change
    if len(args) == 2:
        config.save()
        sys.exit()
    return config

# def get_cell_colour(self):


def transition_function(grid, neighbourstates, neighbourcounts, type_grid, veg_lvl_grid):
    not_burning_n, burning_n, burnt_n = neighbourcounts

    grid_cpy = copy.deepcopy(grid)
    # update vegetation level after burning, search for cells that are either burnt or burning and handle
    # accordingly
    burning_cells = (grid_cpy == 1)
    burnt_cells = (grid_cpy == 2)

    # decrease to represent fuel depletion, increase to represent regrowth

    veg_lvl_grid[burning_cells & (type_grid == 1)] -= 5
    veg_lvl_grid[burning_cells & (type_grid == 2)] -= 1
    veg_lvl_grid[burning_cells & (type_grid == 3)] -= 3

    veg_lvl_grid[burnt_cells] += 0.1
    
    # alternative implementation below -- each cell type grows at different rate 

    # veg_lvl_grid[burnt_cells & (type_grid == 1)] += 1
    # veg_lvl_grid[burnt_cells & (type_grid == 2)] += 1
    # veg_lvl_grid[burnt_cells & (type_grid == 3)] += 1


    # probabilistic model
    # probability of cell being set on fire depends on no. of neighbouring cells on fire and type of cell
    # need to modify the probabilities here to something sensible

    # probabilities for each type of vegetation being set on fire
    p_t1 = 0.9
    p_t2 = 0.9
    p_t3 = 0.9

    # get all cells that are in risk of catching fire (all cells with at least one neighbour on fire, not a 
    # lake and is not already burning)
    fire_risk_cells = (burning_n > 1) & (grid == 0) & (type_grid != 0)
    
    type_1 = (type_grid == 1)
    type_2 = (type_grid == 2)
    type_3 = (type_grid == 3)


    t1_fire_risk = fire_risk_cells & type_1
    t2_fire_risk = fire_risk_cells & type_2
    t3_fire_risk = fire_risk_cells & type_3

    rnd_array = np.random.rand(20,20)

    t1_fire = rnd_array < p_t1
    t2_fire = rnd_array < p_t2
    t3_fire = rnd_array < p_t3

    set_fire = (t1_fire & t1_fire_risk) & (t2_fire & t2_fire_risk) & (t3_fire & t3_fire_risk)
    set_burnt = (veg_lvl_grid == 0) & (grid_cpy != 2)
   
    
    # if cell already on fire and fuel level still above 0, keep cells on fire
    keep_fire = ((veg_lvl_grid > 0) & (grid_cpy == 1))
    # if cell is in burnt state and has not yet recovered fully, keep burnt
    keep_burnt = ((veg_lvl_grid < fuel_cap) & (grid_cpy == 2))

    # set final values for grid
    grid_cpy[:, :] = 0
    grid_cpy[set_fire | keep_fire] = 1
    grid_cpy[keep_burnt] = 2

    # cells 
    grid_cpy[set_burnt] = 2
    # cells that have fuel value n (regrowth complete) turn into state 0 (not burning/flammable)
    grid_cpy[veg_lvl_grid == fuel_cap] = 0

    # grid_cpy[:,:] = 0
    # grid_cpy[type_1] = 2
    # grid_cpy[type_2] = 1
    # grid_cpy[type_3] = 0
    return grid_cpy


def main():
    """ Main function that sets up, runs and saves CA"""
    # Get the config object from set up
    config = setup(sys.argv[1:])
    
    # Keeps track of type of vegetation in each cell (assuming 10000 x 10000) useful for specifying
    # behaviour depending 
    # 1 = chaparral, 2 = dense forest, 3 = canyon, 0 = lake
    type_grid = np.ones(config.grid_dims)

    type_grid[8:14, 0:10] = 2
    type_grid[2:7, 6:10] = 2
    type_grid[7, 3:10] = 0
    type_grid[3:16, 12] = 3

    # Keeps track of how long each cell stays on fire. Period of burning based on type of vegetation
    veg_lvl_grid = np.zeros((20,20))
    veg_lvl_grid.fill(fuel_cap)

    # veg_lvl_grid = copy.deepcopy(type_grid)
    # veg_lvl_grid[veg_lvl_grid == 1] = 10
    # veg_lvl_grid[veg_lvl_grid == 2] = 20
    # veg_lvl_grid[veg_lvl_grid == 3] = 5
    


    # Create grid object using parameters from config + transition function
    grid = Grid2D(config, (transition_function, type_grid, veg_lvl_grid))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
