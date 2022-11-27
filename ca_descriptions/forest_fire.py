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

f = open("fire_neighbour_map.txt", 'w')
f2 = open("grid_map.txt", 'w')
f3 = open("neighbour_map.txt", 'w')
f4 = open("state_map.txt", 'w')
f5 = open("t1_fire_risk.txt", 'w')
edg = open("edge_case_map.txt", 'w')
test = open("test_file.txt", 'w')
f_log = open("log.txt", 'w')

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

# def get_cell_colour(selwf):
def transition_func(grid, neighbourstates, neighbourcounts, type_grid, veg_lvl_grid):
    # dead = state == 0, live = state == 1
    # unpack state counts for state 0 and state 1
    not_burning_n, burning_n, burnt_n = neighbourcounts
    # create boolean arrays for the birth & survival rules
    # if 3 live neighbours and is dead -> cell born
    grid_cpy = grid
    birth = (burning_n >= 1) & (grid_cpy == 0)
    for line in burning_n:
        for i in line:
            if i > 0:
                f3.write(f"{str(i)[0]} ")
            else:
                f3.write("⬚ ")
        f3.write("\n")
    f3.write("\n\n\n\n")

    for i in grid_cpy:
        for j in i:
            if j == False:
                f2.write(f"⬚ ")
            else:
                f2.write("■ ")
        f2.write("\n")
    f2.write("\n\n\n\n")

    # if 2 or 3 live neighbours and is alive -> survives
    survive = (grid_cpy == 1)
    # Set all cells to 0 (dead)
    grid_cpy[:, :] = 0
    # Set cells to 1 where either cell is born or survives
    grid_cpy[birth | survive] = 1

    return grid

