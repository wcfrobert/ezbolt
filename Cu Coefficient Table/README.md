The .csv and .json file above contains Cu coefficients for ~90,000 common bolt configurations. Need to find some Cu coefficient for your connection design? Just copy the csv into your spreadsheet and do some VLOOKUP. No solvers needed!

* `Cu Coefficient.csv`
  * **columns**: column of bolts 
  * **rows**: row of bolts 
  * **eccentricity**: x eccentricity (e_x = M / P_y) 
  * **degree**:  load orientation (0 degrees is vertical downward) 
  * **Ce**: elastic center of rotation coefficient
  * **Cu**: (plastic) instant center of rotation coefficient
* `Cu Coefficient.json`
  * This is a nested dictionary for engineers more comfortable with python. Dictionary lookup is pretty much instant whereas solving a bolt configuration may take ~ 100 ms depending on your computer. 
  * The key order is as follows: `...[N_columns][N_rows][eccentricity][degree]`["Cu" or "Ce"]. All keys are integers.
  * For example, `...[1][6][6][0]["Cu"]` returns the Cu for a single column of bolt with 6 rows, vertical force with 6" eccentricity. The returned Cu is 3.55 which matches the AISC tables.

The cached coefficients have the following range:

* **columns**: 1 to 3
* **rows**: 2 to 12
* **eccentricity**: 1 to 36
* **degree**: 0 to 75
