import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math


def preview(boltgroup):
    """
    Preview bolt configuration
    """   
    # plot bolts
    fig, axs = plt.subplots(1,2, gridspec_kw={"width_ratios":[1,3]}, figsize=[8,6])
    for bolt in boltgroup.bolts :
        axs[1].plot([bolt.x],[bolt.y], 
                 marker="h",
                 markerfacecolor="lightgrey",
                 markeredgecolor="black",
                 markeredgewidth=3,
                 markersize=16,
                 zorder=2,
                 linestyle="none")
        axs[1].annotate("{}".format(bolt.tag), 
                     xy=(bolt.x, bolt.y), 
                     xycoords='data', 
                     xytext=(6, 9), 
                     textcoords='offset points', 
                     fontsize=20,
                     ha = "left",
                     va = "bottom",
                     c = "black")
        
    # plot Cog
    axs[1].plot(boltgroup.x_cg, boltgroup.y_cg, marker="*",c="red",markersize=8,zorder=2,linestyle="none")
    axs[1].annotate("CoR",xy=(boltgroup.x_cg, boltgroup.y_cg), xycoords='data', color="red",
                 xytext=(5, -5), textcoords='offset points', fontsize=14, va="top", zorder=3)
    
    # annotation for bolt group properties
    information_text = "Number of Bolts: {} \n".format(boltgroup.N_bolt) +\
                        "CoR: ({:.2f}, {:.2f})\n".format(boltgroup.x_cg, boltgroup.y_cg) +\
                        "Ix = {:.2f} in4\n".format(boltgroup.Ix) +\
                        "Iy = {:.2f} in4\n".format(boltgroup.Iy) +\
                        "J = {:.2f} in4".format(boltgroup.Iz)
    axs[0].annotate(information_text, (0.1,0.6), xycoords='axes fraction', fontsize=14, va="top", ha="left")

    # styling
    axs[1].set_aspect('equal', 'datalim')
    axs[0].axis("off")
    plt.tight_layout()
    return fig


