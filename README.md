The file should either be run in VS Code (or similar) or in the console. This is because some critical outputs are provided in the console.

You will need the following Python packages to run this code:
- matplotlib
- numpy
- networkx
- cadquery

`makemesh()` is the same in `poremaker.py` and `squaremaker.py`, but `buildmesh()` works differently:
- `buildmesh()` in `poremaker.py` generates a porous medium with circular links whose center axes lie on a plane in the middle of the medium.
- `buildmesh()` in `squaremaker.py` generates a porous medium with rectangular links of Poiseuille conductivity equivalent to the circular links. The rectangular links will have their top face lie on the top face of the sample.

You will need the following folder structure to run properly:

```text
porehammer2/
└── outputs/
    ├── figures/
    └── step/
