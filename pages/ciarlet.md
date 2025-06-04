--
authors:
  - Scroggs, Matthew W.
--

# How to define a finite element
This page describes how finite elements are defined in the DefElement database.

## Cell subentities
Throughout this website, the subentities of a reference cell will be referred to as described here.

The vertices, edges, faces, and volumes of a reference cell have dimension
0, 1, 2, and 3 (respectively).
The (topological) dimension \(d\) is the dimension of the reference cell itself.
(When using the finite element method, the topological dimensions may differ from the
<em>geometric</em> dimension: for example, when meshing a 2D manifold in 3D space, the
topological and geometric dimensions are 2 and 3 (respectively).)

The codimension of an entity is given by subtracting the dimension of the entity from the
topological dimension of the reference cell. Entities of codimension 1, 2, and 3 are
called facets, ridges and peaks (respectively). The usual names given to entities of
reference cells of topological dimensions 0 to 3 are shown below.

<center>
<table class='bordered'>
<thead>
<tr><td>Topological dimension</td><td colspan=4>Entities by dimension</td><td colspan=4>Entities by codimension</td></tr>
<tr><td></td><td>0</td><td>1</td><td>2</td><td>3</td><td>0</td><td>1 (facets)</td><td>2 (ridges)</td><td>3 (peaks)</td></td>
</thead>
<tr><td>0 (a vertex)</td><td>point</td><td>-</td><td>-</td><td>-</td><td>cell</td><td>-</td><td>-</td><td>-</td></tr>
<tr><td>1 (an interval)</td><td>points</td><td>edge</td><td>-</td><td>-</td><td>cell</td><td>points</td><td>-</td><td>-</td></tr>
<tr><td>2 (a polygon)</td><td>points</td><td>edges</td><td>face</td><td>-</td><td>cell</td><td>edges</td><td>points</td><td>-</td></tr>
<tr><td>3 (a polyhedron)</td><td>points</td><td>edges</td><td>faces</td><td>volume</td><td>cell</td><td>faces</td><td>edges</td><td>points</td></tr>
</table>
</center>

## Ciarlet finite elements
The Ciarlet definition <ref type="book" title="The Finite Element Method for Elliptic Problems" author="Ciarlet, P. G." year="1978" publisher="North-Holland">
defines a finite element by a triple \(({{symbols.reference}},{{symbols.polyset}},{{symbols.dual_basis}})\), where

* \({{symbols.reference}}\subset\mathbb{R}^d\) is the reference cell, usually a polygon or polyhedron;
* \({{symbols.polyset}}\) is a finite dimensional polynomial space on \({{symbols.reference}}\) of dimension \(n\);
* \({{symbols.dual_basis}}=\{{{symbols.functional}}_0,...,{{symbols.functional}}_{n-1}\}\) is a basis of the dual space \({{symbols.polyset}}^*=\{f:{{symbols.polyset}}\to\mathbb{R}|f\text{ is linear}\}\). Each functional \({{symbols.functional}}_i\) is associated with a subentity of the reference cell \({{symbols.reference}}\).

The basis functions \(\{{{symbols.basis_function}}_0,...,{{symbols.basis_function}}_{n-1}\}\)
of the finite element space are defined by

\[{{symbols.functional}}_i({{symbols.basis_function}}_j) = \begin{cases}1&i=j\\0&i\not=j\end{cases}\]

The correct continuity is enforced by ensuring that the same global degree-of-freedom is associated with corresponding functionals on the shared subentities of neighbouring cells.

### Example: Order 1 Lagrange space on a triangle
An order 1 [Lagrange space](element::lagrange) on a triangle is defined by:

* \({{symbols.reference}}\) is a triangle with vertices at \((0,0)\), \((1,0)\) and \((0,1)\);
* \({{symbols.polyset}}=\operatorname{span}\{1, x, y\}\);
* \({{symbols.dual_basis}}=\{{{symbols.functional}}_0,{{symbols.functional}}_1,{{symbols.functional}}_2\}\).

The functionals \({{symbols.functional}}_0\) to \({{symbols.functional}}_2\) are defined as
point evaluations at the three vertices of the triangle:

\[{{symbols.functional}}_0:v\mapsto v(0,0)\]
\[{{symbols.functional}}_1:v\mapsto v(1,0)\]
\[{{symbols.functional}}_2:v\mapsto v(0,1)\]

