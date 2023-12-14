import time
import ezbolt





def main():
    # initialize bolt group
    bolt_group = ezbolt.boltgroup.BoltGroup()
    
    # add bolts    
    bolt_group.add_bolts(xo=0, yo=0, width=6, height=6, nx=3, ny=3)
    
    # preview geometry
    ezbolt.plotter.preview(bolt_group)
    
    # solve for bolt force using three different methods
    results = bolt_group.solve(Vx=-50, Vy=-50, torsion=200, bolt_capacity=17.9)
    
    # plot forces
    ezbolt.plotter.plot_elastic(bolt_group)
    #ezbolt.plotter.plot_ICR()
    
    return bolt_group






if __name__ == '__main__':
    time_start = time.time()
    mainReturn = main()
    time_end = time.time()
    print("Script completed. Total elapsed time: {:.2f} seconds".format(time_end - time_start))