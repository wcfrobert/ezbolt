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


# EZBolt

What does this thing do?



## Installation

How to install



## Quick Start

Example scripts



## Usage



## Theoretical Background

```python
Derivation:
            1. Let Mp = applied moment with respect to ECR
                          Mp = P * e_ECR
                          
            2. We know bolt force is linearly proportional to distance from ECR:
                          F_i = K * d_i
                          
            3. Therefore moment contribution from each bolts:
                          M_i = (K * d_i) * d_i
                          
            4. The resisting moment can be found by summing up these bolt moments:
                          Mr = sum(M_i) = K * sum(d_i^2)
                          
            5. Apply moment equilibrium and solve for K:
                          Mp = Mr
                          P * e_ECR = K * sum(d_i^2)
                          K = (P * e_ECR) / sum(d_i^2)
                          
            6. The bolt force is maximum for the bolt furthest from ECR:
                          F_max = K * d_max 
                          F_max = ((P * e_ECR)/sum(d_i^2)) * d_max
                          
            7. Rearrange the equation above, solve for P
                          P = F_max * (sum(d_i^2)) / (e_ECR * d_max)
                          
            8. Let the second term be Ce which is a ratio relating applied load to maximum bolt force
                          P = F_max * Ce
                          Ce = (sum(d_i^2)) / (e_ECR * d_max)
                          
            9. Back calculate the P that would make Fmax = bolt capacity, this is the connection capacity
                          P = F_capacity * Ce = P_capacity
                          
            In the case of pure torsion
                          Mp = torsion = K * sum(d_i^2)
                          K = torsion / sum(d_i^2)
                          F_max = (torsion/sum(d_i^2)) * d_max
                          torsion = F_max * sum(d_i^2) /  d_max
                          Ce = sum(d_i^2) / d_max
                          M_capacity = F_capacity * Ce
```



```python

        Procedure for locating ICR (Brand's Method): 
            1.) calculate ax, ay to get the current guess of ICR location
                        first iteration:
                            fxx = Vx
                            fyy = Vy
                        subsequent iterations:
                            fxx = sum(Fx) - Px     (should equal 0 at ICR)
                            fyy = sum(Fy) - Py     (should equal 0 at ICR)
                        ax_i = fyy * Iz / Mz / N_bolt
                        ay_i = fxx * Iz / Mz / N_bolt
                        x_ICR = x_(i-1) + ax_i
                        y_ICR = y_(i-1) + ay_i
                        ex_ICR = ex - ax_i
                        ey_ICR = ey - ay_i
                        
            2.) Calculate Fmax at the user-specified applied load magnitude
                        Mp = Mr = F_max * sum[(1 - exp(-10*D_i))^(0.55) * di]
                        F_max = Mp / sum[(1 - exp(-10*D_i))^(0.55) * di]
                        
            3.) calculate bolt forces
                        F_i = F_max * (1 - exp(-10*D_i))^(0.55) * di
                        
            4.) calculate the x and y component of bolt force
                        we know the angle from bolt to ICR
                            cos (theta) = dx / d = sin(theta+90)
                            sin (theta) = dy / d = -cos(theta+90)
                        we know the force vector is orthogonal
                            Fx = F_i * cos(theta+90) = -F_i (dy/d)
                            Fy = F_i * sin(theta+90) = F_i (dx/d)
                            
            5.) calculate residual, repeat until residual = 0
                        fxx = sum(Fx) - Vx
                        fyy = sum(Fy) - Vy
                        residual = sqrt(fxx^2 + fyy^2)
                        
            6.) calculate C at this step:
                        C = sum((1 - exp(-10*D_i))^(0.55) * di) / e_ICR
                        
            7.) an alternative procedure is to use unit force, but the above is easier to follow
        
        Derivation:
            Let Mp = applied moment with respect to ICR
                            Mp = P * e_ICR
                          
            Individual bolt force is derived from the following force-deformation relationship
                            F_i = F_max * (1 - exp(-10*D_i))^(0.55)
                          
            We assume the maximum bolt deformation is 0.34 and occurs at furthest bolt from ICR (d_max)
                            D_max = 0.34
                          
            Deformation of other bolts vary linearly from 0 to 0.34 based on its distance from ICR (d_i)
                            D_i = 0.34 * (d_i / d_max)
                          
            Moment contribution from each bolt is:
                            M_i = F_i * d_i
                            M_i = F_max * (1 - exp(-10*D_i))^(0.55) * di
                            Mr = sum(M_i) = F_max * sum[(1 - exp(-10*D_i))^(0.55) * di]

            Moment equilibrium
                            Mp = Mr
                            P * e_ICR = F_max * sum[(1 - exp(-10*D_i))^(0.55) * di]
                            P = F_max * sum((1 - exp(-10*D_i))^(0.55) * di) / e_ICR
                          
            Let the second term be C
                            P = F_max * C 
                            C = sum((1 - exp(-10*D_i))^(0.55) * di) / e_ICR
                          
            Back calculate the P that would make Fmax = bolt capacity, this is the connection capacity
                            P = F_capacity * C = P_capacity
                      
        Notes:
            1.) despite nonlinear bolt force-deformation, the relationship between Fmax and P is linear.
                In other words, if P * 2, then Fmax * 2 and vice versa
            
            2.) e_ICR is sometimes expressed as Mp1 = moment due to normalized unit P
                            Mp1 = (1) e_ICR
                            
            3.) if we sub 0.34 into the exponential function, we get 0.9815. There's a horizontal asymptote at 1
                            F_max2 = F_max1 * (1 - exp(-10*0.34))^(0.55)
                            F_max2 = F_max1 * 0.9815
                We can make a simple adjustment to the coefficient equation:
                            C = sum((1 - exp(-10*D_i))^(0.55) * di) / (e_ICR *0.9815)
                AISC tabluated coefficients did not have this adjustment. This is because the change to final 
                solution is negligible + it is more conservative to have the max bolt force capped to 0.9815Rmax
```








## Assumptions and Limitations

* Units are in (kip, in) unless otherwise noted

## License

MIT License

Copyright (c) 2023 Robert Wang