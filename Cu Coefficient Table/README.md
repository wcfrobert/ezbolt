

## C Coefficients Tabulated

The .csv and .json files above contain over 90,000 pre-computed C coefficients. Simply import this csv into a spreadsheet, and do some XLOOKUP to find the appropriate C coefficients for your connection design. No solvers necessary! Way faster than referencing the AISC steel construction manual. Try it out yourself. 

The csv file contain the following columns:

* `Cu Coefficient.csv`
  * **columns**: column of bolts 
  * **rows**: row of bolts 
  * **eccentricity**: load eccentricity (ex = Mz / Vy) 
  * **degree**:  load orientation (0 degrees is vertical downward) 
  * **Ce**: elastic center of rotation coefficient
  * **Cu**: (plastic) instant center of rotation coefficient (values tabulated in AISC steel construction manual)

For users more comfortable with programming, I've also provided the same data in json format. 

* `Cu Coefficient.json`
  * The key order is as follows: `...[N_columns][N_rows][eccentricity][degree]`["Cu" or "Ce"]. All keys are integers.
  * For example, `...[1][6][6][0]["Cu"]` returns the Cu for a single column of bolt with 6 rows, vertical force with 6" eccentricity. The returned Cu is 3.55 which matches the AISC tables.


If you would like to generate your own table, try running `generate_cu_table.py` in the root folder. You can specify the range for each parameter. The computed coefficients above are based on the following:

* **columns**: 1 col to 3 cols
* **rows**: 2 rows to 12 rows
* **eccentricity**: 1 to 36
* **degree**: 0 to 75

That's 3 * 11 * 76 * 36 = 90,288 iterations. On my Linux desktop with an Intel i7-11700, each iteration took ~ 50 ms. A serial run would have taken ~75 minutes. With some parallel processing, I managed to bring that down to ~5 minutes (running 16 threads).



## Validation Problems



