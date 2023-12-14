import matplotlib.pyplot as plt
import math

def preview(boltgroup):
    """
    Preview bolt configuration
    """
    # get center of gravity
    boltgroup.update_geometric_properties()
    
    # plot bolts
    fig, axs = plt.subplots(figsize=[6,6])
    for bolt in boltgroup.bolts :
        axs.plot([bolt.x],[bolt.y], 
                 marker="o",
                 markerfacecolor="lightgrey",
                 markeredgecolor="black",
                 markeredgewidth=3,
                 markersize=24,
                 zorder=2,
                 linestyle="none")
        axs.annotate("{}".format(bolt.tag), 
                     xy=(bolt.x, bolt.y), 
                     xycoords='data', 
                     xytext=(6, 9), 
                     textcoords='offset points', 
                     fontsize=20,
                     ha = "left",
                     va = "bottom",
                     c = "black")
    
    # plot Cog
    axs.plot(boltgroup.x_cg, boltgroup.y_cg, marker="*",c="black",markersize=12,zorder=2,linestyle="none")
    axs.annotate("CoG",xy=(boltgroup.x_cg, boltgroup.y_cg), xycoords='data', color="black",
                    xytext=(5, -5), textcoords='offset points', fontsize=14, va="top", zorder=3)
    
    # styling
    axs.set_aspect('equal', 'datalim')
    fig.suptitle("Bolt Group Preview", fontweight="bold")
    plt.tight_layout()
    axs.xaxis.grid()
    axs.yaxis.grid()
    return fig


def plot_elastic(boltgroup):
    """
    Plot bolt forces from elastic method
    """
    fig, axs = plt.subplots(figsize=[8,8])
    
    # plot bolts
    for bolt in boltgroup.bolts:
        axs.plot([bolt.x],[bolt.y], 
                 marker="o",
                 markerfacecolor="lightgray",
                 markeredgecolor="black",
                 markeredgewidth=2,
                 markersize=24,
                 zorder=1,
                 linestyle="none")
        axs.annotate("[{:.2f} k, {:.2f} k]".format(bolt.vx_total, bolt.vy_total),
                     xy=(bolt.x, bolt.y), 
                     xycoords='data', 
                     xytext=(0, 12), 
                     textcoords='offset points', 
                     fontsize=14, 
                     c="blue", 
                     ha="center",
                     bbox=dict(boxstyle="round", fc="0.99"))

    # arrow size scaling
    ybound = max([b.y for b in boltgroup.bolts]) - min([b.y for b in boltgroup.bolts])
    xbound = max([b.x for b in boltgroup.bolts]) - min([b.x for b in boltgroup.bolts])
    Larrow_max = max(xbound,ybound) * 0.25
    Qarrow_max = max([b.v_resultant for b in boltgroup.bolts]) if boltgroup.V_resultant==0 else boltgroup.V_resultant
    ARROWWIDTH = 0.03
    
    # bolts reaction arrows
    for bolt in boltgroup.bolts:
        L_arrow = bolt.v_resultant / Qarrow_max * Larrow_max
        dx_arrow = L_arrow * math.cos(math.radians(bolt.v_theta))
        dy_arrow = L_arrow * math.sin(math.radians(bolt.v_theta))
        axs.arrow(bolt.x,
                  bolt.y, 
                  dx_arrow, 
                  dy_arrow, 
                  width=ARROWWIDTH,
                  head_width=8*ARROWWIDTH, 
                  head_length=8*ARROWWIDTH,
                  fc='blue', 
                  ec='blue', 
                  zorder=2)
    
    # ECR and applied load can be far outside plot. Limit plotting limit as to not distort axis
    axs.set_aspect('equal', 'datalim')
    xbound = axs.get_xlim()
    ybound = axs.get_ylim()
    bound = max(abs(max(xbound, key=abs)), abs(max(ybound, key=abs)))
    
    # plot ECR
    within_xview = boltgroup.elastic_ICRx < 1.4*bound and boltgroup.elastic_ICRx > 1.4*-bound
    within_yview = boltgroup.elastic_ICRy < 1.4*bound and boltgroup.elastic_ICRy > 1.4*-bound
    if boltgroup.torsion != 0 and within_xview and within_yview:
        axs.plot(boltgroup.elastic_ICRx, boltgroup.elastic_ICRy, marker="*",c="black",markersize=14,zorder=2,linestyle="none")
        axs.annotate("ECR",
                     xy=(boltgroup.elastic_ICRx, boltgroup.elastic_ICRy), xycoords='data', color="black",
                     xytext=(-5, -5), textcoords='offset points', fontsize=16, va="top", ha="right")
    
    
    # applied force arrows
    if boltgroup.V_resultant != 0:
        axs.annotate("Vx = {:.2f} k\nVy = {:.2f} k\nMz = {:.2f} k.in".format(boltgroup.Vx, boltgroup.Vy, boltgroup.torsion),
                     xy=(0,0), 
                     xytext=(0.98,0.02), 
                     textcoords='axes fraction', 
                     fontsize=14, 
                     c="red", 
                     ha="right", 
                     va="bottom",
                     bbox=dict(boxstyle="round", fc="0.99"),
                     zorder=2)
        
        L_arrow = Larrow_max
        dx_arrow = L_arrow * math.cos(math.radians(boltgroup.theta))
        dy_arrow = L_arrow * math.sin(math.radians(boltgroup.theta))
        ecc_x = boltgroup.ecc * -math.cos(math.radians(boltgroup.theta+90))
        ecc_y = boltgroup.ecc * -math.sin(math.radians(boltgroup.theta+90))
        x_arrow = boltgroup.x_cg + ecc_x
        y_arrow = boltgroup.y_cg + ecc_y
        within_xview = x_arrow < 1.4*bound and x_arrow > 1.4*-bound
        within_yview = y_arrow < 1.4*bound and y_arrow > 1.4*-bound
        if within_xview and within_yview:
            axs.arrow(x_arrow, 
                      y_arrow, 
                      dx_arrow, 
                      dy_arrow, 
                      width=ARROWWIDTH,
                      head_width=8*ARROWWIDTH, 
                      head_length=8*ARROWWIDTH,
                      fc='red', 
                      ec='red', 
                      zorder=3)
            
    # styling
    fig.suptitle("Bolt Forces Determined Via Elastic Method", fontweight="bold", fontsize=16)
    plt.tight_layout()
    axs.xaxis.grid()
    axs.yaxis.grid()




