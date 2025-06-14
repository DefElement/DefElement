<div id='sideplots' style='float:right;width:220px;padding:10px 0px 20px 40px'>
<div>{{plot::triangle,Raviart-Thomas,0::1}}</div>
<div style='font-size:80%;color:#AAAAAA;text-align:center'>A basis function of a degree 0 [Raviart&ndash;Thomas space](element::raviart-thomas) on a triangle</div>
<div>{{plot::quadrilateral,Q,2::3}}</div>
<div style='font-size:80%;color:#AAAAAA;text-align:center'>A basis function of a degree 2 [Q space](element::lagrange) on a quadrilateral</div>
<div>{{plot::tetrahedron,N1curl,0::1}}</div>
<div style='font-size:80%;color:#AAAAAA;text-align:center'>A basis function of a degree 0 [N&eacute;d&eacute;lec (first kind) space](element::nedelec1) on a tetrahedron</div>
<div>{{plot::hexahedron,Scurl,1::13}}</div>
<div style='font-size:80%;color:#AAAAAA;text-align:center'>A basis function of a degree 1 [Arnold&ndash;Awanou H(curl) space](element::scurl) on a hexahedron</div>
</div>

Welcome to DefElement: an encyclopedia of finite element definitions.

This website contains a collection of definitions of finite elements, 
including commonly used elements such as
[Lagrange](element::lagrange),
[Raviart&ndash;Thomas](element::raviart-thomas),
[N&eacute;d&eacute;lec (first kind)](element::nedelec1),
and
[N&eacute;d&eacute;lec (second kind)](element::nedelec2)
elements,
and more exotic elements such as
[serendipity](element::serendipity),
[Hermite](element::hermite),
[P1-iso-P2](element::p1-iso-p2),
and
[Regge](element::regge)
elements.
DefElement currently contains the definition of {{number-of-elements}} elements.

You can:

* [view the full alphabetical list of elements](index::all)
* [view the elements by category](index::categories)
* [view the elements by reference cell](index::references)
* [view the elements that form complexes](index::families)
* [view the elements by available implementations](index::implementations)
* [view recently added/updated elements](index::recent)
* [view a list of all pages on DefElement](/sitemap.html)

## The finite element method
The finite element method is a numerical method that involves discretising a problem using a finite
dimensional function space. These function spaces are commonly defined using a finite element
on a reference cell to derive basis functions for the space. This website contains a collection
of finite elements, and examples of the basis functions they define.

Following the Ciarlet definition of a finite element, the elements on this website
are defined using a reference cell, a polynomial space, and a set of functionals. Each element's
page describes how these are defined for that element, and gives examples of these and the basis
functions they lead to for a selection of low degree spaces.

You can read a detailed description of how the finite element definitions can be understood
on the [how to understand a finite element page](ciarlet.md).

## Implementations of finite elements
There are a large number of libraries that implement finite elements. On each element's page,
code snippets are provided that can create the element in a selection of these libraries.

For many libraries, DefElement performs verification to check that the implementation of
each element in the library matches the element's definition. The results of the most
recent verification run can be found on the [verification page](/verification).

## Contributing to DefElement
If you find an error or inaccuracy in a DefElement entry, please open
[an issue on GitHub](https://github.com/DefElement/DefElement/issues).
You can also open an issue to suggest a new element that should be added to the database.

Alternatively, you could fork the [DefElement GitHub repo](https://github.com/DefElement/DefElement),
make the changes yourself, and open a pull request. You can find more information about adding
an element to DefElement on the [contributing page](contributing.md).

The functional information and examples on the element pages are generated using
[Symfem](https://github.com/mscroggs/symfem), a symbolic finite element definition library.
Before adding an element to DefElement, it should first be implemented in Symfem.

A list of everyone who has contributed to DefElement can be found on the [contributors page](contributors.md).

## Licensing and reuse
All the information and images on DefElement are licensed under a 
[Creative Commons Attribution 4.0 International (CC BY 4.0) license](https://creativecommons.org/licenses/by/4.0/): this means
that you can reuse them as long as you attribute DefElement.
Full details of the licenses and attributions can be found on the [citing page](citing.md).