def transition_function(grid, neighbourstates, neighbourcounts, type_grid, veg_lvl_grid, edge_case_grid):
    not_burning_n, burning_n, burnt_n = neighbourcounts
    NW, N, NE, W, E, SW, S, SE = neighbourstates

    # calculate neighbours for all edge cases that should not be included in the final count

    # edge cases for left side
    nw_left_edge = ((edge_case_grid == 2) & (NW == 1)).astype(int)
    w_left_edge = (edge_case_grid == 2) & (W == 1).astype(int)
    sw_left_edge = (edge_case_grid == 2) & (SW == 1).astype(int)

    left_edge_n = nw_left_edge + w_left_edge + sw_left_edge

    # top edge cases
    n_top_edge = ((edge_case_grid == 1) & (N == 1)).astype(int)
    nw_top_edge = (edge_case_grid == 1) & (NW == 1).astype(int)
    ne_top_edge = (edge_case_grid == 1) & (NE == 1).astype(int)

    top_edge_n = n_top_edge + nw_top_edge + ne_top_edge

    # edge cases for right side
    ne_right_edge = ((edge_case_grid == 3) & (NE == 1)).astype(int)
    e_right_edge = (edge_case_grid == 3) & (E == 1).astype(int)
    se_right_edge = (edge_case_grid == 3) & (SE == 1).astype(int)

    right_edge_n = ne_right_edge + e_right_edge + se_right_edge

    # edge cases for bottom side
    se_bottom_edge = ((edge_case_grid == 4) & (SE == 1)).astype(int)
    s_bottom_edge = (edge_case_grid == 4) & (S == 1).astype(int)
    sw_bottom_edge = (edge_case_grid == 4) & (SW == 1).astype(int)

    bottom_edge_n = se_bottom_edge + s_bottom_edge + sw_bottom_edge

    # Coner edge cases --
    # upper left corner edge cases
    ne_u_left_corner = ((edge_case_grid == 5) & (NE == 1)).astype(int)
    n_u_left_corner = ((edge_case_grid == 5) & (N == 1)).astype(int)
    nw_u_left_corner = ((edge_case_grid == 5) & (NW == 1)).astype(int)
    w_u_left_corner = ((edge_case_grid == 5) & (W == 1)).astype(int)
    sw_u_left_corner = ((edge_case_grid == 5) & (SW == 1)).astype(int)

    u_left_corner_n = ne_u_left_corner + n_u_left_corner + nw_u_left_corner + w_u_left_corner + sw_u_left_corner

    # upper right corner edge cases
    ne_u_left_corner = ((edge_case_grid == 6) & (NE == 1)).astype(int)
    n_u_left_corner = ((edge_case_grid == 6) & (N == 1)).astype(int)
    nw_u_left_corner = ((edge_case_grid == 6) & (NW == 1)).astype(int)
    e_u_left_corner = ((edge_case_grid == 6) & (E == 1)).astype(int)
    se_u_left_corner = ((edge_case_grid == 6) & (SE == 1)).astype(int)

    u_right_corner_n = ne_u_left_corner + n_u_left_corner + nw_u_left_corner + e_u_left_corner + se_u_left_corner

    # lower right corner edge cases
    se_u_left_corner = ((edge_case_grid == 8) & (SE == 1)).astype(int)
    s_u_left_corner = ((edge_case_grid == 8) & (S == 1)).astype(int)
    sw_u_left_corner = ((edge_case_grid == 8) & (SW == 1)).astype(int)
    e_u_left_corner = ((edge_case_grid == 8) & (E == 1)).astype(int)
    ne_u_left_corner = ((edge_case_grid == 8) & (NE == 1)).astype(int)

    l_right_corner_n = se_u_left_corner + s_u_left_corner + sw_u_left_corner + e_u_left_corner + ne_u_left_corner

    # lower left corner edge cases
    se_u_left_corner = ((edge_case_grid == 7) & (SE == 1)).astype(int)
    s_u_left_corner = ((edge_case_grid == 7) & (S == 1)).astype(int)
    sw_u_left_corner = ((edge_case_grid == 7) & (SW == 1)).astype(int)
    w_u_left_corner = ((edge_case_grid == 7) & (W == 1)).astype(int)
    nw_u_left_corner = ((edge_case_grid == 7) & (NW == 1)).astype(int)

    l_left_corner_n = se_u_left_corner + s_u_left_corner + sw_u_left_corner + w_u_left_corner + nw_u_left_corner

    # get a grid for the edge case neighbour count and subtract from main neighbour count to get an adjusted
    # grid
    edge_case_n = left_edge_n + right_edge_n + top_edge_n + bottom_edge_n + u_left_corner_n + u_right_corner_n + l_left_corner_n + l_right_corner_n
    adjusted_burning_n = burning_n - edge_case_n

    for line in edge_case_n:
        for i in line:
            if i > 0:
                edg.write(f"{str(i)[0]} ")
            else:
                edg.write("⬚ ")
        edg.write("\n")
    edg.write("\n\n\n\n")

    for line in adjusted_burning_n:
        for i in line:
            if i > 0:
                test.write(f"{str(i)[0]} ")
            else:
                test.write("⬚ ")
        test.write("\n")
    test.write("\n\n\n\n")

    # if lake is in burning state, turn it back 
    grid[type_grid == 0] = 0

    # files for debugging
    for line in NW:
        for i in line:
            if i > 0:
                f4.write(f" {str(i)[0]} ")
            else:
                f4.write(" ⬚ ")
        f4.write("\n")
    f4.write("\n\n\n\n")
    
    for i in grid:
        for j in i:
            if j == False:
                f2.write(f"⬚ ")
            else:
                f2.write("■ ")
        f2.write("\n")
    f2.write("\n\n\n\n")
    
    for line in burning_n:
        for i in line:
            if i > 0:
                f3.write(f"{str(i)[0]} ")
            else:
                f3.write("⬚ ")
        f3.write("\n")
    f3.write("\n\n\n\n")

    # update vegetation level after burning, search for cells that are either burnt or burning and handle
    # accordinglyw
    burning_cells = (grid == 1)
    burnt_cells = (grid == 2)

    # decrease to represent fuel depletion, increase to represent regrowth
    veg_lvl_grid[burning_cells & (type_grid == 1)] -= 2
    veg_lvl_grid[burning_cells & (type_grid == 2)] -= 3
    veg_lvl_grid[burning_cells & (type_grid == 3)] -= 1

    veg_lvl_grid[burnt_cells] += 0.5
    
    # alternative implementation below -- each cell type grows at different rate 

    # veg_lvl_grid[burnt_cells & (type_grid == 1)] += 1
    # veg_lvl_grid[burnt_cells & (type_grid == 2)] += 1
    # veg_lvl_grid[burnt_cells & (type_grid == 3)] += 1


    # probabilistic model
    # probability of cell being set on fire depends on no. of neighbouring cells on fire and type of cell
    # need to modify the probabilities here to something sensible

    # probabilities for each type of vegetation being set on fire
    p_t1 = 0.01
    p_t2 = 0.01
    p_t3 = 0.01

    # get all cells that are in risk of catching fire (all cells with at least one neighbour on fire, not a 
    # lake and is not already burning)
    fire_risk_cells = ((adjusted_burning_n >= 1) & (grid == 0) & (type_grid != 0))
    # center_fire_risk_cells = (burning_n >= 1) & (grid == 0) & (type_grid != 0)
    
    type_1 = (type_grid == 1)
    type_2 = (type_grid == 2)
    type_3 = (type_grid == 3)

    for i in fire_risk_cells:
        for j in i:
            if j == False:
                f.write(f"⬚ ")
            else:
                f.write("■ ")
        f.write("\n")
    f.write("\n\n\n\n")

    t1_fire_risk = fire_risk_cells & type_1
    t2_fire_risk = fire_risk_cells & type_2
    t3_fire_risk = fire_risk_cells & type_3

    for i in t1_fire_risk:
        for j in i:
            if j == False:
                f5.write("⬚ ")
            else:
                f5.write("■ ")
        f5.write("\n")
    f5.write("\n\n\n\n")

    rnd_array = np.random.rand(20,20)

    t1_fire = rnd_array < p_t1
    t2_fire = rnd_array < p_t2
    t3_fire = rnd_array < p_t3

    set_fire = (t1_fire & t1_fire_risk) | (t2_fire & t2_fire_risk) | (t3_fire & t3_fire_risk)
    # set_fire = fire_risk_cells
    set_burnt = (veg_lvl_grid == 0) & (grid != 2)
    set_new = (veg_lvl_grid == fuel_cap) & (grid == 2)
   
    
    # if cell already on fire and fuel level still above 0, keep cells on fire
    keep_fire = ((veg_lvl_grid > 0) & (grid == 1))
    # if cell is in burnt state and has not yet recovered fully, keep burnt
    keep_burnt = ((veg_lvl_grid < fuel_cap) & (grid == 2))

    # set final values for grid
    grid[:, :] = 0
    grid[set_fire | keep_fire] = 1
    grid[keep_burnt] = 2
    grid[set_new] = 0 
    grid[set_burnt] = 2

    # cells that have fuel value n (regrowth complete) turn into state 0 (not burning/flammable)
    # grid_cpy[veg_lvl_grid == fuel_cap] = 0

    # grid_cpy[:,:] = 0
    # grid_cpy[type_1] = 2
    # grid_cpy[type_2] = 1
    # grid_cpy[type_3] = 0
    
    
    return grid



