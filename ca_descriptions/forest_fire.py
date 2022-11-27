# Name: forest_fire
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
import numpy as np
import os.path
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

# ------------------ Parameters ------------------ #
# if collecting results, edit these parameters
dimensions = (40,40) # suggested that dimensions stays a multiple of 20 x 20 e.g. 40 x 40 or 80 x 80 or 100 x 100 .. etc ..

fuel_cap = 100 # maximum amount of fuel afforded for each cell

# probability cell will be set on fire
p_forest = 0.05
p_charpal = 0.1
p_canyon = 0.2

# how much fuel each type of cell consumes per generation
charpal_burn_rate = 2
forest_burn_rate = 1
canyon_burn_rate = 3

# how much fuel each type gains back every generation
charpal_growth_rate = 1
forest_growth_rate = 1
canyon_growth_rate = 1

# wind direction -> n, w, e, s, ne, nw, se, sw | 0 = no wind
wind_dir = '0'
wind_effect_multiplier = 0.6 # the lower the number the greater the effect, as Probability(Cell catches fire) is multiplied by inverse of this 

# ------------------ ---------- ------------------ #



dir_flip_dict = {'n':'s',
                's':'n',
                'w':'e',
                'e':'w',
                'ne':'sw',
                'sw':'ne',
                'nw':'se',
                'se':'nw'}



# f = open("fire_neighbour_map.txt", 'w')
# f2 = open("grid_map.txt", 'w')
# f3 = open("neighbour_map.txt", 'w')
# f4 = open("state_map.txt", 'w')
# f5 = open("t1_fire_risk.txt", 'w')
# edg = open("edge_case_map.txt", 'w')
# test = open("test_file.txt", 'w')
# typ_map = open("type_map.txt", 'w')
# pgrid = open("p_grid.txt", 'w')
# f_log = open("log.txt", 'w')
# wind_bool = open("wind_bool.txt", 'w')
# wind_num = open("wind_num.txt", 'w')

def setup(args):
    """Set up the config object used to interact with the GUI"""
    config_path = args[0]
    config = utils.load(config_path)
    # -- THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED --
    config.title = "forest_fire"
    config.dimensions = 2
    # 0: no state, 1: burning, 2: burnt, 3: lake, 4: charpal, 5: forest, 6: canyon 
    config.states = (0,1,2,3,4,5,6)
    # -------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    config.state_colors = [(0,0,0),(1,0.4,0.2),(0.5,0.35,0.17),(0.55,0.85,0.85),(0.2,0.6,0.4),(0,0.2,0),(0.83,0.7,0.55)]
    config.grid_dims = dimensions
    # ----------------------------------------------------------------------

    # the GUI calls this to pass the user defined config
    # into the main system with an extra argument
    # do not change
    if len(args) == 2:
        config.save()
        sys.exit()
    return config

