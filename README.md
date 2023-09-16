## Bachelor's thesis: *Optimization of quantum entanglement detection software*

> ## Introduction
>
> Closest Separable State Finder (CSSFinder) is a program which can be used for 
> detection of entanglement in quantum system and determining how strong this
> entanglement is. It is based on an adapted algorithm by Elmer G. Gilbert, which allows
> for calculating the approximate value of the Hilbert-Schmidt distance between a
> quantum state and a set of separated states. The operation of this algorithm is
> described in a paper titled `Hilbert-Schmidt distance and entanglement witnessing'
> whose authors are Palash Pandya, Omer Sakarya and Marcin Wieśniak.
> 
> Dr. Marcin Wieśniak, prof. of UG, created an implementation of the CSSF algorithm in the
> Python language, using the NumPy library to perform the necessary matrix calculations.
> This choice was dictated by the possibilities offered by this toolkit. It allows you to
> quickly create simple code, capable of performing calculations relatively efficiently on
> all the most popular systems for desktop computers.
> 
> The advantages of the Python language are widely noted by both the academia as well as
> the commercial community, as is clearly evident in compilations such as those published
> by GitHub, Inc. `The top programming languages' (2022). The Python language ranks second
> in it.
> 
> Alternatives in the form of the C, C++ or Fortran languages would require more and more
> complex code, while forcing you to manually compile a build system, external libraries,
> and using dedicated solutions for each operating system operating system. In addition,
> performing calculations would be difficult, due to the the complicated process of
> integrating specialized libraries for linear algebra, the need for manual memory
> handling and static typing.

Finished with grade 5 (2-5 range), unfortunately full version is available only in Polish.

## Table of contents

```
1 Introduction.........................................................................3
    1.1 Operation of the Program.......................................................3
    1.2 Purpose of the work............................................................4
    1.3 Reasons to proceed with optimization...........................................5
2 Tools................................................................................5
    2.1 AOT compilation................................................................5
    2.2 JIT compilation................................................................6
    2.3 Tool selection.................................................................7
        2.3.1 Python and NumPy.........................................................7
        2.3.2 Python and NumPy with AOT................................................7
        2.3.3 Python and NumPy with JIT................................................8
        2.3.4 Rust and Ndarray.........................................................8
        2.3.5 Rust and Ndarray with OpenBLAS...........................................9
3 Methods..............................................................................9
    3.1 Modularization.................................................................9
    3.2 Test data.....................................................................10
    3.3 Test environment..............................................................11
    3.4 Profiling.....................................................................11
    3.5 Calculation precision.........................................................12
    3.6 Graphs........................................................................13
4 Results.............................................................................13
    4.1 Preliminary profiling.........................................................13
    4.2 Preliminary performance measurements..........................................15
    4.3 Double precision measurements.................................................16
        4.3.1 Python and NumPy........................................................17
        4.3.2 Python and NumPy with AOT...............................................17
        4.3.3 Python and NumPy with JIT...............................................19
        4.3.4 Rust and Ndarray........................................................20
        4.3.5 Rust and Ndarray with OpenBLAS..........................................20
4.4 Single precision measurements.....................................................21
        4.4.1 Python and NumPy........................................................21
        4.4.2 Python and NumPy with AOT...............................................22
        4.4.3 Python and NumPy with JIT...............................................22
        4.4.4 Rust and Ndarray........................................................24
        4.4.5 Rust and Ndarray with OpenBLAS..........................................24
    4.5 Matrix statements.............................................................25
        4.5.1 Matrix ρ1 (32 × 32).....................................................25
        4.5.2 Matrix ρ2 (4 × 4).......................................................26
        4.5.3 Matrix ρ3 (8 × 8).......................................................27
        4.5.4 Matrix ρ4 (16 × 16).....................................................27
        4.5.5 Matrix ρ5 (32 × 32).....................................................27
        4.5.6 Matrix ρ6 (64 × 64).....................................................28
    4.6 Rust profiling with OpenBLAS..................................................29
5 Discussion..........................................................................30
    5.1 Summary.......................................................................30
    5.2 Follow-up.....................................................................31
    5.3 Overlooked tools..............................................................32
        5.3.1 PyTorch and TensorFlow..................................................32
        5.3.2 PyPy....................................................................32
        5.3.3 C/C++...................................................................32
6 Conclusions.........................................................................33
    6.1 Conclusion....................................................................33
    6.2 Code..........................................................................33
References............................................................................35
```
