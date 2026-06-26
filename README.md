The file should either be run in VSCode (or similar) or in the console. This is beccause some critical outputs are provided in the console.

makemesh() is the same in poremaker.py and squaremaker.py, but buildmesh() works differently:
  > buildmesh() in poremaker.py gnerates a porous medium with circular links whose centre axes lie on a plane in the middle of the medium
  > buildmesh() in squaremaker.py generates a porous medium with rectangular links of Poiseulle conductivity equivalent to the circular links. The rectangular links will have its top face lie on the top face of the sample.

You will need the following folder structure to run properly:
|porehammer2/
|----outputs/
|--------/figures/
|--------/step/

The code places output files (PNG in figures, STEP in step) in the respective subfolders in /outputs/
