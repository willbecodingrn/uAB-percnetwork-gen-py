> squaremaker and poremaker generate different geometries
	> squaremaker generates a network of square links extruded from a common face of the sample
	> poremaker generates a network of cylindrical links whose axes lie in the centre of the sample
	> poremaker generates a network closer to Abitbol et al. but is less manufacture-friendly (more prone to defects)
	> squares from squaremaker have geometries of equal Poiseuille conductance to the cylindrical links, based on Boussinesq's work as presented in Frank M. White (§3-3.3)
	> makemesh() is identical between squaremaker and poremaker except in the definition of capillary pressure
	> hydraulic conductivity is the same between squaremaker and poremaker as equivalent hydraulic conductivity was used to determine the size of the square.

> Update t_c and tension in both squaremaker and poremaker as needed to reflect the values of the fluid being used.

> makemesh() must be run before buildmesh()
	> makemesh() generates the network Graph object, percolation threshold, and node positions, and declares global variables used in buildmesh()
	> makemesh currently only generates an L x L network with every second column offset by half of node spacing

>buildmesh() is not very well optimized and can only functionally generate a limited size of up t0 L ~ 128
	> 128x128