<h1 align="center">
  <br>
  <img src="https://github.com/wcfrobert/ezbolt/blob/master/doc/logo.png?raw=true" alt="logo" style="width: 60%;" />
  <br>
  Bolt Force Calculation in Python
  <br>
</h1>
<p align="center">
Calculate bolt forces with Elastic Method and Instant Center of Rotation (ICR) method.
</p>

<div align="center">
  <img src="https://github.com/wcfrobert/ezbolt/blob/master/doc/demo.gif?raw=true" alt="demo" style="width: 75%;" />
</div>


- [Introduction](#introduction)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Theoretical Background - Elastic Method](#theoretical-background---elastic-method)
- [Theoretical Background - ICR Method](#theoretical-background---icr-method)
- [Theoretical Background - Brandt's Method for Locating ICR](#theoretical-background---brandt-s-method-for-locating-icr)
- [Assumptions and Limitations](#assumptions-and-limitations)
- [License](#license)


## Introduction

EZbolt is a Python program that calculates bolt forces in a bolt group subject to shear and in-plane torsion. It does so using both the Elastic Method and the Instant Center of Rotation (ICR) method as outlined in the AISC steel construction manual. The iterative algorithm for locating the center of rotation is explained in this paper by Donald Brandt: [Rapid Determination of Ultimate Strength of Eccentrically Loaded Bolt Groups.](https://www.aisc.org/Rapid-Determination-of-Ultimate-Strength-of-Eccentrically-Loaded-Bolt-Groups). Unlike the ICR coefficient tables in the steel construction manual which is provided in 15 degree increments, EZbolt can handle **any bolt arrangements, any load orientation, and any eccentricity**.


**Disclaimer:** this package is meant for <u>personal and educational use only</u>.


## Quick Start

Run main.py:

```python
import ezbolt

# initialize a bolt group
bolt_group = ezbolt.boltgroup.BoltGroup()

# add a 3x3 bolt group with 6" width and 6" depth with lower left corner located at (0,0)
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

`plotter.preview()` plots a bolt group preview:

<div align="center">
  <img src="https://github.com/wcfrobert/ezbolt/blob/master/doc/preview.png?raw=true" alt="demo" style="width: 50%;" />
</div>

`plotter.plot_elastic()` shows bolt force calculated from elastic method.

<div align="center">
  <img src="https://github.com/wcfrobert/ezbolt/blob/master/doc/elasticmethod.png?raw=true" alt="demo" style="width: 50%;" />
</div>

`plotter.plot_ECR()` shows bolt forces calculated from elastic center of rotation (ECR) method.

<div align="center">
  <img src="https://github.com/wcfrobert/ezbolt/blob/master/doc/ECRmethod.png?raw=true" alt="demo" style="width: 50%;" />
</div>

`plotter.plot_ICR()` shows bolt forces calculated from instant center of rotation (ICR) method.

<div align="center">
  <img src="https://github.com/wcfrobert/ezbolt/blob/master/doc/ICRmethod.png?raw=true" alt="demo" style="width: 50%;" />
</div>

`BoltGroup.solve()` returns a dictionary containing all relevant calculation results:

* `results["Elastic Method - Superposition"]`
    * `... ["Bolt Capacity"]`
    * `... ["Bolt Demand"]`
    * `... ["Bolt Force Table"]`
    * `... ["DCR"]`
* `results["Elastic Method - Center of Rotation"]`
    * `... ["Center of Rotation"]`
    * `... ["Ce"]`
    * `... ["Connection Capacity"]`
    * `... ["Connection Demand"]`
    * `... ["Bolt Force Table"]`
    * `... ["DCR"]`
* `results["Instant Center of Rotation Method"]`
    * `... ["ICR"]`
    * `... ["Cu"]`
    * `... ["Connection Capacity"]`
    * `... ["Connection Demand"]`
    * `... ["Bolt Force Tables"]`
    * `... ["DCR"]`


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
Pip install is available:

```
pip install ezbolt
```

## Usage

Here are all the public methods available to the user:

**Adding Bolts**

* `ezbolt.BoltGroup.add_bolts(xo, yo, width, height, nx, ny, perimeter_only=False)`
* `ezbolt.BoltGroup.add_bolt_single(x, y)`

**Solving**

* `ezbolt.BoltGroup.solve(Vx, Vy, torsion, bolt_capacity=17.9)`

**Visualizations**

* `ezbolt.plotter.preview(boltgroup_object)`
* `ezbolt.plotter.plot_elastic(boltgroup_object)`
* `ezbolt.plotter.plot_ECR(boltgroup_object)`
* `ezbolt.plotter.plot_ICR(boltgroup_object)`

For further guidance and documentation, you can access the docstring of any method using the help() command. (e.g. `help(ezbolt.boltgroup.BoltGroup.add_bolts)`)


## Theoretical Background - Elastic Method

A group of bolts can be treated like any geometric section, and their geometric properties can be calculated (e.g. centroid, moment of inertia, etc):

Centroid:

$$x_{cg} = \frac{\sum x_i}{N_{bolts}}$$

$$y_{cg} = \frac{\sum y_i}{N_{bolts}}$$

Moment of inertia about x and y axis:

$$I_x = \sum (y_i - y_{cg})^2$$

$$I_y = \sum (x_i - x_{cg})^2$$

Polar moment of inertia:

$$I_z = J = I_p = I_x + I_y$$

For in-plane shear, the resulting demand on individual bolts is simply total force divided by number of bolts. We do this about the x and y components separately. Let's call this **direct shear**.

$$v_{dx} = \frac{V_x}{N_{bolts}}$$

$$v_{dy} = \frac{V_y}{N_{bolts}}$$


In-plane torsion on the bolt group is converted to shear on the individual anchors. Let's call this **torsional shear**.

$$v_{tx} = \frac{M_z (y_i - y_{cg})}{I_z}$$

$$v_{ty} = \frac{-M_z (x_i - x_{cg})}{I_z}$$

Putting it all together, we use principle of superposition to **superimpose** (add) the bolt demands together. In other words, we can look at each action separately, then add them together at the end.

$$v_{x} = v_{dx} + v_{tx}$$

$$v_{y} = v_{dy} + v_{ty}$$

$$v_{resultant} = \sqrt{v_{x}^2 + v_{y}^2}$$

The key assumption of elastic method is that rotational and translational actions are decoupled and do not influence each other. This is not true and produces conservative results.


## Theoretical Background - ICR Method

A less conservative way of determining bolt forces is through the Instant Center of Rotation **(ICR)** method. The underlying theory is illustrated in the figure below. In short, when a bolt group is subjected to combined in-plane force and torsion, the bolt force and applied force vectors **revolve around an imaginary center**. The ICR method is conceptually simple, but identifying the ICR location will require iteration.

Rather than assuming elasticity and using geometric properties to determine bolt forces, we assume the bolt furthest from ICR has a deformation of 0.34", other bolts are assumed to have linearly varying deformation based on its distance from ICR (varying from 0" to 0.34"). We can then determine the corresponding force using the **force-deformation relationship** below.

$$\Delta_i = 0.34 (d_i / d_{max})$$

$$R_i =(1-e^{-10\Delta_i})^{0.55} \times R_{max}$$

Assuming the location of ICR has been correctly identified, equilibrium should hold.

$$\sum F_x = 0 = P_x -\sum R_{ix}$$

$$\sum F_y = 0 = P_y -\sum R_{iy}$$

$$\sum M = 0 = M_z -\sum m_i$$

<div align="center">
  <img src="https://github.com/wcfrobert/ezbolt/blob/master/doc/aisc2.31.png?raw=true" alt="demo" style="width: 60%;" />
</div>

The derivations will follow AISC notations which is somewhat different from the notations above. Most notably, we will use **P** to denote applied force instead of **V**, and **R** to denote in-plane bolt force instead of **v**.

Suppose we know the exact location of ICR, first let's calculate the applied moment with respect to this new center.

$$M_p = P \times r_o$$

The maximum bolt deformation of 0.34" occurs at the bolt furthest from ICR, the other bolts have deformation varying linearly between 0 to 0.34 based on its distance to the ICR ($d_i$)

$$\Delta_{max} = 0.34$$

$$\Delta_i = 0.34 \frac{d_i}{d_{max}}$$

Next, we can calculate individual bolt forces using the following force-deformation relationship:

$$R_i = (1-e^{-10\Delta_i})^{0.55} \times R_{max}$$

Now, we can calculate the reactive moment contributions from each bolt:

$$M_i = R_i \times d_i$$

$$M_i = R_{max} (1-e^{-10\Delta_i})^{0.55} \times d_i$$

$$\sum M_i = R_{max} \times \sum (1-e^{-10\Delta_i})^{0.55} d_i$$

Apply moment equilibrium and rearrange for P:

$$ M_{applied} = M_{resisting}$$

$$ M_p = \sum M_i$$

$$ P \times r_o = R_{max} \times \sum (1-e^{-10\Delta_i})^{0.55} d_i$$

$$ P = R_{max} \times \frac{\sum (1-e^{-10\Delta_i})^{0.55} d_i}{r_o}$$

Let the second term be the ICR coefficient C. You can think of C as simply a ratio between maximum bolt force and applied force

$$ P = R_{max} \times C$$

$$ C = \frac{\sum (1-e^{-10\Delta_i})^{0.55} d_i}{r_o}$$

Set $R_{max}$ equal to the bolt capacity and back-calculate the connection capacity:

$$ R_{max} = R_{capacity}$$

$$ P_{capacity} = R_{capacity} \times C$$

Notes:

1. Despite a nonlinear bolt force-deformation, the relationship between max bolt force ($R_{max}$) and applied force ($P$) is linear. In other words, if applied force doubles, so does maximum bolt force, and vice versa. Embedded in this is the **assumption that eccentricity (e = Mz / P) will remain constant**      
2. If we substitute 0.34 into the exponential function above, we get 0.9815 as there's a horizontal asymptote and we will never reach 1.0 exactly. We can make a simple adjustment to our "C" equation if we desire. Note that AISC does NOT make this adjustment as it is more conservative to set max bolt-force as $0.9815R_{max}$, effectively capping our DCR to 98%.

$$ (1 - e^{-10(0.34)} )^{0.55} = 0.9815 $$

$$ C = \frac{\sum (1-e^{-10\Delta_i})^{0.55} d_i}{0.9815 r_o}$$


## Theoretical Background - Brandt's Method for Locating ICR

When the load orientation is completely horizontal or vertical, the ICR location reside on a line connecting CoG and ICR (this covers most cases). However, when the load orientation isn't 0 or 90 degrees, the search space for ICR is two dimensional and implementation becomes much more challenging. Rather than searching the 2-D plane using brute force or some generic optimization strategy, there exists an iterative method that converges on ICR very quickly. **Brandt's method** is fast and efficient, and it is what AISC uses to construct their design tables.


1. From applied force $(P_x, P_y, M_z)$, calculate load vector orientation ($\theta$). Note [atan2](https://en.wikipedia.org/wiki/Atan2) is a specialized arctan function that returns within the range between -180 to 180 degrees, rather than -90 to 90 degrees. This is to obtain a correct and unambiguous value for the angle theta.

    $$P = \sqrt{P_x^2 + P_y^2}$$

    $$\theta = atan2(\frac{P_y}{P_x})$$

2. Now calculate eccentricity and its x and y components. We can use $e_x$ and $e_y$ to locate the point of applied load (let's call this point P). We know the line P-ICR is perpendicular to the load vector orientation, hence $\theta+90^o$. Note that figures within ICR tables in AISC steel manual is misleading. It seems to imply no vertical eccentricity ($e_y = 0$), yet such an assumption would make the load vector non-orthogonal to the ICR.

    $$e = \frac{M_z}{P}$$

    $$e_x = - e \times cos(\theta + 90^o)$$

    $$e_y = - e \times sin(\theta + 90^o)$$

3. Obtain an initial guess of ICR location per Brandt's method, then calculate distance of line P-ICR ($r_o$)

    $$a_x = V_y \times \frac{I_z}{M_z N_{bolt}}$$

    $$a_y = V_x \times \frac{I_z}{M_z N_{bolt}}$$

    $$x_{ICR} = x_{cg} - a_x$$

    $$y_{ICR} = y_{cg} + a_y$$

    $$r_{ox} = e_x + a_x$$

    $$r_{oy} = e_y - a_y$$

    $$r_{o} = \sqrt{r_{ox}^2 + r_{oy}^2}$$

4. Compute ICR coefficient "C" at assumed location.

    $$C = \frac{ \sum((1 - e^{-10 \Delta_i})^{0.55} d_i)}{r_o}$$
            
5. Next, we need to determine the maximum bolt force ($R_{max}$) at the user-specified load magnitude. This can be done through the moment equilibrium equation; hence why we only need to check force equilibrium at the end. Moment equilibrium is established as a matter of course by enforcing a specific value of $R_{max}$

    $$M_p = P_x r_{oy} - P_y  r_{ox}$$

    $$M_r = R_{max} \times \sum((1 - e^{-10 \Delta_i})^{0.55} d_i)$$

    $$R_{max} = \frac{M_p}{\sum((1 - e^{-10 \Delta_i})^{0.55} d_i)}$$

6. Now that we have $R_{max}$, we can calculate the other bolt forces:

    $$R_i = R_{max} \times \sum((1 - e^{-10 \Delta_i})^{0.55} d_i)$$

7. Now calculate the bolt forces' x and y component to check force equilibrium:

    $$cos(\theta) = d_x / d = sin(\theta+90^o)$$

    $$sin(\theta) = d_y / d = -cos(\theta+90^o)$$

    $$R_x = R_i cos(\theta+90^o) = -R_i \frac{d_y}{d}$$

    $$R_y = R_i sin(\theta+90^o) = R_i \frac{d_x}{d}$$

8. Calculate residual and repeat until a specific tolerance is achieved.

    $$\sum F_x = f_{xx} = P_x - \sum R_{x}$$

    $$\sum F_y = f_{yy} = P_y - \sum R_{y}$$

    $$\mbox{residual} = \sqrt{(f_{xx})^2 + (f_{yy})^2} < tol$$

9. If equilibrium is not achieved, go back to step 4 with the following modifications

    $$a_x = f_{yy} \times \frac{I_z}{M_z N_{bolt}}$$

    $$a_y = f_{xx} \times \frac{I_z}{M_z N_{bolt}}$$

    $$x_{ICR,i} = x_{ICR,i-1} - a_x$$

    $$y_{ICR,i} = x_{ICR,i-1} + a_y$$

10. Once ICR has been located, calculate connection capacity:

    $$P_{capacity} = C \times R_{capacity}$$

    $$DCR = \frac{P}{P_{capacity}} = \frac{R_{max}}{R_{capacity}}$$




## Assumptions and Limitations

* Sign convention follows the right-hand rule. right is +X, top is +Y, counter-clockwise is positive torsion. Note that since we are only concerned with in-plane forces, only the highlighted vectors are relevant.

<div align="center">
  <img src="https://github.com/wcfrobert/ezbolt/blob/master/doc/signconvention.png?raw=true" alt="demo" style="width: 75%;" />
</div>

* Units are in (kip, in) unless otherwise noted
* EZbolt only calculates connection capacity with respect to bolt shear. Other limit states - such as plate rupture, block shear, bearing and tearout - are not considered.



## License

MIT License

Copyright (c) 2023 Robert Wang