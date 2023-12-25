<h1 align="center">
  <br>
  <img src="https://github.com/wcfrobert/ezbolt/blob/master/doc/logo.png?raw=true" alt="logo" style="zoom:20%;" />
  <br>
  Bolt Force Calculation in Python
  <br>
</h1>
<p align="center">
Bolted connection force determination via elastic method and instant center of rotation (ICR) method.
</p>



<div align="center">
  <img src="https://github.com/wcfrobert/ezbolt/blob/master/doc/demo.gif?raw=true" alt="demo" style="width: 100%;" />
</div>


- [Introduction](#introduction)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Theoretical Background - Elastic Method](#theoretical-background---elastic-method)
- [Theoretical Background - ICR Method](#theoretical-background---icr-method)
- [Assumptions and Limitations](#assumptions-and-limitations)
- [License](#license)



## Introduction

What does this thing do?







## Quick Start

Run main.py:

```python
import ezbolt

# initialize a bolt group
bolt_group = ezbolt.boltgroup.BoltGroup()

# add bolts
bolt_group.add_bolts(xo=0, yo=0, width=6, height=6, nx=3, ny=3)

# preview geometry
ezbolt.plotter.preview(bolt_group)

# calculate bolt forces
results = bolt_group.solve(Vx=50, Vy=50, torsion=200)

# plot bolt forces
ezbolt.plotter.plot_elastic(bolt_group)
ezbolt.plotter.plot_ECR(bolt_group)
ezbolt.plotter.plot_ICR(bolt_group)

```

Preview your bolt group using the plotter.preview() function:

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/preview.png?raw=true" alt="demo" style="width: 80%;" />
</div>

plotter.plot_elastic() shows bolt forces as calculated using the elastic method + superposition of forces.

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/elasticmethod.png?raw=true" alt="demo" style="width: 80%;" />
</div>

plotter.plot_ECR() shows bolt forces as calculated using the elastic method + center of rotation.

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/ECRmethod.png?raw=true" alt="demo" style="width: 80%;" />
</div>

plotter.plot_ICR() shows bolt forces as calculated using ICR method.

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/ICRmethod.png?raw=true" alt="demo" style="width: 80%;" />
</div>


## Installation

**Option 1: Anaconda Python**

Simply run main.py using your Anaconda base environment. The following packages are used:

* Numpy
* Matplotlib
* Pandas

Installation procedure:

1. Download Anaconda python
2. Download this package (click the green "Code" button and download zip file)
3. Open and run "main.py" in Anaconda's Spyder IDE.


**Option 2: Vanilla Python**

1. Download this project to a folder of your choosing
    ```
    git clone https://github.com/wcfrobert/ezbolt.git
    ```
2. Change directory into where you downloaded ezbolt
    ```
    cd ezbolt
    ```
3. Create virtual environment
    ```
    py -m venv venv
    ```
4. Activate virtual environment
    ```
    venv\Scripts\activate
    ```
5. Install requirements
    ```
    pip install -r requirements.txt
    ```
6. run ezbolt
    ```
    py main.py
    ```


## Usage


Here is a comprehensive list of all the commands that is available to the user. 

**Adding Bolts**

* `ezbolt.BoltGroup.add_bolts`




**Solving**

* `ezbolt.BoltGroup.solve()`


**Visualizations**

* `ezbolt.plotter.preview()`


## Theoretical Background - Elastic Method




## Theoretical Background - ICR Method




## Assumptions and Limitations

* Units are in (kip, in) unless otherwise noted
* Note the program only calculates connection capacity with respect to bolt shear. Other limit states - such as plate rupture, block shear, bearing and tearout - are not considered.



## License

MIT License

Copyright (c) 2023 Robert Wang