def transition_test(grid, neighbourstates, neighbourcounts, type_grid, veg_lvl_grid):
    '''
    Test transition function
    Issue: neighbourcounts does not seem to be updating for each time stepwhen looking at 
    neighbour_map.txt whereas the grid is being updated based on the neighbourcounts
    '''
    grid_cpy = grid
    not_burning_n, burning_n, burnt_n = neighbourcounts
    NW, N, NE, W, E, SW, S, SE = neighbourstates

    # fire = (burning_n >= 1) & (grid_cpy == 0)
    
    for line in NW:
        for i in line:
            if i > 0:
                f4.write(f" {str(i)[0]} ")
            else:
                f4.write(" ⬚ ")
        f4.write("\n")
    f4.write("\n\n\n\n")

    for line in burning_n:
        for i in line:
            if i > 0:
                f3.write(f" {str(i)[0]} ")
            else:
                f3.write(" ⬚ ")
        f3.write("\n")
    f3.write("\n\n\n\n")

    # for line in fire:
    #     for i in line:
    #         if i == False:
    #             f.write("⬚ ")
    #         else:
    #             f.write("x ")
    #         f.write(" ")
    #     f.write("\n")
    # f.write("\n\n\n\n")
 
    for i in grid_cpy:
        for j in i:
            if j == False:
                f2.write(f"⬚ ")
            else:
                f2.write("x ")
        f2.write("\n")
    f2.write("\n\n\n\n")
    

    keep_fire = grid_cpy == 1
    

    not_yet = grid_cpy != 1

    while(True):
        row = rnd.randint(0,19)
        col = rnd.randint(0,19)
        # f_log.write(f"Trying coord {row} and {col}")
        f_log.write("\n")
        if grid_cpy[row,col] != 1:
            not_yet[:,:] = 0
            not_yet[row,col] = 1
            # f_log.write(f"Added {row} and {col}")
            f_log.write("\n\n\n")
            break
        else:
            f_log.write("Trying another combo wombo")
            f_log.write("\n\n\n")
            continue
    grid_cpy[:,:] = 0
    grid_cpy = (keep_fire | not_yet)
    # grid_cpy[fire | keep_fire] = 1

    
    return grid_cpy

def write_bool_ndarray(nd_array, filename):
    with open(f"{filename}.txt", 'w') as file:
        for i in nd_array:
            for j in i:
                if j == False:
                    file.write(f"⬚ ")
                else:
                    file.write("■ ")
            file.write("\n")
        file.write("\n\n\n\n")
    
    
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

    # grid for edge cases 1 = top, 2 = left, 3 = right, 4 = down
    rows, cols = config.grid_dims
    edge_case_grid = np.zeros(config.grid_dims)
    edge_case_grid[0, 1:cols-1] = 1
    edge_case_grid[1:rows-1, 0] = 2
    edge_case_grid[1:rows-1, cols-1] = 3
    edge_case_grid[rows-1, 1:cols-1] = 4
    # 5 = upper left corner, 6 = upper right corner, 7 = lower left corner, 8 = lower right corner
    edge_case_grid[0,0] = 5
    edge_case_grid[0,cols-1] = 6
    edge_case_grid[rows-1,0] = 7
    edge_case_grid[rows-1,cols-1] = 8




    test.write(f"rows: {rows}  cols: {cols}\n")
    for line in edge_case_grid:
        for i in line:
            if i > 0:
                test.write(f"{str(i)[0]} ")
            else:
                test.write("⬚ ")
        test.write("\n")
    test.write("\n\n\n\n")

    # Keeps track of how long each cell stays on fire. Period of burning based on type of vegetation
    veg_lvl_grid = np.zeros((20,20))
    veg_lvl_grid.fill(fuel_cap)
    
    # Create grid object using parameters from config + transition function

    # grid = Grid2D(config, (transition_test, type_grid, veg_lvl_grid))
    grid = Grid2D(config, (transition_function, type_grid, veg_lvl_grid, edge_case_grid))
    # grid = Grid2D(config, (transition_func, type_grid, veg_lvl_grid))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()


f.close()
f2.close()
f3.close()
f4.close()
f_log.close()