It follows from these definitions that the basis functions of the finite element spaces are
linear functions that are equal 1 to at one of the vertices, and equal to 0 at the other two.
These are:

\[{{symbols.basis_function}}_0(x,y)=1-x-y\]
\[{{symbols.basis_function}}_1(x,y)=x\]
\[{{symbols.basis_function}}_2(x,y)=y\]

{{plot::triangle,Lagrange,1}}

## Integral moments
It is common to use integral moment functionals when defining finite elements. Given a mesh
entity \(e\) and a finite element space \((e,{{symbols.polyset}}_e,{{symbols.dual_basis}}_e)\) defined on \(e\),
the integral moment functionals \({{symbols.functional}}_1,...,{{symbols.functional}}_{n_e}\) are defined by
\[{{symbols.functional}}_i:v\mapsto \int_e v{{symbols.basis_function}}_i,\]
where \({{symbols.basis_function}}_1,...,{{symbols.basis_function}}_{n_e}\) are the basis functions of the finite
element space on \(e\).

For vector-valued spaces, integral moment functional can be defined using a vector-valued space
on \(e\) and taking the dot product inside the integral,
\[{{symbols.functional}}_i:\boldsymbol{v}\mapsto \int_e \boldsymbol{v}\cdot{{symbols.vector_basis_function}}_i.\]
Alternatively, an integral moment can
be taken with a scalar-valued space by taking the dot product with a fixed vector \(\boldsymbol{a}\),
\[{{symbols.functional}}_i:\boldsymbol{v}\mapsto \int_e \boldsymbol{v}\cdot\boldsymbol{a}\,{{symbols.basis_function}}_i.\]
Typically, \(\boldsymbol{a}\) will be tangent to an edge, normal to a facet, or a unit vector in one of
the coordinate directions.

### Example: Order 1 N&eacute;d&eacute;lec (second kind) space on a triangle
The functionals that define an order 1 [N&eacute;d&eacute;lec (second kind) space](element::nedelec2)
on a triangle <ref author="N&eacute;d&eacute;lec, J. C." title="A new family of mixed finite elements in \(\mathbb{R}^3\)" journal="Numerische Mathematik" volume="50" issue="1" year="1986" doi="10.1007/BF01389668" pagestart=57 pageend=81>
are tangential integral moments with order 1 Lagrange spaces on the edges of the triangle.
For example, the two functionals on the edge \(e_0\) of the triangle between \((1,0)\) and \((0,1)\) are
\[{{symbols.functional}}_0:\boldsymbol{v}\to\int_{e_0}\boldsymbol{v}\cdot\left(\begin{array}{c}-\frac1{\sqrt2}\\\frac1{\sqrt{2}}\end{array}\right)(1-s_0),\]
\[{{symbols.functional}}_1:\boldsymbol{v}\to\int_{e_0}\boldsymbol{v}\cdot\left(\begin{array}{c}-\frac1{\sqrt2}\\\frac1{\sqrt{2}}\end{array}\right)s_0,\]
where \(s_0\) varies from 0 (at \((1,0)\)) to 1 (at \((0,1)\)) along \(e_0\).

The basis functions of this space are:
{{plot::triangle,N2curl,1}}

## Mapping finite elements
In order to maintain desired properties when mapping finite elements from a reference
cell to an actual mesh, an appropriate mapping must be defined.
<ref title="Efficient assembly of H(div) and H(curl) conforming finite elements" author="Rognes, M. E. and Kirby, R. C. and Logg, A." journal="SIAM Journal on Scientific Computing" volume="31" issue="6" pagestart="4130" pageend="4151" year="2009" doi="10.1137/08073901X">
<ref title="Quadrilateral H(div) Finite Elements" author="Arnold, D. A. and Boffi, D. and Falk, R. S." journal="SIAM Journal on Numerical Analysis" volume="42" issue="6" pagestart="2429" pageend="2451" year="2005" doi="10.1137/S0036142903431924">
(For elements with a mixture of functional types, a more complex approach is required.
<ref author="Kirby, R. C." title="A general approach to transforming finite elements" journal="The SMAI journal of computational mathematics" pagestart="197" pageend="224" volume="4" year="2018" doi="10.5802/smai-jcm.33">)

Let \({{symbols.geometry_map}}\) be a transformation that maps the reference cell to a cell in the mesh,
and let \(\boldsymbol{x}\) be a point in the cell.