def plot_elastic(boltgroup):
    """
    Plot bolt forces from elastic method
    """
    fig, axs = plt.subplots(1,2, gridspec_kw={"width_ratios":[1.3,4]}, figsize=[10,6])
    
    # arrow size scaling set up. 
    # Larrow_max is set to 20% of x and y bound. Qarrow_max the associated amplitude. 
    # Therefore, L = (q/Qarrow_max) * Larrow_max
    ybound = max([b.y for b in boltgroup.bolts]) - min([b.y for b in boltgroup.bolts])
    xbound = max([b.x for b in boltgroup.bolts]) - min([b.x for b in boltgroup.bolts])
    Larrow_max = max(xbound,ybound) * 0.20
    Qarrow_max = max([b.v_resultant for b in boltgroup.bolts])
    ARROWWIDTH = 0.03
    
    # text box showing applied load
    information_text = "Vx = {:.2f} k\n".format(boltgroup.Vx) +\
                        "Vy = {:.2f} k\n".format(boltgroup.Vy) +\
                        "Mz = {:.2f} k.in\n\n".format(boltgroup.torsion) +\
                        "Bolt Demand = {:.2f} k\n".format(boltgroup.bolt_demand) +\
                        "Bolt Capacity = {:.2f} k\n".format(boltgroup.bolt_capacity) +\
                        "DCR = {:.2f}".format(boltgroup.bolt_demand / boltgroup.bolt_capacity)
    axs[0].annotate(information_text,
                 xy=(0,0), 
                 xytext=(0.1,0.7), 
                 textcoords='axes fraction', 
                 fontsize=14, 
                 c="black", 
                 ha="left", 
                 va="top",
                 zorder=2)
    
    # plot bolts
    for bolt in boltgroup.bolts:
        axs[1].plot([bolt.x],[bolt.y], 
                 marker="h",
                 markerfacecolor="lightgray",
                 markeredgecolor="black",
                 markeredgewidth=2,
                 markersize=16,
                 zorder=2,
                 linestyle="none")
        axs[1].annotate("({:.1f} k, {:.1f} k)".format(bolt.vx_total, bolt.vy_total),
                     xy=(bolt.x, bolt.y), 
                     xycoords='data', 
                     xytext=(0, -16), 
                     textcoords='offset points', 
                     fontsize=14, 
                     c="black", 
                     ha="center",
                     va="top",
                     zorder=1,
                     bbox=dict(boxstyle='round', facecolor='white'))
    
    # plot Cog
    axs[1].plot(boltgroup.x_cg, boltgroup.y_cg, marker="*",c="red",markersize=8,zorder=3,linestyle="none")

    # bolts reaction arrows
    for bolt in boltgroup.bolts:
        L_arrow = (bolt.v_resultant / Qarrow_max) * Larrow_max
        dx_arrow = L_arrow * math.cos(math.radians(bolt.theta))
        dy_arrow = L_arrow * math.sin(math.radians(bolt.theta))
        axs[1].arrow(bolt.x,
                  bolt.y, 
                  dx_arrow, 
                  dy_arrow, 
                  width=ARROWWIDTH,
                  head_width=8*ARROWWIDTH, 
                  head_length=8*ARROWWIDTH,
                  fc='black', 
                  ec='black', 
                  zorder=2)
    
    # applied force arrows
    if boltgroup.V_resultant != 0:
        L_arrow = Larrow_max * 1.4
        dx_arrow = L_arrow * math.cos(math.radians(boltgroup.theta))
        dy_arrow = L_arrow * math.sin(math.radians(boltgroup.theta))
        x_arrow = boltgroup.x_cg
        y_arrow = boltgroup.y_cg
        axs[1].arrow(x_arrow-dx_arrow, 
                  y_arrow-dy_arrow, 
                  dx_arrow, 
                  dy_arrow, 
                  width=ARROWWIDTH,
                  head_width=8*ARROWWIDTH, 
                  head_length=8*ARROWWIDTH,
                  fc='red', 
                  ec='red', 
                  zorder=3,
                  head_starts_at_zero=False,
                  length_includes_head=True)
        
    if boltgroup.torsion != 0:
        style = "Simple, tail_width=0.8, head_width=10, head_length=10"
        rotation_sign = -1.0 if boltgroup.torsion < 0 else 1.0
        moment_arrow = patches.FancyArrowPatch((boltgroup.x_cg+rotation_sign*0.6, boltgroup.y_cg),
                                               (boltgroup.x_cg-rotation_sign*0.6, boltgroup.y_cg),
                                               connectionstyle=f"arc3,rad={0.65*rotation_sign}",
                                               arrowstyle = style,
                                               color="red")
        axs[1].add_patch(moment_arrow)
        
    # styling
    fig.suptitle("Elastic Method - Superposition", fontweight="bold", fontsize=16)
    axs[1].set_aspect('equal', 'datalim')
    axs[0].axis("off")
    plt.tight_layout()
    return fig