def transition_function(grid, neighbourstates, neighbourcounts, type_grid, veg_lvl_grid, edge_case_grid, p_grid, wind_dir, rows, cols):
    not_state_n, burning_n, burnt_n, lake_n, charpal_n, forest_n, canyon_n = neighbourcounts
    NW, N, NE, W, E, SW, S, SE = neighbourstates


    wind_grid_dict = {'n':N,'s':S,'w':W,'e':E,'nw':NW,'ne':NE,'SW':SW,'SE':SE}

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
    ne_u_right_corner = ((edge_case_grid == 6) & (NE == 1)).astype(int)
    n_u_right_corner = ((edge_case_grid == 6) & (N == 1)).astype(int)
    nw_u_right_corner = ((edge_case_grid == 6) & (NW == 1)).astype(int)
    e_u_right_corner = ((edge_case_grid == 6) & (E == 1)).astype(int)
    se_u_right_corner = ((edge_case_grid == 6) & (SE == 1)).astype(int)

    u_right_corner_n = ne_u_right_corner + n_u_right_corner + nw_u_right_corner + e_u_right_corner + se_u_right_corner

    # lower right corner edge cases
    se_l_right_corner = ((edge_case_grid == 8) & (SE == 1)).astype(int)
    s_l_right_corner = ((edge_case_grid == 8) & (S == 1)).astype(int)
    sw_l_right_corner = ((edge_case_grid == 8) & (SW == 1)).astype(int)
    e_l_right_corner = ((edge_case_grid == 8) & (E == 1)).astype(int)
    ne_l_right_corner = ((edge_case_grid == 8) & (NE == 1)).astype(int)

    l_right_corner_n = se_l_right_corner + s_l_right_corner + sw_l_right_corner + e_l_right_corner + ne_l_right_corner

    # lower left corner edge cases
    se_l_left_corner = ((edge_case_grid == 7) & (SE == 1)).astype(int)
    s_l_left_corner = ((edge_case_grid == 7) & (S == 1)).astype(int)
    sw_l_left_corner = ((edge_case_grid == 7) & (SW == 1)).astype(int)
    w_l_left_corner = ((edge_case_grid == 7) & (W == 1)).astype(int)
    nw_l_left_corner = ((edge_case_grid == 7) & (NW == 1)).astype(int)

    l_left_corner_n = se_l_left_corner + s_l_left_corner + sw_l_left_corner + w_l_left_corner + nw_l_left_corner

    # get a grid for the edge case neighbour count and subtract from main neighbour count to get an adjusted
    # grid
    edge_case_n = left_edge_n + right_edge_n + top_edge_n + bottom_edge_n + u_left_corner_n + u_right_corner_n + l_left_corner_n + l_right_corner_n
    adjusted_burning_n = burning_n - edge_case_n

    # adjust the neigbourstates values for the edge case cells
    N = N - n_top_edge - n_u_left_corner - n_u_right_corner
    S = S - s_bottom_edge - s_l_left_corner - s_l_right_corner
    W = W - w_l_left_corner - w_left_edge - w_u_left_corner
    E = E - e_l_right_corner - e_right_edge - e_u_right_corner
    NE = NE - ne_l_right_corner - ne_right_edge - ne_top_edge - ne_u_left_corner - ne_u_right_corner
    NW = NW - nw_l_left_corner - nw_left_edge - nw_top_edge - nw_u_left_corner - nw_u_right_corner
    SE = SE - se_bottom_edge - se_l_left_corner - se_l_right_corner - se_right_edge - se_u_right_corner
    SW = SW - sw_bottom_edge - sw_l_left_corner - sw_l_right_corner - sw_left_edge - sw_u_left_corner

    # for line in edge_case_n:
    #     for i in line:
    #         if i > 0:
    #             edg.write(f"{str(i)[0]} ")
    #         else:
    #             edg.write("⬚ ")
    #     edg.write("\n")
    # edg.write("\n\n\n\n")

    # for line in adjusted_burning_n:
    #     for i in line:
    #         if i > 0:
    #             test.write(f"{str(i)[0]} ")
    #         else:
    #             test.write("⬚ ")
    #     test.write("\n")
    # test.write("\n\n\n\n")

    # if lake is in burning state, turn it back 
    grid[type_grid == 0] = 3

    # files for debugging
    # for line in NW:
    #     for i in line:
    #         if i > 0:
    #             f4.write(f" {str(i)[0]} ")
    #         else:
    #             f4.write(" ⬚ ")
    #     f4.write("\n")
    # f4.write("\n\n\n\n")
    
    # for i in grid:
    #     for j in i:
    #         f2.write(f"{str(j)}")
    #         # if j == False:
    #         #     f2.write(f"⬚ ")
    #         # else:
    #         #     f2.write("■ ")
    #     f2.write("\n")
    # f2.write("\n\n\n\n")
    
    # for line in burning_n:
    #     for i in line:
    #         if i > 0:
    #             f3.write(f"{str(i)[0]} ")
    #         else:
    #             f3.write("⬚ ")
    #     f3.write("\n")
    # f3.write("\n\n\n\n")

    # update vegetation level after burning, search for cells that are either burnt or burning and handle
    # accordingly
    burning_cells = (grid == 1)
    burnt_cells = (grid == 2)

    # decrease to represent fuel depletion, increase to represent regrowth
    veg_lvl_grid[burning_cells & (type_grid == 1)] -= charpal_burn_rate
    veg_lvl_grid[burning_cells & (type_grid == 2)] -= forest_burn_rate
    veg_lvl_grid[burning_cells & (type_grid == 3)] -= canyon_burn_rate

    # veg_lvl_grid[burnt_cells] += 0.5
    
    # alternative implementation below -- each cell type grows at different rate 

    veg_lvl_grid[burnt_cells & (type_grid == 1)] += charpal_growth_rate
    veg_lvl_grid[burnt_cells & (type_grid == 2)] += forest_growth_rate
    veg_lvl_grid[burnt_cells & (type_grid == 3)] += canyon_growth_rate


    # probability of cell being set on fire depends on no. of neighbouring cells on fire and type of cell
    # need to modify the probabilities here to something sensible

    # get all cells that are in risk of catching fire (all cells with at least one neighbour on fire, not a 
    # lake and is not already burning)
    fire_risk_cells = ((adjusted_burning_n >= 1) & ((grid > 3) | (grid == 0)) & (type_grid != 0))
    
    if wind_dir != '0':
        # calculate effects of wind on cells, if wind is pushing fire towards cell, increase prob of cell being set on fire
        # if wind pushing fire in opposite direction of cell, decrease prob of cell being set on fire
        wind_from_dir_bool = (wind_grid_dict[dir_flip_dict[wind_dir]] == 1) & fire_risk_cells
        wind_from_dir_inv = np.invert(wind_from_dir_bool).astype(int)
        wind_from_dir = wind_from_dir_bool.astype(int) * (1/wind_effect_multiplier)
        from_dir = wind_from_dir + wind_from_dir_inv

        wind_from_opp_dir_bool = (wind_grid_dict[wind_dir] == 1) & fire_risk_cells
        wind_from_opp_dir_inv = np.invert(wind_from_opp_dir_bool).astype(int)
        wind_from_opp_dir = wind_from_opp_dir_bool.astype(int) * (wind_effect_multiplier)
        from_opp_dir = wind_from_opp_dir_inv + wind_from_opp_dir

        # for i in wind_from_dir_bool:
        #     for j in i:
        #         if j == False:
        #             wind_bool.write(f"⬚ ")
        #         else:
        #             wind_bool.write("■ ")
        #     wind_bool.write("\n")
        # wind_bool.write("\n\n\n\n")

        # for line in wind_from_dir:
        #     for i in line:
        #         wind_num.write(f" {str(i)} ")
        #     wind_num.write("\n")
        # wind_num.write("\n\n\n\n")

        # final multiplier such that if winds pushing from both opposite directions, effects cancel (eventhough it won't
        # happen in this simulation)
        wind_mltp_grid = from_dir * from_opp_dir
        # probabilities of cells is multiplied by proportion of neighbour cells on fire and also the wind multiplier
        p_grid = p_grid * (adjusted_burning_n/8) * wind_mltp_grid
    else:
        p_grid = p_grid * (adjusted_burning_n/8) # don't consider wind effects


    # type_1 = (type_grid == 1)
    # type_2 = (type_grid == 2)
    # type_3 = (type_grid == 3)

    # for i in fire_risk_cells:
    #     for j in i:
    #         if j == False:
    #             f.write(f"⬚ ")
    #         else:
    #             f.write("■ ")
    #     f.write("\n")
    # f.write("\n\n\n\n")

    # t1_fire_risk = fire_risk_cells & type_1
    # t2_fire_risk = fire_risk_cells & type_2
    # t3_fire_risk = fire_risk_cells & type_3

    

    # for line in p_grid:
    #     for i in line:
    #         pgrid.write(f" {str(i)} ")
    #     pgrid.write("\n")
    # pgrid.write("\n\n\n\n")

    rnd_array = np.random.rand(rows, cols)

    # for line in rnd_array:
    #     for i in line:
    #         pgrid.write(f" {str(i)} ")
    #     pgrid.write("\n")
    # pgrid.write("\n\n\n\n")

    # t1_fire = rnd_array < p_t1
    # t2_fire = rnd_array < p_t2
    # t3_fire = rnd_array < p_t3

    # set_fire = (t1_fire & t1_fire_risk) | (t2_fire & t2_fire_risk) | (t3_fire & t3_fire_risk)
    set_fire = (p_grid > rnd_array) & (fire_risk_cells)
    set_burnt = (veg_lvl_grid == 0) & (grid != 2)
    # set_new = (veg_lvl_grid == fuel_cap) & (grid == 2)

    # for line in set_fire:
    #     for i in line:
    #         pgrid.write(f" {str(i)} ")
    #     pgrid.write("\n")
    # pgrid.write("\n\n\n\n")

    set_new_1 = (veg_lvl_grid == fuel_cap) & (grid == 2) & (type_grid == 1)
    set_new_2 = (veg_lvl_grid == fuel_cap) & (grid == 2) & (type_grid == 2)
    set_new_3 = (veg_lvl_grid == fuel_cap) & (grid == 2) & (type_grid == 3)
   
    
    # if cell already on fire and fuel level still above 0, keep cells on fire
    keep_fire = ((veg_lvl_grid > 0) & (grid == 1))
    # if cell is in burnt state and has not yet recovered fully, keep burnt
    keep_burnt = ((veg_lvl_grid < fuel_cap) & (grid == 2))

    # set final values for grid
    grid[:, :] = 0
    grid[type_grid == 0] = 3
    grid[type_grid == 1] = 4
    grid[type_grid == 2] = 5
    grid[type_grid == 3] = 6
    grid[set_fire | keep_fire] = 1
    grid[keep_burnt] = 2
    # grid[set_new] = 0 
    grid[set_new_1] = 4
    grid[set_new_2] = 5 
    grid[set_new_3] = 6
    
    grid[set_burnt] = 2
    
    
    return grid
    
