import time
import ezbolt


def main():
    # initialize bolt group
    bolt_group = ezbolt.boltgroup.BoltGroup()
    
    # add bolts    
    bolt_group.add_bolts(xo=0, yo=0, width=6, height=6, nx=3, ny=3)
    
    # preview geometry
    ezbolt.plotter.preview(bolt_group)
    
    # calculate bolt force with elastic method
    results = bolt_group.solve(Vx=vx, Vy=vy, torsion=Mz)
    
    # plot bolt forces
    ezbolt.plotter.plot_elastic(bolt_group)
    ezbolt.plotter.plot_ECR(bolt_group)
    ezbolt.plotter.plot_ICR(bolt_group)
    return results




# exhaustive list of input for debugging
vx,vy,Mz = 50,50,200
# vx,vy,Mz = 50,50,-200
# vx,vy,Mz = 50,50,0
# vx,vy,Mz = 50,-50,200
# vx,vy,Mz = 50,-50,-200
# vx,vy,Mz = 50,-50,0
# vx,vy,Mz = 50,0,200
# vx,vy,Mz = 50,0,-200
# vx,vy,Mz = 50,0,0
# vx,vy,Mz = -50,50,200
# vx,vy,Mz = -50,50,-200
# vx,vy,Mz = -50,50,0
# vx,vy,Mz = -50,-50,200
# vx,vy,Mz = -50,-50,-200
# vx,vy,Mz = -50,-50,0
# vx,vy,Mz = -50,0,200
# vx,vy,Mz = -50,0,-200
# vx,vy,Mz = -50,0,0
# vx,vy,Mz = 0,50,200
# vx,vy,Mz = 0,50,-200
# vx,vy,Mz = 0,50,0
# vx,vy,Mz = 0,-50,200
# vx,vy,Mz = 0,-50,-200
# vx,vy,Mz = 0,-50,0
# vx,vy,Mz = 0,0,200
# vx,vy,Mz = 0,0,-200
# vx,vy,Mz = 0,0,0


if __name__ == '__main__':
    TIME_START = time.time()
    mainReturn = main()
    TIME_END = time.time()
    print("Script completed. Total elapsed time: {:.2f} seconds".format(TIME_END - TIME_START))