def plot_ECR(boltgroup):
    """
    plot bolt forces from ECR method.
    """
    if boltgroup.torsion == 0:
        fig, axs = plt.subplots()
        axs.annotate("ECR method is not applicable for torsion = 0",
                     xy=(0,0), 
                     xytext=(0.05,0.5), 
                     textcoords='axes fraction', 
                     fontsize=14)
        return fig
    
    fig, axs = plt.subplots(1,2, gridspec_kw={"width_ratios":[1.5,4]}, figsize=[10,6])
    # arrow size scaling set up. 
    # Larrow_max is set to 20% of x and y bound. Qarrow_max the associated amplitude. 
    # Therefore, L = (q/Qarrow_max) * Larrow_max
    ybound = max([b.y for b in boltgroup.bolts]) - min([b.y for b in boltgroup.bolts])
    xbound = max([b.x for b in boltgroup.bolts]) - min([b.x for b in boltgroup.bolts])
    Larrow_max = max(xbound,ybound) * 0.20
    Qarrow_max = max([b.vtotal_ECR for b in boltgroup.bolts])
    ARROWWIDTH = 0.03
    
    # text box showing applied load
    unit = "k" if boltgroup.ecc!=0 else "k.in"
    information_text = "Vx = {:.2f} k\n".format(boltgroup.Vx) +\
                        "Vy = {:.2f} k\n".format(boltgroup.Vy) +\
                        "Mz = {:.2f} k.in\n\n".format(boltgroup.torsion) +\
                        "ECR: ({:.2f}, {:.2f})\n".format(boltgroup.ECR_x, boltgroup.ECR_y) +\
                        "Ce: {:.2f}\n".format(boltgroup.Ce) +\
                        "Rult: {:.2f} k\n".format(boltgroup.bolt_capacity) +\
                        "Connection Demand = {:.2f} {}\n".format(boltgroup.P_demand,unit) +\
                        "Connection Capacity = {:.2f} {}\n".format(boltgroup.P_capacity,unit) +\
                        "DCR = {:.2f}".format(abs(boltgroup.P_demand / boltgroup.P_capacity))
    axs[0].annotate(information_text,
                 xy=(0,0), 
                 xytext=(0.1,0.8), 
                 textcoords='axes fraction', 
                 fontsize=14, 
                 c="black", 
                 ha="left", 
                 va="top",
                 zorder=2)
    
    # plot bolts
    for bolt in boltgroup.bolts:
        axs[1].plot([bolt.x],[bolt.y], 
                 marker="h",
                 markerfacecolor="lightgray",
                 markeredgecolor="black",
                 markeredgewidth=2,
                 markersize=16,
                 zorder=2,
                 linestyle="none")
        axs[1].annotate("({:.1f} k, {:.1f} k)".format(bolt.vx_ECR, bolt.vy_ECR),
                     xy=(bolt.x, bolt.y), 
                     xycoords='data', 
                     xytext=(0, -16), 
                     textcoords='offset points', 
                     fontsize=14, 
                     c="black", 
                     ha="center",
                     va="top",
                     zorder=1,
                     bbox=dict(boxstyle='round', facecolor='white'))
    # plot Cog
    axs[1].plot(boltgroup.x_cg, boltgroup.y_cg, marker="*",c="red",markersize=8,zorder=3,linestyle="none")

    # plot ECR
    if boltgroup.torsion != 0:
        axs[1].plot(boltgroup.ECR_x, boltgroup.ECR_y, marker="*",c="red",markersize=14,zorder=3,linestyle="none")
        axs[1].annotate("ECR",
                     xy=(boltgroup.ECR_x, boltgroup.ECR_y), xycoords='data', color="red",
                     xytext=(-5, -5), textcoords='offset points', fontsize=16, va="top", ha="right")
    
    # bolts reaction arrows
    for bolt in boltgroup.bolts:
        L_arrow = (bolt.vtotal_ECR / Qarrow_max) * Larrow_max
        dx_arrow = L_arrow * math.cos(math.radians(bolt.theta_ECR))
        dy_arrow = L_arrow * math.sin(math.radians(bolt.theta_ECR))
        axs[1].arrow(bolt.x,
                  bolt.y, 
                  dx_arrow, 
                  dy_arrow, 
                  width=ARROWWIDTH,
                  head_width=8*ARROWWIDTH, 
                  head_length=8*ARROWWIDTH,
                  fc='black', 
                  ec='black', 
                  zorder=2)
    
    # applied force arrows
    if boltgroup.V_resultant != 0:
        L_arrow = Larrow_max * 1.4
        dx_arrow = L_arrow * math.cos(math.radians(boltgroup.theta))
        dy_arrow = L_arrow * math.sin(math.radians(boltgroup.theta))
        x_arrow = boltgroup.x_cg + boltgroup.ecc_x
        y_arrow = boltgroup.y_cg + boltgroup.ecc_y
        axs[1].axline([x_arrow-dx_arrow, y_arrow-dy_arrow], 
                      [x_arrow, y_arrow],
                      linewidth=1,
                      linestyle="--",
                      color="black")
        axs[1].axline([x_arrow, y_arrow], 
                      [boltgroup.ECR_x, boltgroup.ECR_y],
                      linewidth=1,
                      linestyle="--",
                      color="black")
        axs[1].arrow(x_arrow-dx_arrow, 
                  y_arrow-dy_arrow, 
                  dx_arrow, 
                  dy_arrow, 
                  width=ARROWWIDTH,
                  head_width=8*ARROWWIDTH, 
                  head_length=8*ARROWWIDTH,
                  fc='red', 
                  ec='red', 
                  zorder=3,
                  head_starts_at_zero=False,
                  length_includes_head=True)
        
    # styling
    fig.suptitle("Elastic Method - Center of Rotation", fontweight="bold", fontsize=16)
    axs[1].set_aspect('equal', 'datalim')
    axs[0].axis("off")
    plt.tight_layout()
    
    return fig


