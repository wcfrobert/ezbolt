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
    results = bolt_group.solve(Vx=50, Vy=50, torsion=200)
    
    # plot bolt forces
    ezbolt.plotter.plot_elastic(bolt_group)
    ezbolt.plotter.plot_ECR(bolt_group)
    ezbolt.plotter.plot_ICR(bolt_group)
    return results






if __name__ == '__main__':
    TIME_START = time.time()
    mainReturn = main()
    TIME_END = time.time()
    print("Script completed. Total elapsed time: {:.2f} seconds".format(TIME_END - TIME_START))