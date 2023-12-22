import math


class Bolt:
    """
    Bolt object is used to represent individual bolts within a bolt group.
    They are created through the .add_bolts() method in the BoltGroup class.
    
    Input Arguments:
        tag ::str                       - unique ID for each bolt
        x ::float                       - x coordinate
        y ::float                       - y coordinate
        
    Attributes:
        dx ::float                      - x distance from CG to bolt (x - x_cg)
        dy ::float                      - y distance from CG to bolt (y - y_cg)
        ro ::float                      - Euclidean distance from CG to bolt
        
        vx_direct ::float               - shear demand in x direction due to direct shear
        vy_direct ::float               - shear demand in y direction due to direct shear
        vx_torsion ::float              - shear demand in x direction due to torsion
        vy_torsion ::float              - shear demand in y direction due to torsion
        vx_total ::float                - shear demand in x direction total
        vy_total ::float                - shear demand in y direction total
        v_resultant ::float             - shear demand total vector sum
        theta ::float                   - force vector angle with respect to horizontal in degrees
        moment ::float                  - resisting moment contribution = v_resultant * ro
        
        dx_ECR ::float                  - x distance from ECR to bolt (x - x_ECR)
        dy_ECR ::float                  - y distance from ECR to bolt (y - y_ECR)
        ro_ECR ::float                  - Euclidean distance from ECR to bolt
        vx_ECR ::float                  - shear demand in x direction from ECR method
        vy_ECR ::float                  - shear demand in y direction from ECR method
        theta_ECR ::float               - force vector angle with respect to horizontal in degrees from ECR method
        vtotal_ECR ::float              - shear demand total vector sum from ECR method
        moment_ECR ::float              - resisting moment contribution with respect to CoG = v_resultant * ro
        moment_ECG ::float              - resisting moment contribution with respect to ECR
        
        dx_ICR ::list(float)            - x distance from ICR to bolt (x - x_ICR)
        dy_ICR ::list(float)            - y distance from ICR to bolt (y - y_ICR)
        ro_ICR ::list(float)            - Euclidean distance from ICR to bolt
        force_ICR ::list(float)         - total shear based on ICR force-deformation relationship
        deformation_ICR ::list(float)   - bolt deformation varying linearly from ICR
        moment_ICR ::list(float)        - resisting moment contribution with respect to ICR
        moment_ICG ::list(float)        - resisting moment contribution with respect to CoG = v_resultant * ro
        vx_ICR ::list(float)            - shear demand in x direction from ICR method
        vy_ICR ::list(float)            - shear demand in y direction from ICR method
        theta_ICR ::list(float)         - force vector angle with respect to horizontal in degrees from ICR method
        
    Public Methods:
        .update_geometry()
        .update_geometry_ECR()
        .update_geometry_ICR()
        .update_forces_elastic()
        .update_forces_ECR()
        .update_forces_ICR()
        .get_moment_ICR()
    """
    def __init__(self, tag, x, y):
        # general attributes
        self.tag = tag
        self.x = x
        self.y = y
        self.dx = None
        self.dy = None
        self.ro = None
        
        # attributes for elastic method
        self.vx_direct = None
        self.vy_direct = None
        self.vx_torsion = None
        self.vy_torsion = None
        self.vx_total = None
        self.vy_total = None
        self.v_resultant = None
        self.theta = None
        self.moment = None
        
        # attributes for ECR method
        self.dx_ECR = None
        self.dy_ECR = None
        self.ro_ECR = None
        self.vx_ECR = None
        self.vy_ECR = None
        self.theta_ECR = None
        self.vtotal_ECR = None
        self.moment_ECR = None
        self.moment_ECG = None
        
        # attributes for ICR method
        self.dx_ICR = []
        self.dy_ICR = []
        self.ro_ICR = []
        self.force_ICR = []
        self.deformation_ICR = []
        self.moment_ICR = []
        self.moment_ICG = []
        self.vx_ICR = []
        self.vy_ICR = []
        self.theta_ICR = []

    def update_geometry(self, x_cg, y_cg):
        """
        Update bolt geometry with respect to bolt group CG
        """
        self.dx = self.x - x_cg
        self.dy = self.y - y_cg
        self.ro = (self.dx**2 + self.dy**2)**(1/2)
        
    def update_geometry_ECR(self, x_ECR, y_ECR):
        """
        Update geometry with respect to elastic center of rotation
        """
        self.dx_ECR = self.x - x_ECR
        self.dy_ECR = self.y - y_ECR
        self.ro_ECR = (self.dx_ECR**2 + self.dy_ECR**2)**(1/2)
        
    def update_geometry_ICR(self, x_ICR, y_ICR):
        """
        Update geometry with respect to instant center of rotation
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
        self.theta = math.atan2(self.vy_total,self.vx_total) * 180 / math.pi
        self.moment = -(self.vx_total*self.dy) + self.vy_total*self.dx
        
    def update_forces_ECR(self, K):
        """
        Compute bolt forces using elastic center of rotation method
        """
        self.vx_ECR = K * self.dy_ECR
        self.vy_ECR = -K * self.dx_ECR
        self.theta_ECR = math.atan2(self.vy_ECR,self.vx_ECR) * 180 / math.pi
        self.vtotal_ECR = math.sqrt(self.vx_ECR**2 + self.vy_ECR**2)
        self.moment_ECR = self.vtotal_ECR * self.ro_ECR
        self.moment_ECG = -self.vx_ECR*self.dy + self.vy_ECR*self.dx
    
    def update_forces_ICR(self, ro_max, Rult):
        """
        Compute bolt forces using ICR method
        """      
        D_ULT = 0.34
        deformation = self.ro_ICR[-1] / ro_max * D_ULT
        force = (1-math.exp(-10*deformation))**(0.55) * Rult
        moment_icr = force*self.ro_ICR[-1]
        
        # calculate force components in x and y and moment
        vx = -force * self.dy_ICR[-1] / self.ro_ICR[-1] if self.ro_ICR[-1]!=0 else 0
        vy = force * self.dx_ICR[-1] / self.ro_ICR[-1] if self.ro_ICR[-1]!=0 else 0
        moment_cg = - vx*self.dy + vy*self.dx
        theta_ICR = math.atan2(vy, vx) * 180 / math.pi
        
        # save results
        self.vx_ICR.append(vx)
        self.vy_ICR.append(vy)
        self.deformation_ICR.append(deformation)
        self.force_ICR.append(force)
        self.moment_ICR.append(moment_icr)
        self.moment_ICG.append(moment_cg)
        self.theta_ICR.append(theta_ICR)
        
    def get_moment_ICR(self, ro_max):
        """
        Used to calculate the ICR coefficient. In particular, it is called by the
        BoltGroup object to calculate sum of moment contribution due to unit load P (i.e. sum(Mi1))
        """
        D_ULT = 0.34
        deformation = self.ro_ICR[-1] / ro_max * D_ULT
        force = (1-math.exp(-10*deformation))**(0.55)
        moment = force * self.ro_ICR[-1]
        return moment