def plot_ICR(boltgroup):
    """
    plot bolt forces from ICR method.
    """
    if boltgroup.torsion == 0:
        fig, axs = plt.subplots()
        axs.annotate("ICR method is not applicable for torsion = 0",
                     xy=(0,0), 
                     xytext=(0.05,0.5), 
                     textcoords='axes fraction', 
                     fontsize=14)
        return fig
    
    fig, axs = plt.subplots(1,2, gridspec_kw={"width_ratios":[1.5,4]}, figsize=[10,6])
    # arrow size scaling set up. 
    # Larrow_max is set to 20% of x and y bound. Qarrow_max the associated amplitude. 
    # Therefore, L = (q/Qarrow_max) * Larrow_max
    ybound = max([b.y for b in boltgroup.bolts]) - min([b.y for b in boltgroup.bolts])
    xbound = max([b.x for b in boltgroup.bolts]) - min([b.x for b in boltgroup.bolts])
    Larrow_max = max(xbound,ybound) * 0.20
    Qarrow_max = max([abs(b.force_ICR[-1]) for b in boltgroup.bolts])
    #Qarrow_max = boltgroup.V_resultant
    ARROWWIDTH = 0.03
    
    # text box showing applied load
    unit = "k" if boltgroup.ecc!=0 else "k.in"
    information_text = "Vx = {:.2f} k\n".format(boltgroup.Vx) +\
                        "Vy = {:.2f} k\n".format(boltgroup.Vy) +\
                        "Mz = {:.2f} k.in\n\n".format(boltgroup.torsion) +\
                        "ICR: ({:.2f}, {:.2f})\n".format(boltgroup.ICR_x[-1], boltgroup.ICR_y[-1]) +\
                        "Cu: {:.2f}\n".format(boltgroup.Cu[-1]) +\
                        "Rult: {:.2f} k\n".format(boltgroup.bolt_capacity) +\
                        "Connection Demand = {:.2f} {}\n".format(boltgroup.P_demand_ICR,unit) +\
                        "Connection Capacity = {:.2f} {}\n".format(boltgroup.P_capacity_ICR,unit) +\
                        "DCR = {:.2f}".format(abs(boltgroup.P_demand_ICR / boltgroup.P_capacity_ICR))
    axs[0].annotate(information_text,
                 xy=(0,0), 
                 xytext=(0.1,0.8), 
                 textcoords='axes fraction', 
                 fontsize=14, 
                 c="black", 
                 ha="left", 
                 va="top",
                 zorder=2)
    
    # plot bolts
    for bolt in boltgroup.bolts:
        axs[1].plot([bolt.x],[bolt.y], 
                 marker="h",
                 markerfacecolor="lightgray",
                 markeredgecolor="black",
                 markeredgewidth=2,
                 markersize=16,
                 zorder=2,
                 linestyle="none")
        axs[1].annotate("({:.1f} k, {:.1f} k)".format(bolt.vx_ICR[-1], bolt.vy_ICR[-1]),
                     xy=(bolt.x, bolt.y), 
                     xycoords='data', 
                     xytext=(0, -16), 
                     textcoords='offset points', 
                     fontsize=14, 
                     c="black", 
                     ha="center",
                     va="top",
                     zorder=1,
                     bbox=dict(boxstyle='round', facecolor='white'))
    # plot Cog
    axs[1].plot(boltgroup.x_cg, boltgroup.y_cg, marker="*",c="red",markersize=8,zorder=3,linestyle="none")

    # plot ICR
    if boltgroup.torsion != 0:
        axs[1].plot(boltgroup.ICR_x[-1], boltgroup.ICR_y[-1], marker="*",c="red",markersize=14,zorder=3,linestyle="none")
        axs[1].annotate("ICR",
                     xy=(boltgroup.ICR_x[-1], boltgroup.ICR_y[-1]), xycoords='data', color="red",
                     xytext=(-5, -5), textcoords='offset points', fontsize=16, va="top", ha="right")
    
    # bolts reaction arrows
    for bolt in boltgroup.bolts:
        L_arrow = (abs(bolt.force_ICR[-1]) / Qarrow_max) * Larrow_max
        dx_arrow = L_arrow * math.cos(math.radians(bolt.theta_ICR[-1]))
        dy_arrow = L_arrow * math.sin(math.radians(bolt.theta_ICR[-1]))
        axs[1].arrow(bolt.x,
                  bolt.y, 
                  dx_arrow, 
                  dy_arrow, 
                  width=ARROWWIDTH,
                  head_width=8*ARROWWIDTH, 
                  head_length=8*ARROWWIDTH,
                  fc='black', 
                  ec='black', 
                  zorder=2)
    
    # applied force arrows
    if boltgroup.V_resultant != 0:
        L_arrow = Larrow_max * 1.4
        dx_arrow = L_arrow * math.cos(math.radians(boltgroup.theta))
        dy_arrow = L_arrow * math.sin(math.radians(boltgroup.theta))
        x_arrow = boltgroup.x_cg + boltgroup.ecc_x
        y_arrow = boltgroup.y_cg + boltgroup.ecc_y
        axs[1].axline([x_arrow-dx_arrow, y_arrow-dy_arrow], 
                      [x_arrow, y_arrow],
                      linewidth=1,
                      linestyle="--",
                      color="black")
        axs[1].axline([x_arrow, y_arrow], 
                      [boltgroup.ICR_x[-1], boltgroup.ICR_y[-1]],
                      linewidth=1,
                      linestyle="--",
                      color="black")
        axs[1].arrow(x_arrow-dx_arrow, 
                  y_arrow-dy_arrow, 
                  dx_arrow, 
                  dy_arrow, 
                  width=ARROWWIDTH,
                  head_width=8*ARROWWIDTH, 
                  head_length=8*ARROWWIDTH,
                  fc='red', 
                  ec='red', 
                  zorder=3,
                  head_starts_at_zero=False,
                  length_includes_head=True)
        
    # styling
    fig.suptitle("Instant Center of Rotation Method", fontweight="bold", fontsize=16)
    axs[1].set_aspect('equal', 'datalim')
    axs[0].axis("off")
    plt.tight_layout()
    
    return fig






