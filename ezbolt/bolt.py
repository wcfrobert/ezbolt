import math



class Bolt:
    """
    Bolt object definition
    
    Input Arguments:
        tag              an unique ID for each bolt
        x                absolute x coordinate
        y                absolute y coordinate
        
    Attributes:
        dx               x distance from CG to bolt (x - x_cg)
        dy               y distance from CG to bolt (y - y_cg)
        ro               Euclidean distance from CG to bolt
        
        vx_direct        shear demand in x direction due to direct shear
        vy_direct        shear demand in y direction due to direct shear
        vx_torsion       shear demand in x direction due to torsion
        vy_torsion       shear demand in y direction due to torsion
        vx_total         shear demand in x direction total
        vy_total         shear demand in y direction total
        v_resultant      shear demand total vector sum
        v_theta          shear vector angle with respect to horizontal
        
        dx_ICR           x distance from ICR to bolt (x - x_ICR)
        dy_ICR           y distance from ICR to bolt (y - y_ICR)
        ro_ICR           Euclidean distance from ICR to bolt
        theta_ICR        angle of line from bolt to ICR with respect to horizontal
        vx_ICR_unit
        vy_ICR_unit
        v_theta_ICR
        m_ICR_unit       bolt moment contribution
        
    Public Methods:
        None
    """
    def __init__(self, tag, x, y):
        self.tag = tag
        self.x = x
        self.y = y
        self.dx = None
        self.dy = None
        self.ro = None
        
        # elastic method
        self.vx_direct = None
        self.vy_direct = None
        self.vx_torsion = None
        self.vy_torsion = None
        self.vx_total = None
        self.vy_total = None
        self.v_resultant = None
        self.v_theta = None
        self.moment_z = None
        
        # elastic ICR method
        self.dx_elastic = None
        self.dy_elastic = None
        self.ro_elastic = None
        self.vx_ECR = None
        self.vy_ECR = None
        self.v_ECR = None
        self.moment_ECR = None
        self.moment_CG_elastic = None
        
        # instant center of rotation method
        self.dx_ICR = []
        self.dy_ICR = []
        self.ro_ICR = []
        self.force_ICR = []
        self.deformation_ICR = []
        self.moment_ICR = []
        self.moment_CG = []
        self.vx_ICR = []
        self.vy_ICR = []

    def update_geometry(self, x_cg, y_cg):
        """
        Update geometry with respect to bolt group CG
        """
        self.dx = self.x - x_cg
        self.dy = self.y - y_cg
        self.ro = (self.dx**2 + self.dy**2)**(1/2)
        
    def update_geometry_elastic_ICR(self, x_elastic_ICR, y_elastic_ICR):
        """
        Update geometry with respect to elastic center of rotation
        """
        self.dx_elastic = self.x - x_elastic_ICR
        self.dy_elastic = self.y - y_elastic_ICR
        self.ro_elastic = (self.dx_elastic**2 + self.dy_elastic**2)**(1/2)
        
    def update_geometry_ICR(self, x_ICR, y_ICR):
        """
        Update geometry with respect to elastic center of rotation
        """
        self.dx_ICR.append( self.x - x_ICR )
        self.dy_ICR.append( self.y - y_ICR )
        self.ro_ICR.append( (self.dx_ICR[-1]**2 + self.dy_ICR[-1]**2)**(1/2) )
        
    def update_forces_elastic(self, Vx, Vy, N_bolt, torsion, Iz):
        """
        Compute bolt demands using elastic method
        """
        self.vx_direct = -Vx / N_bolt
        self.vy_direct = -Vy / N_bolt
        self.vx_torsion = torsion * self.dy / Iz
        self.vy_torsion = -torsion * self.dx / Iz
        self.vx_total = self.vx_direct + self.vx_torsion
        self.vy_total = self.vy_direct + self.vy_torsion
        self.v_resultant = (self.vx_total**2 + self.vy_total**2)**(1/2)
        self.v_theta = math.atan2(self.vy_total,self.vx_total) * 180 / math.pi
        self.moment_z = - self.vx_total*self.dy + self.vy_total*self.dx
        
    def update_forces_elastic_ICR(self, sumdsquared, Mp, scale_factor):
        """
        Compute bolt forces using elastic method (equivalent elastic center of rotation)
        """
        self.vx_ECR = (Mp * self.dy_elastic / sumdsquared)
        self.vy_ECR = - (Mp * self.dx_elastic / sumdsquared) 
        self.v_ECR = math.sqrt(self.vx_ECR**2 + self.vy_ECR**2) * scale_factor
        theta = math.atan2(self.vy_ECR, self.vx_ECR) * 180 / math.pi
        self.vx_ECR = self.v_ECR * math.cos(math.radians(theta))
        self.vy_ECR = self.v_ECR * math.sin(math.radians(theta))
        self.moment_ECR = - self.vx_ECR*self.dy_elastic + self.vy_ECR*self.dx_elastic
        self.moment_CG_elastic = - self.vx_ECR*self.dy + self.vy_ECR*self.dx
    
    def update_forces_ICR(self, ro_max, Rult, get_moment_only):
        """
        Compute bolt forces using ICR method
        """      
        if get_moment_only:
            D_ULT = 0.34  # in. maximum bolt deformation
            deformation = self.ro_ICR[-1] / ro_max * D_ULT
            force = (1-math.exp(-10*deformation))**(0.55)
            moment = force * self.ro_ICR[-1]
            return moment
        else:
            D_ULT = 0.34  # in. maximum bolt deformation
            deformation = self.ro_ICR[-1] / ro_max * D_ULT
            force = (1-math.exp(-10*deformation))**(0.55) * Rult
            
            # calculate force components in x and y and moment
            theta = math.atan2(self.dy_ICR[-1], self.dx_ICR[-1]) * 180 / math.pi
            vx = force * -math.cos(math.radians(theta+90))
            vy = force * -math.sin(math.radians(theta+90))
            moment_cg = -vx*self.dy + vy*self.dx
            moment_icr = force*self.ro_ICR[-1]
            
            # save results
            self.vx_ICR.append(vx)
            self.vy_ICR.append(vy)
            self.deformation_ICR.append(deformation)
            self.force_ICR.append(force)
            self.moment_ICR.append(moment_icr)
            self.moment_CG.append(moment_cg)
        