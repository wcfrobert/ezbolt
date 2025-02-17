import ezbolt

# Example 1
example1 = ezbolt.BoltGroup()
example1.add_bolts(xo=0, yo=0, width=1, height=9, nx=1, ny=4)
results = example1.solve(Vx=0, Vy=-40, torsion=-160, bolt_capacity=17.9)
ezbolt.plot_elastic(example1)
ezbolt.plot_ICR(example1)



# Example 2
example2 = ezbolt.BoltGroup()
example2.add_bolts(xo=0, yo=0, width=3, height=9, nx=2, ny=4)
results = example2.solve(Vx=80, Vy=-80, torsion=-160, bolt_capacity=17.9)
ezbolt.plot_elastic(example2)
ezbolt.plot_ICR(example2)



# Example 3
example3 = ezbolt.BoltGroup()
example3.add_bolts(xo=0, yo=0, width=6, height=6, nx=2, ny=2)
results = example3.solve(Vx=-30, Vy=-40, torsion=120, bolt_capacity=17.9)
ezbolt.plot_elastic(example3)
ezbolt.plot_ICR(example3)