def plot_ICR_anim(boltgroup):
    """
    temporary function to produce animations
    """
    fig, axs = plt.subplots(figsize=[8,8])
    # arrow size scaling set up. 
    # Larrow_max is set to 20% of x and y bound. Qarrow_max the associated amplitude. 
    # Therefore, L = (q/Qarrow_max) * Larrow_max
    ybound = max([b.y for b in boltgroup.bolts]) - min([b.y for b in boltgroup.bolts])
    xbound = max([b.x for b in boltgroup.bolts]) - min([b.x for b in boltgroup.bolts])
    Larrow_max = max(xbound,ybound) * 0.20
    Qarrow_max = max([abs(b.force_ICR[-1]) for b in boltgroup.bolts])
    #Qarrow_max = boltgroup.V_resultant
    ARROWWIDTH = 0.03
    
    information_text = "Px = {:.0f} k\n".format(boltgroup.Vx) +\
                        "Py = {:.0f} k\n".format(boltgroup.Vy) +\
                        "Mz = {:.0f} k.in\n".format(boltgroup.torsion)
    axs.annotate(information_text,
                 xy=(0,0), 
                 xytext=(0.98,-0.02), 
                 textcoords='axes fraction', 
                 fontsize=14, 
                 c="black", 
                 ha="right", 
                 va="bottom",
                 zorder=2)
    
    # plot bolts
    for bolt in boltgroup.bolts:
        axs.plot([bolt.x],[bolt.y], 
                 marker="h",
                 markerfacecolor="lightgray",
                 markeredgecolor="black",
                 markeredgewidth=2,
                 markersize=16,
                 zorder=2,
                 linestyle="none")
        axs.annotate("({:.1f} k, {:.1f} k)".format(bolt.vx_ICR[-1], bolt.vy_ICR[-1]),
                     xy=(bolt.x, bolt.y), 
                     xycoords='data', 
                     xytext=(0, -16), 
                     textcoords='offset points', 
                     fontsize=14, 
                     c="black", 
                     ha="center",
                     va="top",
                     zorder=1,
                     bbox=dict(boxstyle='round', facecolor='white'))
    # plot Cog
    axs.plot(boltgroup.x_cg, boltgroup.y_cg, marker="*",c="red",markersize=8,zorder=3,linestyle="none")

    # plot ICR
    if boltgroup.torsion != 0:
        axs.plot(boltgroup.ICR_x[-1], boltgroup.ICR_y[-1], marker="*",c="red",markersize=14,zorder=3,linestyle="none")
        axs.annotate("ICR",
                     xy=(boltgroup.ICR_x[-1], boltgroup.ICR_y[-1]), xycoords='data', color="red",
                     xytext=(-5, -5), textcoords='offset points', fontsize=16, va="top", ha="right")
    
    # bolts reaction arrows
    for bolt in boltgroup.bolts:
        L_arrow = (abs(bolt.force_ICR[-1]) / Qarrow_max) * Larrow_max
        dx_arrow = L_arrow * math.cos(math.radians(bolt.theta_ICR[-1]))
        dy_arrow = L_arrow * math.sin(math.radians(bolt.theta_ICR[-1]))
        axs.arrow(bolt.x,
                  bolt.y, 
                  dx_arrow, 
                  dy_arrow, 
                  width=ARROWWIDTH,
                  head_width=8*ARROWWIDTH, 
                  head_length=8*ARROWWIDTH,
                  fc='black', 
                  ec='black', 
                  zorder=2)
    
    # applied force arrows
    if boltgroup.V_resultant != 0:
        L_arrow = Larrow_max * 1.4
        dx_arrow = L_arrow * math.cos(math.radians(boltgroup.theta))
        dy_arrow = L_arrow * math.sin(math.radians(boltgroup.theta))
        x_arrow = boltgroup.x_cg + boltgroup.ecc_x
        y_arrow = boltgroup.y_cg + boltgroup.ecc_y
        axs.axline([x_arrow-dx_arrow, y_arrow-dy_arrow], 
                      [x_arrow, y_arrow],
                      linewidth=1,
                      linestyle="--",
                      color="black")
        axs.axline([x_arrow, y_arrow], 
                      [boltgroup.ICR_x[-1], boltgroup.ICR_y[-1]],
                      linewidth=1,
                      linestyle="--",
                      color="black")
        axs.arrow(x_arrow-dx_arrow, 
                  y_arrow-dy_arrow, 
                  dx_arrow, 
                  dy_arrow, 
                  width=ARROWWIDTH,
                  head_width=8*ARROWWIDTH, 
                  head_length=8*ARROWWIDTH,
                  fc='red', 
                  ec='red', 
                  zorder=3,
                  head_starts_at_zero=False,
                  length_includes_head=True)

    # styling
    fig.suptitle("Instant Center of Rotation Method (Cu = {:.2f})".format(boltgroup.Cu[-1]), fontweight="bold", fontsize=16)
    #axs.set_aspect('equal', 'datalim')
    axs.set_xlim([-2,8])
    axs.set_ylim([-2,8])
    plt.tight_layout()
    
    return fig





