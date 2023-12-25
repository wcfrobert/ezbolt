import time
import ezbolt
import numpy as np


def main():
    vx_list = np.concatenate([np.linspace(0,-50,10),
                              np.linspace(-50,50,20),
                              np.linspace(50,0,10),
                              np.array([0]*20),
                              np.linspace(0,50,10),
                              np.linspace(50,-50,20),
                              np.linspace(-50,0,10),
                              np.array([0]*20)
                              ])
    vy_list = np.array([-50]*120)
    Mz_list = np.concatenate([np.array([-200]*40),
                              np.linspace(-200,200,20),
                              np.array([200]*40),
                              np.linspace(200,-200,20)
                              ])
    
    torsion_too_low_index = [i for i in range(len(Mz_list)) if abs(Mz_list[i]) < 40]
    vx_list = np.delete(vx_list,torsion_too_low_index)
    vy_list = np.delete(vy_list,torsion_too_low_index)
    Mz_list = np.delete(Mz_list,torsion_too_low_index)
    
    
    for i in range(len(vx_list)):
        print("---------------------frame {}---------------".format(i))
        vx = vx_list[i]
        vy = vy_list[i]
        Mz = Mz_list[i]
        # initialize bolt group
        bolt_group = ezbolt.boltgroup.BoltGroup()
        
        # add bolts    
        bolt_group.add_bolts(xo=0, yo=0, width=6, height=6, nx=3, ny=3)
        
        # preview geometry
        #ezbolt.plotter.preview(bolt_group)
        
        # calculate bolt force with elastic method
        results = bolt_group.solve(Vx=vx, Vy=vy, torsion=Mz)
        
        # plot bolt forces
        #ezbolt.plotter.plot_elastic(bolt_group)
        #ezbolt.plotter.plot_ECR(bolt_group)
        fig = ezbolt.plotter.plot_ICR_anim(bolt_group)
        fig.savefig("anim/frame{:04d}.png".format(i))
    
    
    return 0


# exhaustive list of input for debugging
# vx,vy,Mz = 50,50,200
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