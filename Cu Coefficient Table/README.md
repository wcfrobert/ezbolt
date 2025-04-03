

## C Coefficients Tabulated

The .csv and .json files above contain over 90,000 pre-computed C coefficients. Simply import this csv into a spreadsheet, and do some XLOOKUP to find the appropriate C coefficients. No solvers necessary! The csv file contain the following columns. Note all bolts are assumed to have 3" spacing.

* `Cu Coefficient.csv`
  * **columns**: column of bolts 
  * **rows**: row of bolts 
  * **eccentricity**: horizontal load eccentricity (ex = Mz / Vy) 
  * **degree**:  load orientation (0 degrees is vertical downward) 
  * **Ce**: elastic center of rotation coefficient
  * **Cu**: (plastic) instant center of rotation coefficient

I've also provided the same data in json format. 

* `Cu Coefficient.json`
  * The key order is as follows: `...[N_columns][N_rows][eccentricity][degree]`["Cu" or "Ce"]. All keys are integers.
  * For example, `...[1][6][6][0]["Cu"]` returns the Cu for a single column of bolt with 6 rows, vertical force with 6" eccentricity. The returned Cu is 3.55 which matches the AISC tables.


If you would like to generate your own table, try running `generate_cu_table.py` in the root folder. You can specify the range for each parameter. The computed coefficients above are based on the following:

* **columns**: 1 col to 3 cols
* **rows**: 2 rows to 12 rows
* **eccentricity**: 1 to 36
* **degree**: 0 to 75
* **spacing**: ALL BOLTS ARE SPACED AT 3" ON CENTER.

That's 3 * 11 * 76 * 36 = 90,288 iterations. On my Linux desktop with an Intel i7-11700, each iteration took ~ 50 ms. A serial run would have taken ~75 minutes. With some parallel processing, I managed to bring that down to ~5 minutes (running 16 threads).



## Validation Problems

In the examples below, all bolts are spaced 3" apart unless otherwise noted. Assume A325-N 3/4" bolt with shear capacity of 17.9 kips. Only consider bolt shear; ignore all other limit states. The code to analyze these three examples is provided in: `validation_examples.py`


**Example 1:** A 9" long bolt group with 4 rows, 1 columns, subjected to Py = -40 kips, and Mz = -160 k.in.

<div align="center">
  <img src="https://github.com/wcfrobert/ezbolt/blob/master/doc/example1.png?raw=true" alt="fig" style="width: 90%;" />
</div>

**Example 2:** A 3" x 9" bolt group with 4 rows, 2 columns, subjected to Px = 80 kips, Py = -80 kips, and Mz = -160 k.in.

<div align="center">
  <img src="https://github.com/wcfrobert/ezbolt/blob/master/doc/example2.png?raw=true" alt="fig" style="width: 90%;" />
</div>


**Example 3:** A 8" x 6" bolt group with 2 rows, 2 columns, subjected to Px = -17.3 kips, Py = -30 kips, and Mz = -180 k.in.

<div align="center">
  <img src="https://github.com/wcfrobert/ezbolt/blob/master/doc/example3.png?raw=true" alt="fig" style="width: 90%;" />
</div>