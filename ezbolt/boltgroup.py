import ezbolt.bolt
import math
import itertools
import pandas as pd


class BoltGroup:
    """
    BoltGroup object represents a configuration of bolts. It contains attributes such as
    the bolt group's geometric properties and results from three bolt force calculation methods:
        1. Elastic Method - Superposition
        2. Elastic Method - Center of Rotation
        3. Instant Center of Rotation Method
    
    Input Arguments:
        None               
        
    Attributes: 
        (units = kip, in unless otherwise noted)
        
        bolts (list(obj)):              - List of bolt objects
        N_bolt (int):                   - number of bolts
        x_cg (float):                   - bolt group centroid X coordiante
        y_cg (float):                   - bolt group centroid Y coordiante
        Ix (float):                     - moment of inertia about the x-axis
        Iy (float):                     - moment of inertia about the y-axis
        Ixy (float):                    - product of inertia
        Iz (float):                     - moment of inertia about the z-axis (also known as Ip or J)
        results (dict):                 - a dictionary storing all critical calculation results

        Vx (float):                     - applied shear force in X direction
        Vy (float):                     - applied shear force in Y direction
        theta (float):                  - angle of applied force vector with respect to horizontal
        V_resultant (float):            - resultant applied shear force
        torsion (float):                - applied in-plane moment
        ecc (float):                    - eccentricity. Distance between CG and point of applied load
        ecc_x (float):                  - Eccentricity x component
        ecc_y (float):                  - Eccentricity y component
        bolt_capacity (float):          - bolt capacity
        bolt_demand (float):            - bolt demand (elastic method - superposition)

        ecc_ECRx (float):               - eccentricity x component (ECR method)
        ecc_ECRy (float):               - eccentricity y component (ECR method)
        ecc_ECR (float):                - eccentricity. Distance between ECR and point of applied load
        ECR_ax (float):                 - x direction increment from CoG to ECR
        ECR_ay (float):                 - y direction increment from CoG to ECR
        ECR_x (float):                  - x-coordinate for ECR
        ECR_y (float):                  - y-coordinate for ECR
        Ce (float):                     - connection capacity coefficient (ECR method)
        P_demand (float):               - connection demand = V_resultant
        P_capacity (float):             - connection capacity = bolt_capacity * Ce

        ecc_ICRx (list(float)):         - Eccentricity for ICR method along the x-axis.
        ecc_ICRy (list(float)):         - Eccentricity for ICR method along the y-axis.
        ecc_ICR (list(float)):          - Eccentricity for ICR method.
        ICR_ax (list(float)):           - Axial force for ICR method.
        ICR_ay (list(float)):           - Shear force for ICR method.
        ICR_x (list(float)):            - X-coordinate for ICR method.
        ICR_y (list(float)):            - Y-coordinate for ICR method.
        Cu (list(float)):               - Eccentricity coefficient for ICR method.
        P_demand_ICR (float):           - Demand on axial force for ICR method.
        P_capacity_ICR (float):         - Capacity of axial force for ICR method.
        ICR_table (list(dataframe)):    - List containing ICR method table data.

    Public Methods:
        .add_bolt_single()
        .add_bolts()
        .solve()
    """
    def __init__(self):
        # general geometric attributes
        self.bolts = []
        self.N_bolt = 0
        self.x_cg = None
        self.y_cg = None
        self.Ix = None
        self.Iy = None
        self.Ixy = None
        self.Iz = None
        self.results = None
        
        # attributes common to all methods
        self.Vx = None
        self.Vy = None
        self.theta = None
        self.V_resultant = None
        self.torsion = None
        self.ecc = None
        self.ecc_x = None
        self.ecc_y = None
        self.bolt_capacity = None
        self.bolt_demand = None
        
        # ECR method
        self.ecc_ECRx = None
        self.ecc_ECRy = None
        self.ecc_ECR = None
        self.ECR_ax = None
        self.ECR_ay = None
        self.ECR_x = None
        self.ECR_y = None
        self.Ce = None
        self.P_demand = None
        self.P_capacity = None

        # ICR method
        self.ecc_ICRx = []
        self.ecc_ICRy =[]
        self.ecc_ICR = []
        self.ICR_ax = []
        self.ICR_ay = []
        self.ICR_x =[]
        self.ICR_y = []
        self.Cu = []
        self.P_demand_ICR = None
        self.P_capacity_ICR = None
        self.ICR_table = []
    
    def add_bolt_single(self, x, y):
        """
        Add a bolt at user-specified coordinate
        
        Args:
            x ::float           - x coordinate of bolt
            y ::float           - y coordinate of bolt
            
        Returns:
            None
        """
        self.bolts.append(ezbolt.bolt.Bolt(self.N_bolt,x,y))
        self.N_bolt += 1
        self.update_geometric_properties()
        
    def add_bolts(self,xo,yo,width,height,nx,ny,perimeter_only=False):
        """
        Add a retangular array of bolts.
        
        Args:
            xo ::float                          - x coordinate of bottom left corner
            yo ::float                          - y coordinate of bottom left corner
            b ::float                           - width of bolt group
            h ::float                           - height of bolt group
            nx ::float                          - number of bolt in x (evenly spaced)
            ny ::float                          - number of bolt in y (evenly spaced)
            (OPTIONAL) perimeter_only ::bool    - True or False. Have rebar on perimeter only or fill full array
        
        Returns:
            None
        """
        # determine spacing
        sx = 0 if nx==1 else width / (nx-1)
        sy = 0 if ny==1 else height / (ny-1)
        
        # generate bolt coordinate
        xcoord=[]
        ycoord=[]
        xcoord.append(xo)
        ycoord.append(yo)
        if sx != 0:
            for i in range(nx-1):
                xcoord.append(xcoord[-1]+sx)
        if sy !=0:
            for i in range(ny-1):
                ycoord.append(ycoord[-1]+sy)
        bolt_coord = list(itertools.product(xcoord,ycoord))
        
        # remove middle bolts if in perimeter mode
        if perimeter_only:
            x_edge0=xo
            x_edge1=xcoord[-1]
            y_edge0=yo
            y_edge1=ycoord[-1]
            bolt_coord = [e for e in bolt_coord if e[0]==x_edge0 or e[0]==x_edge1 or e[1]==y_edge0 or e[1]==y_edge1]
        
        # add bolts
        for coord in bolt_coord:
            self.add_bolt_single(coord[0],coord[1])
        
    def update_geometric_properties(self):
        """
        Update bolt group geometry properties. Called everytime a bolt is added.
        Recalculate center of gravity, Ix, Iy, Ixy, Iz and update bolt positions
        with respect to the new CoG.
        """
        self.x_cg = sum([b.x / self.N_bolt for b in self.bolts])
        self.y_cg = sum([b.y / self.N_bolt for b in self.bolts])
        self.Iy = sum([(b.x - self.x_cg)**2 for b in self.bolts])
        self.Ix = sum([(b.y - self.y_cg)**2 for b in self.bolts])
        self.Ixy = sum([(b.y - self.y_cg)*(b.x - self.x_cg) for b in self.bolts])
        self.Iz = self.Ix + self.Iy
        for bolt in self.bolts:
            bolt.update_geometry(self.x_cg, self.y_cg)
    
    def solve(self, Vx, Vy, torsion, bolt_capacity=17.9, verbose=True):
        """
        Public method called by user to solve for bolt forces using three methods:
            1. Elastic Method - Superposition
            2. Elastic Method - Center of Rotation
            3. Instant Center of Rotation Method
            
        Args:
            Vx ::float                          - applied horizontal force
            Vy ::float                          - applied vertical force 
            torsion ::float                     - applied in-plane torsion
            (OPTIONAL) bolt_capacity ::float    - bolt capacity in kips. Default = 17.9 kips for A325-N 3/4"
                
        Return:
            return_dict ::dict                  - a dictionary containing calculation results
        """
        # store user input
        self.Vx = Vx
        self.Vy = Vy
        self.torsion = torsion
        self.bolt_capacity = bolt_capacity
        
        # calculate resultant and load vector orientation
        self.V_resultant = (Vx**2 + Vy**2)**(1/2)
        if self.V_resultant == 0 and self.torsion == 0:
            raise RuntimeError("ERROR: No force applied!")
        self.theta = math.atan2(Vy, Vx) * 180 / math.pi
        
        # ezbolt simplifies user input into three load vectors at the centroid of bolt group, namely Vx, Vy, Mz
        # the (x,y) coordinate of applied load (let's call this point P) can reside anywhere along the line 
        # defined by (Vx*ey + Vy*ex = Mz). Therefore, another constraint is added where we let line P-ICR be
        # perpendicular to the applied load vector (i.e. theta + 90).
        # Note that figures within ICR tables in AISC steel manual is misleading. It seems to imply no vertical 
        # eccentricity (e_y = 0). Yet such an assumption will lead to slightly different ICR coefficients than what's tabulated
        self.ecc = 0 if self.V_resultant==0 else -self.torsion / self.V_resultant
        self.ecc_y = self.ecc * math.sin(math.radians(self.theta+90))
        self.ecc_x = self.ecc * math.cos(math.radians(self.theta+90))
        
        # solve with all three methods
        result_elastic = self.solve_elastic()
        result_ECR = self.solve_ECR()
        result_ICR = self.solve_ICR(verbose)
        
        # return a dictionary containing all result dataframes
        self.results = dict()
        self.results["Elastic Method - Superposition"] = result_elastic
        self.results["Elastic Method - Center of Rotation"] = result_ECR
        self.results["Instant Center of Rotation Method"] = result_ICR
        return self.results

    def solve_elastic(self):
        """
        Solve for bolt forces using elastic method and superposition of forces.
        """
        # calculate bolt forces per elastic method
        for bolt in self.bolts:
            bolt.update_forces_elastic(Vx = self.Vx, 
                                       Vy = self.Vy, 
                                       N_bolt = self.N_bolt, 
                                       torsion = self.torsion, 
                                       Iz = self.Iz)
        
        # calculate maximum bolt force
        self.bolt_demand = max([b.v_resultant for b in self.bolts])
        
        # tabulate bolt forces
        result_dict=dict()
        result_dict["bolt_tag"] = [x.tag for x in self.bolts]
        result_dict["x"] = [b.x for b in self.bolts]
        result_dict["y"] = [b.y for b in self.bolts]
        result_dict["dx"] = [x.dx for x in self.bolts]
        result_dict["dy"] = [x.dy for x in self.bolts]
        result_dict["d"] = [x.ro for x in self.bolts]
        result_dict["vx_direct"] = [x.vx_direct for x in self.bolts]
        result_dict["vx_torsion"] = [x.vx_torsion for x in self.bolts]
        result_dict["vy_direct"] = [x.vy_direct for x in self.bolts]
        result_dict["vy_torsion"] = [x.vy_torsion for x in self.bolts]
        result_dict["vx_total"] = [x.vx_total for x in self.bolts]
        result_dict["vy_total"] = [x.vy_total for x in self.bolts]
        result_dict["v_resultant"] = [x.v_resultant for x in self.bolts]
        result_dict["moment"] = [x.moment for x in self.bolts]
        result_dict["theta"] = [x.theta for x in self.bolts]
        df = pd.DataFrame(result_dict)
        sum_row = pd.DataFrame([""] * df.shape[1]).T
        sum_row.columns = df.columns
        sum_row["bolt_tag"] = "Total"
        sum_row["vx_total"] = sum([x.vx_total for x in self.bolts])
        sum_row["vy_total"] = sum([x.vy_total for x in self.bolts])
        sum_row["moment"] = sum([x.moment for x in self.bolts])
        df = pd.concat([df, sum_row], ignore_index=True)
        df = df.set_index("bolt_tag")
        
        # save results to return dictionary
        return_dict = dict()
        return_dict["Bolt Force Table"] = df
        return_dict["Bolt Demand"] = self.bolt_demand
        return_dict["Bolt Capacity"] = self.bolt_capacity
        return_dict["DCR"] = self.bolt_demand/self.bolt_capacity
        return return_dict
    
    def solve_ECR(self):
        """
        Solve for bolt forces using elastic center of rotation (ECR) method.
        """
        if self.torsion == 0:
            return "Method not applicable when torsion = 0"
        else:
            # calculate location of ECR which is deterministic
            self.ECR_ax = self.Vy * self.Iz / self.torsion / self.N_bolt
            self.ECR_ay = self.Vx * self.Iz / self.torsion / self.N_bolt
            self.ECR_x = self.x_cg - self.ECR_ax
            self.ECR_y = self.y_cg + self.ECR_ay
            
            # calculate new eccentricity with respect to ECR
            self.ecc_ECRx = self.ecc_x + self.ECR_ax
            self.ecc_ECRy = self.ecc_y - self.ECR_ay
            self.ecc_ECR = math.sqrt(self.ecc_ECRx**2 + self.ecc_ECRy**2)
            
            # calculate bolt distance to ECR
            for bolt in self.bolts:
                bolt.update_geometry_ECR(self.ECR_x, self.ECR_y)
            
            # calculate elastic center of rotation coefficient
            dmax = max([b.ro_ECR for b in self.bolts])
            sumdsquared = sum([b.ro_ECR**2 for b in self.bolts])
            if self.V_resultant == 0:
                self.Ce = sumdsquared / (dmax)
            else:
                self.Ce = sumdsquared / (self.ecc_ECR * dmax)

            # calculate bolt force 
            if self.V_resultant == 0:
                K = 1 / sumdsquared * self.torsion
            else:
                if self.torsion < 0:
                    K = - self.ecc_ECR / sumdsquared * self.V_resultant
                elif self.torsion > 0:
                    K = self.ecc_ECR / sumdsquared * self.V_resultant
                
            for bolt in self.bolts:
                bolt.update_forces_ECR(K)
                
            # calculate final connection capacity and demand
            self.P_capacity = self.Ce * self.bolt_capacity
            self.P_demand = self.V_resultant if self.ecc!= 0 else self.torsion
            
            # tabulate bolt forces
            result_dict=dict()
            result_dict["bolt_tag"] = [x.tag for x in self.bolts]
            result_dict["x"] = [b.x for b in self.bolts]
            result_dict["y"] = [b.y for b in self.bolts]
            result_dict["dx_ECR"] = [x.dx_ECR for x in self.bolts]
            result_dict["dy_ECR"] = [x.dy_ECR for x in self.bolts]
            result_dict["d_ECR"] = [x.ro_ECR for x in self.bolts]
            result_dict["vx"] = [x.vx_ECR for x in self.bolts]
            result_dict["vy"] = [x.vy_ECR for x in self.bolts]
            result_dict["v_resultant"] = [x.vtotal_ECR for x in self.bolts]
            result_dict["moment_CG"] = [x.moment_ECG for x in self.bolts]
            result_dict["moment_ECR"] = [x.moment_ECR for x in self.bolts]
            df = pd.DataFrame.from_dict(result_dict)
            sum_row = pd.DataFrame([""] * df.shape[1]).T
            sum_row.columns = df.columns
            sum_row["bolt_tag"] = "Total"
            sum_row["vx"] = sum([x.vx_ECR for x in self.bolts])
            sum_row["vy"] = sum([x.vy_ECR for x in self.bolts])
            sum_row["moment_CG"] = sum([x.moment_ECG for x in self.bolts])
            sum_row["moment_ECR"] = sum([x.moment_ECR for x in self.bolts])
            df = pd.concat([df, sum_row], ignore_index=True)
            df = df.set_index("bolt_tag")
            
            # save results to return dictionary
            return_dict= dict()
            return_dict["Bolt Force Table"] = df
            return_dict["Center of Rotation"] = [self.ECR_x, self.ECR_y]
            return_dict["Ce"] = self.Ce
            return_dict["Bolt Capacity"] = self.bolt_capacity
            return_dict["Connection Capacity"] = self.P_capacity
            return_dict["Connection Demand"] = self.P_demand
            return_dict["DCR"] = self.P_demand / self.P_capacity
        return return_dict
    
    def solve_ICR(self, verbose):
        """
        Solve for bolt forces using ICR method.
        """
        # possibility #1: No torsion. ICR method is not applicable
        if self.torsion == 0:
            return "ICR Method not applicable when torsion = 0"
        
        # possibility #2: Typical applied load. Iteration needed to find ICR
        elif self.V_resultant !=0:
            if verbose:
                print("Searching for location of ICR using Brandt's method...")
            tol = 0.01
            N_iter = 0
            max_iter = 1000
            fxx = []
            fyy = []
            residual = []
            while True:
                if N_iter == 0:
                    ax = self.Vy * self.Iz / self.torsion / self.N_bolt
                    ay = self.Vx * self.Iz / self.torsion / self.N_bolt
                    ICR_x = self.x_cg - ax
                    ICR_y = self.y_cg + ay
                    ICR_ex = self.ecc_x + ax
                    ICR_ey = self.ecc_y - ay
                else:
                    # I reduced ax, ay by a factor of 5 to ensure convergence with smaller step
                    # some configurations of load and bolts leads to infinite cycles and no convergence
                    ax = fyy[-1] * self.Iz / self.torsion / self.N_bolt/2
                    ay = fxx[-1] * self.Iz / self.torsion / self.N_bolt/2
                    ICR_x = self.ICR_x[-1] - ax
                    ICR_y = self.ICR_y[-1] + ay
                    ICR_ex = self.ecc_ICRx[-1] + ax
                    ICR_ey = self.ecc_ICRy[-1] - ay
                
                self.ICR_x.append(ICR_x)
                self.ICR_y.append(ICR_y)
                self.ICR_ax.append(ax)
                self.ICR_ay.append(ay)
                self.ecc_ICRx.append(ICR_ex)
                self.ecc_ICRy.append(ICR_ey)
                self.ecc_ICR.append(math.sqrt(self.ecc_ICRx[-1]**2 + self.ecc_ICRy[-1]**2))
                
                # update bolt geometry with respect to assumed ICR
                for bolt in self.bolts:
                    bolt.update_geometry_ICR(self.ICR_x[-1], self.ICR_y[-1])
                
                # compute ICR coefficient at assumed ICR
                ro_max = max([b.ro_ICR[-1] for b in self.bolts])
                Mi1 = [b.get_moment_ICR(ro_max) for b in self.bolts]
                Mp1 = math.sqrt(self.ecc_ICRx[-1]**2 + self.ecc_ICRy[-1]**2)
                ICR_Cu = abs(sum(Mi1) / Mp1)
                self.Cu.append(ICR_Cu)
                
                # compute Fmax at specified force magnitude
                Mp = self.Vx * self.ecc_ICRy[-1] - self.Vy * self.ecc_ICRx[-1]
                F_max = Mp / sum(Mi1)
                
                # compute bolt forces
                for bolt in self.bolts:
                    bolt.update_forces_ICR(ro_max, F_max)
                    
                # check equilibrium
                sumFx = sum([b.vx_ICR[-1] for b in self.bolts])
                sumFy = sum([b.vy_ICR[-1] for b in self.bolts])
                fxx.append(sumFx + self.Vx)
                fyy.append(sumFy + self.Vy)
                residual.append(math.sqrt(fxx[-1]**2 + fyy[-1]**2))
                if verbose:
                    print("\t Trial {}: ({:.2f}, {:.2f}). fxx = {:.2f}, fyy = {:.2f}".format(N_iter+1, self.ICR_x[-1], self.ICR_y[-1], fxx[-1], fyy[-1]))

                # tabulate bolt forces at each step
                result_dict=dict()
                result_dict["bolt_tag"] = [x.tag for x in self.bolts]
                result_dict["x"] = [b.x for b in self.bolts]
                result_dict["y"] = [b.y for b in self.bolts]
                result_dict["dx_ICR"] = [x.dx_ICR[-1] for x in self.bolts]
                result_dict["dy_ICR"] = [x.dy_ICR[-1] for x in self.bolts]
                result_dict["ro_ICR"] = [x.ro_ICR[-1] for x in self.bolts]
                result_dict["deformation"] = [x.deformation_ICR[-1] for x in self.bolts]
                result_dict["force"] = [x.force_ICR[-1] for x in self.bolts]
                result_dict["moment_ICR"] = [x.moment_ICR[-1] for x in self.bolts]
                result_dict["moment_CG"] = [x.moment_ICG[-1] for x in self.bolts]
                result_dict["Vx"] = [x.vx_ICR[-1] for x in self.bolts]
                result_dict["Vy"] = [x.vy_ICR[-1] for x in self.bolts]
                df = pd.DataFrame.from_dict(result_dict)
                sum_row = pd.DataFrame([""] * df.shape[1]).T
                sum_row.columns = df.columns
                sum_row["bolt_tag"] = "Total"
                sum_row["Vx"] = sum([x.vx_ICR[-1] for x in self.bolts])
                sum_row["Vy"] = sum([x.vy_ICR[-1] for x in self.bolts])
                sum_row["moment_CG"] = sum([x.moment_ICG[-1] for x in self.bolts])
                sum_row["moment_ICR"] = sum([x.moment_ICR[-1] for x in self.bolts])
                df = pd.concat([df, sum_row], ignore_index=True)
                df = df.set_index("bolt_tag")
                self.ICR_table.append(df)

                # end loop if equilibrium is obtained
                if residual[-1] < tol:
                    if verbose:
                        print("\t Success! ICR found at ({:.2f}, {:.2f})".format(self.ICR_x[-1], self.ICR_y[-1]))
                    self.P_demand_ICR = self.V_resultant
                    self.P_capacity_ICR = self.Cu[-1] * self.bolt_capacity
                    
                    return_dict = dict()
                    return_dict["Bolt Force Tables"] = self.ICR_table
                    return_dict["ICR"] = list(zip(self.ICR_x, self.ICR_y))
                    return_dict["Cu"] = self.Cu
                    return_dict["Connection Demand"] = self.P_demand_ICR
                    return_dict["Connection Capacity"] = self.P_capacity_ICR
                    return_dict["DCR"] = self.P_demand_ICR/self.P_capacity_ICR
                    return return_dict
                
                # end loop if maximum number of iterations exceeded
                N_iter +=1
                if N_iter > max_iter:
                    print(f"nbolt = {self.N_bolt}\nVx = {self.Vx}\nVy = {self.Vy}\nMz = {self.torsion}\n")
                    raise RuntimeError("could not converge on ICR after 1000 iterations. Ending solver.")
         
                
         
        # possibility #3: Pure torsion. ICR is located at centroid
        elif self.V_resultant == 0:
            self.ICR_x = [self.x_cg]
            self.ICR_y = [self.y_cg]
            print("Special Case: Pure Torsion. ICR at ({:.2f}, {:.2f})".format(self.x_cg, self.y_cg))
            
            # update bolt geometry with respect to assumed ICR
            for bolt in self.bolts:
                bolt.update_geometry_ICR(self.ICR_x[-1], self.ICR_y[-1])
            
            # compute ICR coefficient at assumed ICR
            ro_max = max([b.ro_ICR[-1] for b in self.bolts])
            Mi1 = [b.get_moment_ICR(ro_max) for b in self.bolts]
            Mp1 = 1
            ICR_Cu = [abs(sum(Mi1) / Mp1)]
            self.Cu = ICR_Cu
            
            # compute Fmax at specified force magnitude
            Mp = -self.torsion
            F_max = Mp / sum(Mi1)
            
            # compute bolt forces
            for bolt in self.bolts:
                bolt.update_forces_ICR(ro_max, F_max)
                
            # tabulate bolt forces
            result_dict=dict()
            result_dict["bolt_tag"] = [x.tag for x in self.bolts]
            result_dict["x"] = [b.x for b in self.bolts]
            result_dict["y"] = [b.y for b in self.bolts]
            result_dict["dx_ICR"] = [x.dx_ICR[-1] for x in self.bolts]
            result_dict["dy_ICR"] = [x.dy_ICR[-1] for x in self.bolts]
            result_dict["ro_ICR"] = [x.ro_ICR[-1] for x in self.bolts]
            result_dict["deformation"] = [x.deformation_ICR[-1] for x in self.bolts]
            result_dict["force"] = [x.force_ICR[-1] for x in self.bolts]
            result_dict["moment_ICR"] = [x.moment_ICR[-1] for x in self.bolts]
            result_dict["moment_CG"] = [x.moment_ICG[-1] for x in self.bolts]
            result_dict["Vx"] = [x.vx_ICR[-1] for x in self.bolts]
            result_dict["Vy"] = [x.vy_ICR[-1] for x in self.bolts]
            df = pd.DataFrame.from_dict(result_dict)
            sum_row = pd.DataFrame([""] * df.shape[1]).T
            sum_row.columns = df.columns
            sum_row["bolt_tag"] = "Total"
            sum_row["Vx"] = sum([x.vx_ICR[-1] for x in self.bolts])
            sum_row["Vy"] = sum([x.vy_ICR[-1] for x in self.bolts])
            sum_row["moment_CG"] = sum([x.moment_ICG[-1] for x in self.bolts])
            sum_row["moment_ICR"] = sum([x.moment_ICR[-1] for x in self.bolts])
            df = pd.concat([df, sum_row], ignore_index=True)
            df = df.set_index("bolt_tag")
            self.ICR_table.append(df)
            
            # gather return dict
            self.P_demand_ICR = self.torsion
            self.P_capacity_ICR = self.Cu[-1] * self.bolt_capacity
            
            return_dict = dict()
            return_dict["Bolt Force Tables"] = self.ICR_table
            return_dict["ICR"] = list(zip(self.ICR_x, self.ICR_y))
            return_dict["Cu"] = self.Cu
            return_dict["Connection Demand"] = self.P_demand_ICR
            return_dict["Connection Capacity"] = self.P_capacity_ICR
            return_dict["DCR"] = self.P_demand_ICR/self.P_capacity_ICR
            return return_dict
            