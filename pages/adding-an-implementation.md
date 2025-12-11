--
authors:
  - Scroggs, Matthew W.
--

# Adding an implementation to DefElement

This walkthrough will take you through all the steps involved in adding an implementation to
DefElement.

Detailed documentation of the class methods and variables used in this walkthrough, as well as
other optional method, can be found in the file
[defelement/implementations/core.py](https://github.com/DefElement/DefElement/tree/main/defelement/implementations/core.py).

## simplefem
As an example, this walkthrough will look at adding the
[simplefem](https://github.com/DefElement/simplefem) library to DefElement.
simplefem has been created to serve as an illustration library for this walkthrough, and should not be considered as a fully fledged library. 
It only features Lagrange elements on triangles and can evaluate their basis functions.
For example, the following
snippet will create a Lagrange element on a triangle with 10 basis functions and evaluate its basis
function with index 5 at the point (0.3, 0.1):

```python
import simplefem
import numpy as np

e = simplefem.lagrange_element(10)
value = e.evaluate(5, np.array([0.3, 0.1]))
```

## Adding simplefem snippets to element pages
To add simplefem to DefElement, a file in the folder
[defelement/implementations](https://github.com/DefElement/DefElement/tree/main/defelement/implementations)
must be created. In this case, we called the file
[simplefem.py](https://github.com/DefElement/DefElement/tree/main/defelement/implementations/simplefem.py).
In this file, we begin by importing functionality from the file
[core.py](https://github.com/DefElement/DefElement/tree/main/defelement/implementations/core.py):

{{snippet::defelement/implementations/simplefem.py::intro}}

In order to add information about a finite element library to DefElement, we must implement four class methods
and set the values of four variables in this class.

### `format`
The first method to implement is `format`.
The formatting string and parameters set in DefElement's .def files will be passed into this method.
For simplefem, this method simply returns the format string included in the .def file:

{{snippet::defelement/implementations/simplefem.py::format}}

In the file
[elements/lagrange.def](https://github.com/DefElement/DefElement/tree/main/elements/lagrange.def)
the following lines are included in the `implementations` section:

```
implementations:
  ...
  simplefem:
    equispaced:
      triangle: lagrange_element DEGREEMAP=(k+1)*(k+2)//2
```

Therefore, the `format` class method will be called for an equispaced Lagrange element on a triangle,
with `string="lagrange_element"` and `params={}` (note that `DEGREEMAP` uses the syntax for a
parameter but is not included in `param` due to being a special parameter: we will return to
`DEGREEMAP` in the next section).

The value returned by `format` will be displayed on the element's page. In the case, the
class method returns the string `lagrange_element` (which is the function in simplefem used to create
the element).

### `example_import` and `single_example`
To generate example code that will be displayed on an element's page, DefElement will use the
class methods `example_import` and `single_example`. The class method `example_import` returns the
import statements to include at the start of the example code. The class method `single_example`
returns Python code that will create the element: the inputs to this method are
the string included in the .def file (`name`);
the name of the reference cell for this example (`reference`);
the degree for this example (`degree`); and
the parameters included in the .def file (`params`).
The additional inputs `element` and `example` are the DefElement `Element` object and the raw example
information: these may be needed in some more complex cases.

For simplefem, these class methods are defined as follows:

{{snippet::defelement/implementations/simplefem.py::example}}

The funtion `example_import` gives code to import simplefem. The inputs to class method `single_example`
will be `name="lagrange_element"`, `reference="triangle"`, and `params={}`. The degree used in
DefElement (in this case, the [polynomial subdegree](/ciarlet.html#The+degree+of+a+finite+element) 1, 2, or 3) will be substituted into the `DEGREEMAP`
special parameter as `k` before this method is called (so the values 3, 6, and 10 will be passed in).
In this way, DefElement's notion of degree can be automatically converted to the number of points
input that simplefem uses.

### `version`
The final class method that must be implemented is `version`, which should return the version
number of the implementation library. For simplefem, this is implemented as follows:

{{snippet::defelement/implementations/simplefem.py::version}}

When an implementation can be installed from PyPI, the decorator `pypi_name` can be used.
This decorator will automatically implement the method `version` and set the variable `install`
(as described in the next section). For the ndelement library, for example, `pypi_name` is used as
follows:

{{snippet::defelement/implementations/ndelement.py::pypi_name}}

### Variables
Finally, four variables need to be defined:

* `id` gives the id used to identify this implementation (eg in URLs). This should be all lowercase
  and not contain any special characters.
* `name` gives the name of the implementation as it will appear in text.
* `url` gives the URL of the git repository of the inplementation.
* `install` gives the pip command to install the implementation. Note that this can be omitted
  if the `pypi_name` decorator is used.

For simplefem, these variables are set to the following values. In general, it is preferable for
the install to be done from PyPI rather than via git, but as simplefem is merely an example library
and has no official release, installing via git is used in this case.

{{snippet::defelement/implementations/simplefem.py::variables}}

### Appearance on element page
We have now added everything that we need for an implementation to be included on DefElement.
As simplefem is an example library, it is by default hidden from the
[Lagrange element page](element::lagrange). If it were included, its section on the page would look
like this:

<table class="element-info"><tbody>
<tr><td></td><td></td></tr>
<tr><td><a&nbsp;href=' lists="" implementations="" simplefem.html'="">simplefem</a&nbsp;href='></td><td><code>lagrange_element</code><br><a class="show_eg_link" id="show_simplefem_link" href="javascript:show_simplefem_eg()" style="display:block">↓ Show simplefem examples ↓</a><a class="hide_eg_link" id="hide_simplefem_link" href="javascript:hide_simplefem_eg()" style="display:none">↑ Hide simplefem examples ↑</a><div id="simplefem_eg" style="display:none">Before running this example, you must install <a href="https://github.com/DefElement/simplefem">simplefem</a>:<p class="pcode">pip3 install git+https://github.com/DefElement/simplefem</p>This element can then be created with the following lines of Python:<p class="pcode"><span style="color:#FF8800">#&nbsp;Create&nbsp;Lagrange&nbsp;(equispaced&nbsp;variant)&nbsp;degree&nbsp;10&nbsp;on&nbsp;a&nbsp;triangle</span><br>element&nbsp;=&nbsp;simplefem.lagrange_element(10)</p></div><i class="fa-solid fa-square-check" style="color:#55FF00;font-size:150%;vertical-align:middle"></i> <span style="font-size:80%;vertical-align:middle">This implementation is correct for all the examples below that it supports.</span><div style="display:block;margin-left:30px;font-size:80%;vertical-align:middle" id="simplefem-showverification"><a href="javascript:show_simplefem_verification()">↓ Show more ↓</a></div><div style="display:none;" id="simplefem-hiddenverification"><div style="margin-left:30px;font-size:80%;vertical-align:middle"><a href="javascript:hide_simplefem_verification()">↑ Hide ↑</a></div><div style="margin-left:70px;text-indent:-40px;font-size:80%;vertical-align:middle"><i class="fa-solid fa-square-check" style="color:#55FF00;font-size:150%;vertical-align:middle"></i> <b>Correct</b>: triangle,1,equispaced; triangle,2,equispaced; triangle,3,equispaced</div><div style="margin-left:70px;text-indent:-40px;font-size:80%;vertical-align:middle"><i class="fa-solid fa-square-minus" style="color:#44AAFF;font-size:150%;vertical-align:middle"></i> <b>Not implemented</b>: interval,1,equispaced; interval,2,equispaced; interval,3,equispaced; quadrilateral,1,equispaced; quadrilateral,2,equispaced; quadrilateral,3,equispaced; tetrahedron,1,equispaced; tetrahedron,2,equispaced; hexahedron,1,equispaced; hexahedron,2,equispaced; prism,1,equispaced; prism,2,equispaced; pyramid,1,equispaced; pyramid,2,equispaced; interval,1,gll; interval,2,gll; interval,3,gll; interval,4,gll; quadrilateral,1,gll; quadrilateral,2,gll; interval,1,lobatto; interval,2,lobatto; interval,3,lobatto; quadrilateral,1,lobatto; quadrilateral,2,lobatto; quadrilateral,3,lobatto; hexahedron,1,lobatto; hexahedron,2,lobatto</div></div><script type="text/javascript">
function show_simplefem_verification(){
document.getElementById('simplefem-showverification').style.display = 'none'
document.getElementById('simplefem-hiddenverification').style.display = 'block'
}
function hide_simplefem_verification(){
document.getElementById('simplefem-showverification').style.display = 'block'
document.getElementById('simplefem-hiddenverification').style.display = 'none'
}
</script><div style="font-size:80%;vertical-align:middle;margin-top:5px">Note: This implementation uses an alternative value of degree for this element</div><script type="text/javascript">
function show_simplefem_eg(){
 document.getElementById('show_simplefem_link').style.display='none'
 document.getElementById('hide_simplefem_link').style.display='block'
 document.getElementById('simplefem_eg').style.display='block'
}
function hide_simplefem_eg(){
 document.getElementById('show_simplefem_link').style.display='block'
 document.getElementById('hide_simplefem_link').style.display='none'
 document.getElementById('simplefem_eg').style.display='none'
}
</script></td></tr>
<tr></tr>
</tbody></table>

## Verification
As well as giving information about implementations and code snippets for creating elements,
DefElement is able to [verify](/verification) that the basis functions of elements provided by different
implementations span the same polynomial spaces. If you want your implementation to be verified, you
will need to additionally implement the class method `verify` and set the variable `verification` to
`True`.

The method `verify` takes
the string included in the .def file (`name`);
the name of the reference cell for this example (`reference`);
the degree for this example (`degree`); and
the parameters included in the .def file (`params`).
The additional inputs `element` and `example` are the DefElement `Element` object and the raw example
in case these are needed. The method should return a list of DOFs associated with each entity of each
dimension (as detailed below) and a function that maps a set of points on the DefElement reference
cell to a table of values: this table will be a three-dimensional Numpy array with the value
`table[i][j][k]` giving the `j`th component of the `k`th basis function evalutated at the `i`th
point.

### `verify` for simplefem

We now look in detail at the implementation of this function for simplefem. We begin with the
`def` statement defining the method:

{{snippet::defelement/implementations/simplefem.py::verify1}}

The method begins by importing simplefem and numpy: it is important that these are imported inside
the method so that import errors can be caught when running verification.

{{snippet::defelement/implementations/simplefem.py::verify2}}

The method then uses `getattr` to get the relevant element creation function and creates the element
(`e`). As only one element is implemented in simplefem, `name` will always be equal to
`"lagrange_element"`, but this function has been written with a more general library in mind.

{{snippet::defelement/implementations/simplefem.py::verify3}}

We next make lists of which degrees of freedom (DOFs) are associated with each sub-entity: the
variable `entity_dofs` that is created is a list of lists of lists where
`entity_dofs[i][j]` is a list of DOFs associated with the `j`th subentity of dimension `i`.
This variable will be one of the two value returned by this function.
The numbering of DOFs in simplefem is not the same as in DefElement's examples, so
we do this by looping over the points used to define each basis function and checking
if they're at a vertex or on an edge. Luckily, the ordering of points on each edge and inside
the triangle matches the [ordering used by DefElement](/reference_numbering.html#Triangle), so
these lists do not need to be permuted once created.

{{snippet::defelement/implementations/simplefem.py::verify4}}

Next, we define a function `tabulate` that takes a set of points as an inputs and returns the values
of all of the basis functions of the element at every point. The points input to this function
are points on the [reference cell as used by DefElement](/reference_numbering.html#Triangle) and so
points and function values may need to be mapped if the implementation uses an alternative reference
cell.

DefElement's reference cell has vertices at (0,0), (1,0) and (0,1), while simplefem's reference cell
has vertices at (-1,0), (1,0) and (1,0), so we define `mapped_points` to be the points in simplefem's
reference cell that correspond to the points that are input.

We then loop through each point and each basis function and use `e.evaluate` to evaluate the value
of the basis function at the point.

{{snippet::defelement/implementations/simplefem.py::verify5}}

Finally, we return `entity_dofs` and the function `tabulate` and set the class variable
`verification` to `True`:
{{snippet::defelement/implementations/simplefem.py::verify6}}

{{snippet::defelement/implementations/simplefem.py::verificationvariable}}

### The verification page

As it is an example library, simplefem is hidden from the main verification index pages,
but can be viewed at  [defelement.org/verification/simplefem.html](/verification/simplefem.html).

