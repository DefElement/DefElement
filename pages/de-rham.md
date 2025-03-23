--
authors:
  - Scroggs, Matthew W.
  - Nobre, Nuno
--

# De Rham element families
The following relationship is the de Rham complex in 3D:
$$
H^1
\xrightarrow{\nabla}
\textbf{H}(\text{curl})
\xrightarrow{\nabla\times}
\textbf{H}(\text{div})
\xrightarrow{\nabla\cdot}
L^2
$$
We say this sequence is exact since the range (or image) of each of the
differential operators coincides with the null space (or kernel) of the next
operator in the sequence. We also note the last map is a surjection.

A set of four finite elements \(\mathcal{V}_0\) to \(\mathcal{V}_3\) forms 
a discrete de Rham complex if the following commutative diagram holds,
where \(I_0\) to \(I_3\) are interpolations into \(\mathcal{V}_0\) to \(\mathcal{V}_3\).
(The commutative diagram holds if following different arrow combinations to the same destination will give the same result.)
$$
\begin{array}{ccccccc}
H^1
&\xrightarrow{\nabla}
&\textbf{H}(\text{curl})
&\xrightarrow{\nabla\times}
&\textbf{H}(\text{div})
&\xrightarrow{\nabla\cdot}
&L^2\\
\hphantom{\small I_0}\big\downarrow {\small I_0}&&
\hphantom{\small I_1}\big\downarrow {\small I_1}&&
\hphantom{\small I_2}\big\downarrow {\small I_2}&&
\hphantom{\small I_3}\big\downarrow {\small I_3}\\
\mathcal{V}_0
&\xrightarrow{\nabla}
&\mathcal{V}_1
&\xrightarrow{\nabla\times}
&\mathcal{V}_2
&\xrightarrow{\nabla\cdot}
&\mathcal{V}_3
\end{array}
$$
Sequences of finite element spaces forming discrete de Rham complexes are, in
general, not exact. However, it is certainly still the case that the range of
each of the differential operators is contained in (but is not necessarily
coincident with) the null space of the next operator in the sequence.

You can view families of elements that form discrete de Rham complexes on the [families page](index::families).
On DefElement, two naming conventions for elements in a de Rham complex are used.
The first of these is the exterior calculus convention: this is the notation used in the
<a href=https://www-users.cse.umn.edu/~arnold/femtable>Periodic table of the finite elements</a>
<ref title="Periodic table of the finite elements" author="Arnold, D. and Logg, A." journal="SIAM News" year="2014" volume="47" issue="9" url="https://www.siam.org/publications/siam-news/issues/volume-47-number-09-november-2014">.
The second is the Cockburn&ndash;Fu convention: this gives the names used for element families in Cockburn and Fu's 2017 paper<ref title="A systematic construction of finite element commuting exact sequences" author="Cockburn, B. and Fu, G." journal="SIAM journal on numerical analysis" volume="55" issue="4" pagestart="1650" pageend="1688" year="2017" doi="10.1137/16M1073352">.
