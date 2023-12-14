import ezbolt.bolt
import math
import itertools
import pandas as pd
import numpy as np

class BoltGroup:
    """
    Bolt group object definition
    
    Input Arguments:
        None               
        
    Attributes:
        bolts
        N_bolts
        x_cg
        y_cg
        Ix
        Iy
        Iz
        rn
        
        Vx
        Vy
        V_resultant
        torsion
        ecc
        theta
        
        ICR_xi
        ICR_yi
        ICR_Ci
        sumFx
        sumFy
        sumMz
        
    Public Methods:
        add_bolt(x, y)
        solve(Vx, Vy, torsion, rn)
        preview()
        plot_forces()
        plot_ICR(xlim, ylim, du)
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
        
        # elastic method
        self.Vx = None
        self.Vy = None
        self.V_resultant = None
        self.torsion = None
        self.ecc = None
        self.theta = None
        self.Vcapacity = None
        self.Vdemand = None
        self.result_elastic1 = None
        
        # elastic ICR method
        self.elastic_ax = None
        self.elastic_ay = None
        self.elastic_ICRx = None
        self.elastic_ICRy = None
        self.df_results_elastic2 = None
        
        # instant center of rotation method
        self.ICR_ax = []
        self.ICR_ay = []
        self.ICR_x = []
        self.ICR_y = []
        self.ICR_coeff = []
        self.ICR_table = []
        self.Mp = []
    
    def add_bolt_single(self, x, y):
        """
        Add a bolt at user-specified coordinate
        """
        self.bolts.append(ezbolt.bolt.Bolt(self.N_bolt,x,y))
        self.N_bolt += 1
        
    def add_bolts(self,xo,yo,width,height,nx,ny,perimeter_only=False):
        """
        Add a retangular array of bolts
            xo                  x coordinate of bottom left corner
            yo                  y coordinate of bottom left corner
            b                   width of bolt group
            h                   height of bolt group
            nx                  number of bolt in x (evenly spaced)
            ny                  number of bolt in y (evenly spaced)
            perimeter_only      True or False. Have rebar on perimeter only or fill full array
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
        Update bolt group geometry properties
        """
        self.x_cg = sum([b.x / self.N_bolt for b in self.bolts])
        self.y_cg = sum([b.y / self.N_bolt for b in self.bolts])
        self.Ix = sum([(b.x - self.x_cg)**2 for b in self.bolts])
        self.Iy = sum([(b.y - self.y_cg)**2 for b in self.bolts])
        self.Ixy = sum([(b.y - self.y_cg)*(b.x - self.x_cg) for b in self.bolts])
        self.Iz = self.Ix + self.Iy
        for bolt in self.bolts:
            bolt.update_geometry(self.x_cg, self.y_cg)
          
    def solve(self, Vx, Vy, torsion, bolt_capacity=17.9, verbose=True):
        """
        Solve for bolt shear and tension demand
        """
        # store user input
        self.update_geometric_properties()
        self.Vx = Vx
        self.Vy = Vy
        self.torsion = torsion
        self.Vcapacity = bolt_capacity  # default = 17.9 kips for 3/4" A325N bolt in single shear
        self.verbose = verbose
        
        # calculate resultant and load vector orientation
        self.V_resultant = (self.Vx**2 + self.Vy**2)**(1/2)
        self.theta = math.atan2(self.Vy, self.Vx) * 180 / math.pi
        self.ecc = 0 if self.V_resultant==0 else self.torsion / self.V_resultant
        
        # print information about the bolt group
        if self.verbose:
            print("Bolt Group Definition")
            print("\t N_bolts = {} bolts".format(self.N_bolt))
            print("\t Centroid: ({:.2f} in, {:.2f} in)".format(self.x_cg, self.y_cg))
            print("\t Ix = {:.2f} in4".format(self.Ix))
            print("\t Iy = {:.2f} in4".format(self.Iy))
            print("\t J = {:.2f} in4".format(self.Iz))
            print("\nApplied Loading Definition")
            print("\t Vx = {:.1f} kips".format(self.Vx))
            print("\t Vy = {:.1f} kips".format(self.Vy))
            print("\t Mz = {:.1f} k.in".format(self.torsion))
            print("\t eccentricity = {:.1f} in".format(abs(self.ecc)))
            print("\t load angle = {:.1f} deg".format(self.theta))
            
        # solve with al three methods
        self.df_result_elastic1 = self.solve_elastic()
        self.df_result_elastic2 = self.solve_elastic_ICR()
        self.df_result_ICR = self.solve_ICR()
        
        # return a dictionary containing all result dataframes
        all_results = dict()
        all_results["elastic"] = self.df_result_elastic1
        all_results["elastic ICR"] = self.df_result_elastic2
        all_results["ICR"] = self.df_result_ICR
        return all_results
        
    def solve_elastic(self):
        """
        Solve for bolt forces using elastic method (superposition of forces)
        """
        # calculate bolt forces
        for bolt in self.bolts:
            bolt.update_forces_elastic(Vx=self.Vx, Vy=self.Vy, N_bolt=self.N_bolt, torsion=self.torsion, Iz=self.Iz)
        
        # write out results to console
        self.Vdemand = max([b.v_resultant for b in self.bolts])
        if self.verbose:
            print("\nMethod 1 - Elastic method via superposition:")
            print("\t Vmax = {:.2f} kips".format(self.Vdemand))
            print("\t Capacity (one bolt) = {:.2f} kips".format(self.Vcapacity))
            print("\t Demand (one bolt) = {:.2f} kips".format(self.Vdemand))
            print("\t DCR = {:.2f}".format(self.Vdemand/self.Vcapacity))
        
        # summarize results in a dataframe
        result_dict=dict()
        result_dict["bolt_tag"] = [x.tag for x in self.bolts]
        result_dict["x"] = [b.x for b in self.bolts]
        result_dict["y"] = [b.y for b in self.bolts]
        result_dict["dx"] = [x.dx for x in self.bolts]
        result_dict["dy"] = [x.dy for x in self.bolts]
        result_dict["ro"] = [x.ro for x in self.bolts]
        result_dict["vx_direct"] = [x.vx_direct for x in self.bolts]
        result_dict["vx_torsion"] = [x.vx_torsion for x in self.bolts]
        result_dict["vy_direct"] = [x.vy_direct for x in self.bolts]
        result_dict["vy_torsion"] = [x.vy_torsion for x in self.bolts]
        result_dict["vx_total"] = [x.vx_total for x in self.bolts]
        result_dict["vy_total"] = [x.vy_total for x in self.bolts]
        result_dict["v_resultant"] = [x.v_resultant for x in self.bolts]
        result_dict["moment"] = [x.moment_z for x in self.bolts]
        result_dict["theta"] = [x.v_theta for x in self.bolts]
        df = pd.DataFrame.from_dict(result_dict)
        
        # add a summation row
        empty_row = list(np.full(df.shape[1], None))
        empty_row[0] = "Sum"
        empty_row[10] = sum(result_dict["vx_total"])
        empty_row[11] = sum(result_dict["vy_total"])
        empty_row[13] = sum(result_dict["moment"])
        headers = df.columns
        sum_row = pd.DataFrame(empty_row, index=headers).T
        df = pd.concat([df, sum_row.iloc[[0]]], ignore_index=True)
        df = df.set_index("bolt_tag")
        return df
    
    def solve_elastic_ICR(self):
        """
        Solve for bolt forces using elastic method (equivalent center of rotation). See Brandt paper.
        """
        if self.torsion == 0:
            if self.verbose:
                print("\nMethod 2 - Elastic method via equivalent center of rotation:")
                print("\t Applied torsion = 0")
                print("\t This method is not applicable as center of rotation does not exist when torsion = 0")
                return "not applicable"
        else:
            # determine location of elastic ICR
            self.elastic_ax = -self.Vy * self.Iz / self.torsion / self.N_bolt
            self.elastic_ay = self.Vx * self.Iz / self.torsion / self.N_bolt
            self.elastic_ICRx = self.x_cg + self.elastic_ax
            self.elastic_ICRy = self.y_cg + self.elastic_ay
            
            # calculate bolt distance to elastic ICR
            for bolt in self.bolts:
                bolt.update_geometry_elastic_ICR(self.elastic_ICRx, self.elastic_ICRy)
            
            # calculate elastic bolt force coefficient
            sumdsquared = sum([b.ro_elastic**2 for b in self.bolts])
            dmax = max([b.ro_elastic for b in self.bolts])
            ecc_ECRx = -self.ecc * math.cos(math.radians(self.theta+90)) - self.elastic_ax
            ecc_ECRy = -self.ecc * math.sin(math.radians(self.theta+90)) - self.elastic_ay
            ecc_ECR = math.sqrt(ecc_ECRx**2 + ecc_ECRy**2)

            # special case of pure torsion
            if self.ecc==0:
                Mp = 1
                Ce = self.Vcapacity*(sumdsquared / dmax / Mp)/self.torsion
                Pmax = Ce * self.torsion
                
                # calculate bolt forces
                for bolt in self.bolts:
                    bolt.update_forces_elastic_ICR(sumdsquared, Mp, self.torsion)
                
                # print result to console
                if self.verbose:
                    print("\nMethod 2 - Elastic method via center of rotation:")
                    print("\t SPECIAL CASE: Pure Torsion")
                    print("\t Elastic center of rotation found at ({:.2f} in, {:.2f} in)".format(self.elastic_ICRx, self.elastic_ICRy))
                    print("\t Ce is equal to {:.2f}; Rult is equal to {:.2f} k.in".format(Ce, self.Vcapacity))
                    print("\t Capacity (overall connection) = Ce*Rult = {:.2f} k.in".format(Pmax))
                    print("\t Demand (overall connection) = {:.2f} k.in".format(self.torsion))
                    print("\t DCR = {:.2f}".format(self.torsion/Pmax))
                    
            # typical case with torsion + applied force
            else:
                Mp = 1 * ecc_ECR
                Ce = 1 / (Mp * dmax / sumdsquared)
                Pmax = Ce * self.Vcapacity
            
                # calculate bolt forces
                for bolt in self.bolts:
                    bolt.update_forces_elastic_ICR(sumdsquared, Mp, self.V_resultant)
                
                # print result to console
                if self.verbose:
                    print("\nMethod 2 - Elastic method with center of rotation:")
                    print("\t Elastic center of rotation found at ({:.2f} in, {:.2f} in)".format(self.elastic_ICRx, self.elastic_ICRy))
                    print("\t Ce = {:.2f}".format(Ce))
                    print("\t Rult = {:.2f} kips".format(self.Vcapacity))
                    print("\t Capacity (overall connection) = Ce*Rult = {:.2f} kips".format(Pmax))
                    print("\t Demand (overall connection) = {:.2f} kips".format(self.V_resultant))
                    print("\t DCR = {:.2f}".format(self.V_resultant/Pmax))
                
            # save results to dataframe
            result_dict=dict()
            result_dict["bolt_tag"] = [x.tag for x in self.bolts]
            result_dict["x"] = [b.x for b in self.bolts]
            result_dict["y"] = [b.y for b in self.bolts]
            result_dict["dx_ECR"] = [x.dx_elastic for x in self.bolts]
            result_dict["dy_ECR"] = [x.dy_elastic for x in self.bolts]
            result_dict["ro_ECR"] = [x.ro_elastic for x in self.bolts]
            result_dict["vx"] = [x.vx_ECR for x in self.bolts]
            result_dict["vy"] = [x.vy_ECR for x in self.bolts]
            result_dict["v_resultant"] = [x.v_ECR for x in self.bolts]
            result_dict["moment_CG"] = [x.moment_CG_elastic for x in self.bolts]
            result_dict["moment_ECR"] = [x.moment_ECR for x in self.bolts]
            df = pd.DataFrame.from_dict(result_dict)
            
            # add a summation row
            empty_row = list(np.full(df.shape[1], None))
            empty_row[0] = "Sum"
            empty_row[6] = sum(result_dict["vx"])
            empty_row[7] = sum(result_dict["vy"])
            empty_row[9] = sum(result_dict["moment_CG"])
            empty_row[10] = sum(result_dict["moment_ECR"])
            headers = df.columns
            sum_row = pd.DataFrame(empty_row, index=headers).T
            df = pd.concat([df, sum_row.iloc[[0]]], ignore_index=True)
            df = df.set_index("bolt_tag")
            return df
    
    def solve_ICR(self):
        """
        Solve for bolt forces using ICR method. See Brandt's Method paper
        """
        # Possibility 1: No torsion. ICR method is not applicable
        if self.torsion == 0:
            if self.verbose:
                print("\nMethod 3 - ICR method:")
                print("\t Applied torsion = 0")
                print("\t This method is not applicable as center of rotation does not exist when torsion = 0")
                return "not applicable"
        
        # Possibility 2: Pure torsion. ICR is located at bolt group CoG
        else:
            if self.ecc==0:
                if self.verbose:
                    print("\nMethod 3 - ICR method:")
                    print("\t SPECIAL CASE: Pure Torsion")
                    print("\t ICR located at bolt group CG: ({:.2f}, {:.2f})".format(self.x_cg, self.y_cg))
                self.ICR_x.append(self.x_cg)
                self.ICR_y.append(self.y_cg)
                result_dict = dict()
                return result_dict
                
        # Possibility 3: Typical applied force + torsion
            else:
                if self.verbose:
                    print("\nMethod 3 - ICR method:")
                    print("\t Searching location of ICR with Brandt's Method':")
                
                # convert to unit force
                Px_unit = math.cos(math.radians(self.theta))
                Py_unit = math.sin(math.radians(self.theta))
                print(Px_unit,Py_unit)
                
                # start iteration to search for ICR
                residual = 999
                tol = 0.00001
                N_iter = 0
                max_iter = 50
                fxx = []
                fyy = []
                residual = []
                ecc_ICRx = []
                ecc_ICRy = []
                while True:
                    # increment to next ICR location
                    if N_iter == 0:
                        ax = -Py_unit * self.Iz / self.ecc / self.N_bolt
                        ay = Px_unit * self.Iz / self.ecc / self.N_bolt
                        ICR_x = self.x_cg + ax
                        ICR_y = self.y_cg + ay
                    else:
                        ax = -fyy[-1] * self.Iz / self.ecc / self.N_bolt
                        ay = fxx[-1] * self.Iz / self.ecc / self.N_bolt
                        ICR_x = self.ICR_x[-1] + ax
                        ICR_y = self.ICR_y[-1] + ay
                    
                    # calculate Mp, ecc with respect to new ICR
                    if N_iter == 0:
                        ecc_ICRx = self.ecc * -math.cos(math.radians(self.theta+90)) - ax
                        ecc_ICRy = self.ecc * -math.sin(math.radians(self.theta+90)) - ay
                    else:
                        ecc_ICRx += ax
                        ecc_ICRy += ay
                    ecc_ICR = math.sqrt(ecc_ICRx**2 + ecc_ICRy**2)
                    Mp = 1 * ecc_ICR
                    
                    # update bolt geometry with respect to assumed ICR
                    for bolt in self.bolts:
                        bolt.update_geometry_ICR(ICR_x, ICR_y)
                    
                    # calculate sumMi based on new ICR
                    ro_max = max([b.ro_ICR[-1] for b in self.bolts])
                    Mi = []
                    for bolt in self.bolts:
                        Mi.append(bolt.update_forces_ICR(ro_max, 1.0, get_moment_only=True))
                    
                    # calculate ICR coefficient and Rult
                    Cu = sum(Mi) / Mp
                    
                    # check equilibrium
                    Rult_unit = 1 / Cu
                    for bolt in self.bolts:
                        bolt.update_forces_ICR(ro_max, Rult_unit, get_moment_only=False)
                    
                    sumFx = sum([b.vx_ICR[-1] for b in self.bolts])
                    sumFy = sum([b.vy_ICR[-1] for b in self.bolts])
                    fxx.append(sumFx + Px_unit)
                    fyy.append(sumFy + Py_unit)
                    residual.append(math.sqrt(fxx[-1]**2 + fyy[-1]**2))
                    
                    if self.verbose:
                        print("\t\t Trial {}: ({:.2f}, {:.2f}). fxx = {:.2f}, fyy = {:.2f}".format(N_iter+1, ICR_x, ICR_y, fxx[-1], fyy[-1]))
                    
                    # save results
                    self.ICR_coeff.append(Cu)
                    self.ICR_ax.append(ax)
                    self.ICR_ay.append(ay)
                    self.ICR_x.append(ICR_x)
                    self.ICR_y.append(ICR_y)
                    self.Mp.append(Mp)
                    
                    # create tabular summary
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
                    result_dict["moment_CG"] = [x.moment_CG[-1] for x in self.bolts]
                    result_dict["Vx"] = [x.vx_ICR[-1] for x in self.bolts]
                    result_dict["Vy"] = [x.vy_ICR[-1] for x in self.bolts]
                    df = pd.DataFrame.from_dict(result_dict)
                    
                    # add a summation row
                    empty_row = list(np.full(df.shape[1], None))
                    empty_row[0] = "Sum"
                    empty_row[10] = sum(result_dict["Vx"])
                    empty_row[11] = sum(result_dict["Vy"])
                    empty_row[8] = sum(result_dict["moment_ICR"])
                    empty_row[9] = sum(result_dict["moment_CG"])
                    headers = df.columns
                    sum_row = pd.DataFrame(empty_row, index=headers).T
                    df = pd.concat([df, sum_row.iloc[[0]]], ignore_index=True)
                    df = df.set_index("bolt_tag")
                    self.ICR_table.append(df)
                    
                    # end loop if equilibrium is obtained
                    if residual[-1] < tol:
                        if self.verbose:
                            print("\t Success. ICR found at ({:.2f}, {:.2f})".format(self.ICR_x[-1], self.ICR_y[-1]))
                        found_ICR = True
                        break
                    
                    # end loop if maximum number of iterations exceeded
                    N_iter +=1
                    if N_iter > max_iter:
                        print("\t WARNING: could not converge on ICR after 100 iterations. Ending solver.")
                        found_ICR = False
                        break
            
                # once ICR has been found, update forces and summarize
                if found_ICR:
                    return result_dict
                else:
                    return "ICR not found. Could not obtain solution"
        