The Jacobian, \({{symbols.jacobian}}\), of the transformation \({{symbols.geometry_map}}\) is
\(\displaystyle\frac{\mathrm{d}F}{\mathrm{d}x}\) for 1D reference cells,
\(\displaystyle\left(
\begin{array}{cc}
\frac{\partial F_1}{\partial x}&\frac{\partial F_1}{\partial y}\\
\frac{\partial F_2}{\partial x}&\frac{\partial F_2}{\partial y}
\end{array}
\right)\) for 2D reference cells, or
\(\displaystyle\left(
\begin{array}{ccc}
\frac{\partial F_1}{\partial x}&\frac{\partial F_1}{\partial y}&\frac{\partial F_1}{\partial z}\\
\frac{\partial F_2}{\partial x}&\frac{\partial F_2}{\partial y}&\frac{\partial F_2}{\partial z}\\
\frac{\partial F_3}{\partial x}&\frac{\partial F_3}{\partial y}&\frac{\partial F_3}{\partial z}
\end{array}
\right)\) for 3D reference cells.

### Scalar-valued basis functions
The identity mapping&mdash;used to map scalar basis functions, \({{symbols.basis_function}}\)&mdash;is defined by
$$\left({{symbols.mapping}}^\text{id}{{symbols.basis_function}}\right)(\boldsymbol{x})
:={{symbols.basis_function}}({{symbols.geometry_map}}^{-1}(\boldsymbol{x})).$$
The term \({{symbols.geometry_map}}^{-1}(\boldsymbol{x})\) is the point on the reference cell corresponding to the point \(\boldsymbol{x}\), so this mapping
maps a value of the function on the reference to the same value at the corresponding point.

The L2 Piola mapping&mdash;used to map scalar discontinuous elements, \({{symbols.basis_function}}\)&mdash;is defined by
$$\left({{symbols.mapping}}^\text{L2}{{symbols.basis_function}}\right)(\boldsymbol{x})
:=\frac1{\det {{symbols.jacobian}}}{{symbols.basis_function}}({{symbols.geometry_map}}^{-1}(\boldsymbol{x})).$$

### Vector-valued basis functions
For vector-valued basis functions, \({{symbols.vector_basis_function}}\), the
<b>covariant Piola</b> (\({{symbols.mapping}}^\text{curl}\)) and
<b>contravariant Piola</b> (\({{symbols.mapping}}^\text{div}\)) mappings are defined:
$$\left({{symbols.mapping}}^\text{curl}{{symbols.vector_basis_function}}\right)(\boldsymbol{x})
:={{symbols.jacobian}}^{-T}{{symbols.vector_basis_function}}({{symbols.geometry_map}}^{-1}(\boldsymbol{x}))$$
$$\left({{symbols.mapping}}^\text{div}{{symbols.vector_basis_function}}\right)(\boldsymbol{x})
:=\frac1{\det {{symbols.jacobian}}}{{symbols.jacobian}}{{symbols.vector_basis_function}}({{symbols.geometry_map}}^{-1}(\boldsymbol{x}))$$
The covariant Piola mapping preserves the tangential component of basis functions on edges and facets,
and are typically used to map H(curl) elements.
The contravariant Piola mapping preserves the normal component of basis functions on facets,
and are typically used to map H(div) elements.

### Matrix-valued basis functions
For matrix-valued basis functions, \({{symbols.matrix_basis_function}}\), the
<b>double covariant Piola</b> (\({{symbols.mapping}}^\text{curl curl}\)),
<b>double contravariant Piola</b> (\({{symbols.mapping}}^\text{div div}\)) and
<b>covariant-contravariant Piola</b> (\({{symbols.mapping}}^\text{curl div}\))
mappings are defined:
$$\left({{symbols.mapping}}^\text{curl curl}{{symbols.matrix_basis_function}}\right)(\boldsymbol{x})
:={{symbols.jacobian}}^{-T}{{symbols.matrix_basis_function}}({{symbols.geometry_map}}^{-1}(\boldsymbol{x})){{symbols.jacobian}}^{-1}$$
$$\left({{symbols.mapping}}^\text{div div}{{symbols.matrix_basis_function}}\right)(\boldsymbol{x})
:=\frac1{\left(\det {{symbols.jacobian}}\right)^2}{{symbols.jacobian}}{{symbols.matrix_basis_function}}({{symbols.geometry_map}}^{-1}(\boldsymbol{x})){{symbols.jacobian}}^T$$
$$\left({{symbols.mapping}}^\text{curl div}{{symbols.matrix_basis_function}}\right)(\boldsymbol{x})
:=\frac1{\left(\det {{symbols.jacobian}}\right)}{{symbols.jacobian}}^{-T}{{symbols.matrix_basis_function}}({{symbols.geometry_map}}^{-1}(\boldsymbol{x})){{symbols.jacobian}}^T$$