def main():
    """ Main function that sets up, runs and saves CA"""
    # Get the config object from set up
    config = setup(sys.argv[1:])
    rows, cols = config.grid_dims
    
    # Keeps track of type of vegetation in each cell (assuming 10000 x 10000) useful for specifying
    # behaviour depending 

    # 1 = chaparral, 2 = dense forest, 3 = canyon, 0 = lake
    type_grid = np.ones(config.grid_dims)

    # type_grid[8:14, 0:10] = 2
    # type_grid[2:7, 6:10] = 2
    # type_grid[7, 3:10] = 0
    # type_grid[3:16, 12] = 3

    type_grid[round(rows*(2/5)):round(rows*(7/10)), 0:round(cols*0.5)] = 2
    type_grid[round(rows*(3/20)):round(rows*(7/10)), round(cols*(3/10)):round(cols*0.5)] = 2
    type_grid[round(rows*(14/40)):round(rows*(16/40)), round(cols*(3/20)):round(cols*0.5)] = 0
    type_grid[round(rows*(3/20)):round(cols*(4/5)), round(cols*(24/40)):round(cols*(26/40))] = 3

    # for line in type_grid:
    #     for i in line:
    #         typ_map.write(f"{str(i)[0]} ")
    #     typ_map.write("\n")
    # typ_map.write("\n\n\n\n")

    # grid for edge cases 1 = top, 2 = left, 3 = right, 4 = down
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

    # test.write(f"rows: {rows}  cols: {cols}\n")
    # for line in edge_case_grid:
    #     for i in line:
    #         if i > 0:
    #             test.write(f"{str(i)[0]} ")
    #         else:
    #             test.write("⬚ ")
    #     test.write("\n")
    # test.write("\n\n\n\n")

    # Keeps track of how long each cell stays on fire. Period of burning based on type of vegetation
    veg_lvl_grid = np.zeros(dimensions)
    veg_lvl_grid.fill(fuel_cap)
    
    p_grid = np.zeros(config.grid_dims)
    p_grid[type_grid == 0] = 0
    p_grid[type_grid == 1] = p_charpal
    p_grid[type_grid == 2] = p_forest
    p_grid[type_grid == 3] = p_canyon

    # Create grid object using parameters from config + transition function

    # grid = Grid2D(config, (transition_test, type_grid, veg_lvl_grid))
    grid = Grid2D(config, (transition_function, type_grid, veg_lvl_grid, edge_case_grid, p_grid, wind_dir, rows, cols))
    # grid = Grid2D(config, (transition_func, type_grid, veg_lvl_grid))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()


# f.close()
# f2.close()
# f3.close()
# f4.close()
# f_log.close()