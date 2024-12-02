import ezbolt
import time
import numpy as np
import pandas as pd
import math
from tqdm import tqdm
import json
from multiprocessing import Pool, cpu_count



# parameters to vary
n_rows = [int(x) for x in [2,3,4,5,6,7,8,9,10,11,12]]
n_cols = [int(x) for x in [1,2,3]]
n_degrees = [int(x) for x in np.linspace(0,75,76)]
n_eccs = [int(x) for x in np.linspace(1,36,36)]

row_spacing = 3
col_spacing = 3
csv_filename = "Cu Coefficient Table.csv"
json_filename = "Cu Coefficient Table.json"


# test run to estimate expected runtime
time_start = time.time()
bolt_group = ezbolt.BoltGroup()
bolt_group.add_bolts(xo=0, yo=0, width=6, height=6, nx=3, ny=3)
_= bolt_group.solve(Vx=-10, Vy=-30, torsion=-200, verbose=False)
time_end = time.time()

# calculate expected run time and ask user if want to continue
n_iterations = len(n_rows) * len(n_cols)* len(n_degrees) * len(n_eccs)
run_time = (time_end - time_start)
n_cores = cpu_count()
serial_runtime = n_iterations * run_time
parallel_runtime = serial_runtime / n_cores
print("{:,.0f} iterations. ~{:.0f} ms per run. ".format(n_iterations, run_time*1000))
print("Estimated Serial Runtime = {:.1f} minutes".format(serial_runtime/60))
print("Estimated Parallel Runtime = {:.1f} minutes".format(parallel_runtime/60))
user_option = input("Would you like to continue? 1=serial, 2=parallel, 3=exit: ")
if user_option == "3":
    raise RuntimeError("stopped by user")
else:
    run_serial = True if user_option == "1" else False


# define function to run in parallel
def compute_cu(args):
    """ function used to calculate Ce and Cu"""
    # unpack arguments
    n_col, n_row, ecc, degree = [args[0], args[1], args[2], args[3]]
    
    # calculate input parameters based on orientation and eccentricity
    nx = n_col
    ny = n_row
    width = (n_col-1) * col_spacing
    height = (n_row-1) * row_spacing
    
    Vx = -math.sin(degree * math.pi / 180) * 100
    Vy = -math.cos(degree * math.pi / 180) * 100
    torsion = Vy * ecc
    
    # create bolt group and calculate Cu
    bolt_group = ezbolt.BoltGroup()
    bolt_group.add_bolts(xo=0, yo=0, width=width, height=height, nx=nx, ny=ny)
    r = bolt_group.solve(Vx=Vx, Vy=Vy, torsion=torsion, verbose=False)
    Ce = r["Elastic Method - Center of Rotation"]["Ce"]
    Cu = r["Instant Center of Rotation Method"]["Cu"]
    
    return [n_col, n_row, ecc, degree, Ce, Cu]
    
# create arg_list
arg_list = []
for a in n_cols:
    for b in n_rows:
        for c in n_eccs:
            for d in n_degrees:
                arg_list.append([a,b,c,d])

if run_serial:
    # run calculation in serial
    results = []
    for a in tqdm(arg_list):
        results.append(compute_cu(a))
else:   
    # run calculation in parallel
    print("\nStarting parallel computation. This may take some time...")
    print("Some bolt group configurations taken longer to converge. Progress bar may not be accurate.")
    start=time.time()
    with Pool() as pool:
        results = list(tqdm(pool.imap(compute_cu, arg_list), total=n_iterations))
    print("Done! Elapsed time = {:.2f} s".format(time.time() - start))



# write results to csv
df_data = pd.DataFrame(results, columns = ["columns", "rows", "eccentricity", "degree", "Ce", "Cu"])
df_data.to_csv(csv_filename, index=False)


# write results to json
json_data = dict()
for row in results:
    col_key = row[0]
    row_key = row[1]
    ecc_key = row[2]
    deg_key = row[3]
    ce = row[4]
    cu = row[5]
    
    if col_key not in json_data:
        json_data[col_key] = dict()
    if row_key not in json_data[col_key]:
        json_data[col_key][row_key] = dict()
    if ecc_key not in json_data[col_key][row_key]:
        json_data[col_key][row_key][ecc_key] = dict()
    if deg_key not in json_data[col_key][row_key][ecc_key]:
        json_data[col_key][row_key][ecc_key][deg_key] = dict()
    
    json_data[col_key][row_key][ecc_key][deg_key]["Ce"] = ce
    json_data[col_key][row_key][ecc_key][deg_key]["Cu"] = cu
    
with open(json_filename, "w") as f:
    json.dump(json_data, f)