## Variants of finite elements
For many elements, there are a number of different choices that could be made for the functionals
in \({{symbols.dual_basis}}\) that define the element that give rise to an element with the same
key properties. For example, when defining a [Lagrange element](element::lagrange) on a triangle, there are many possible
choices for where exactly to locate the point evaluation functionals.
We refer to a pair of elements as variants of each other if:

* They are defined on the same reference cell \({{symbols.reference}}\);
* They are defined using the same polynomial set \({{symbols.polyset}}\);
* The functionals in \({{symbols.dual_basis}}\) associated with each facet, ridge, and peak of the
  cell, and the push forward/pull back map used lead to the same type of continuity between cells.

Commonly used variants of elements are shown on each element's page.

## The degree of a finite element
There are a few different ways to describe the (polynomial) degree of a finite element:

* The polynomial subdegree is the degree of the highest degree complete polynomial space that is a subspace of this element's polynomial space.
* The polynomial superdegree is the degree of the lowest degree complete polynomial space that is a superspace of this element's polynomial space.
* The Lagrange subdegree is the degree of the highest degree Lagrange space that is a subspace of this element's polynomial space.
* The Lagrange superdegree is the degree of the lowest degree Lagrange space that is a superspace of this element's polynomial space.

On each element's page, the value of these is shown, as well as information about which one is used as the canonical degree of that element.
In general, the polynomial subdegree is used to index every element whenever possible; the numbering on DefElement therefore differs from that used
in some implementations (most notably FEniCS and UFL, where the Lagrange superdegree is used to index the majority of elements).

## Notation
Throughout this website, the notation given here in this section is used.

<table>
<tr><td style='padding-right:10px'>\({{symbols.reference}}\)</td><td>A reference cell</td></tr>
<tr><td style='padding-right:10px'>\({{symbols.polyset}}\)</td><td>A polynomial set</td></tr>
<tr><td style='padding-right:10px'>\({{symbols.dual_basis}}\)</td><td>A dual basis</td></tr>
<tr><td style='padding-right:10px'>\({{symbols.functional}}_i\)</td><td>A functional in the dual basis</td></tr>
<tr><td style='padding-right:10px'>\({{symbols.basis_function}}_i\)</td><td>A scalar basis function</td></tr>
<tr><td style='padding-right:10px'>\({{symbols.vector_basis_function}}_i\)</td><td>A vector basis function</td></tr>
<tr><td style='padding-right:10px'>\({{symbols.matrix_basis_function}}_i\)</td><td>A matrix basis function</td></tr>
<tr><td style='padding-right:10px'>\({{symbols.jacobian}}\)</td><td>Jacobian</td></tr>
<tr><td style='padding-right:10px'>\({{symbols.geometry_map}}\)</td><td>A map from a reference to a cell in a mesh</td></tr>
<tr><td style='padding-right:10px'>\({{symbols.mapping}}\)</td><td>A mapping</td></tr>
<tr><td style='padding-right:10px'>\({{symbols.entity(0)}}_i\)</td><td>The \(i\)th vertex</td></tr>
<tr><td style='padding-right:10px'>\({{symbols.entity(1)}}_i\)</td><td>The \(i\)th edge</td></tr>
<tr><td style='padding-right:10px'>\({{symbols.entity(2)}}_i\)</td><td>The \(i\)th face</td></tr>
<tr><td style='padding-right:10px'>\({{symbols.entity(3)}}_i\)</td><td>The \(i\)th volume</td></tr>
<tr><td style='padding-right:10px'>\(k\)</td><td>Degree of a finite element</td></tr>
<tr><td style='padding-right:10px'>\(d\)</td><td>Topological dimension</td></tr>
<tr><td style='padding-right:10px'>\(d_g\)</td><td>Geometric dimension</td></tr>
<tr><td style='padding-right:10px'>\(r\)</td><td>Exterior derivative order</td></tr>
</table>
