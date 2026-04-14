--
authors:
  - Scroggs, Matthew W.
--

# Verification and JIT

When implementing the functions required for verificiation for libraries without a Python interface,
Python's FFI interface can be used to just-in-time (JIT) compile functions to get the required basis
function values. In order the make this easier, DefElement includes some JIT helper functions:
this pages demonstrates how these helper functions can be used.

## simplefem++
As an example, this walkthrough will look at implementing verification for the
[simplefem++](https://github.com/DefElement/simplefempp) library.
simplefem++ has been created to serve as an illustration library for this walkthrough,
and should not be considered as a fully fledged library.  It only features degree 1 to 3 Lagrange
elements on triangles and can evaluate their basis functions. For example, the following
snippet will create a degree 2 Lagrange element on a triangle and evaluate its basis
function with index 3 at the point (0.3, 0.1):

```cpp
#include <simplefem.h>
#include <vector>
using namespace simplefem;

auto e = lagrange_element(2);
std::vector<double> point(2);
point[0] = 0.3;
point[1] = 0.1;
auto value = e.evaluate(3, point);
```

## `defelement.implementations.jit`

To use DefElement's JIT helpers, you must first import the `defelement.implementations.jit`
submodule:

{{snippet::defelement/implementations/simplefem.py::jit-intro}}

The function `cpp` in the submodule can then be used to JIT compile some C++ code that will
evaluate basis functions. `cpp` can take the following keyword arguments:

* `function`: the C++ that makes up the body of the function.
* `inputs`: a list of inputs to the function. The items in this list should be `ArgType` objects
  which can be created using the functions in
  [`defelement.implementations.jit.argument_types`](https://github.com/DefElement/DefElement/blob/main/defelement/implementations/jit/argument_types.py).
* `outputs`: a list of outputs from the function. Again these should be `ArgType` objects.
  Outputs that are arrays of values will automatically be converted to in/out arguments and
  wrapped as `mdspan`s inside the function. The special command `INIT variable_name;` can be used
  to initialise one of these arguments inside the function body (this is useful when (for example)
  the shape of the array is defined using another object that first needs creating).
* `imports`: a string containing the include statements to include at the start of the C++ file.
* `id`: A unique id to use for caching the built function.
* `packages`: A list of packages that this function relies on. Each package should be a tuple of
  two strings: including `("A", "B")` as a package will lead to `target_link_libraries(...  A::B)`
  being added to the cmake file.

The full implementation of the `verification` function for simplefem++ is as follows:

{{snippet::defelement/implementations/simplefem.py::verificationpp}}

## Supported programming languages

The following programming languages currently have helper functions in
`defelement.implementations.jit`:

<table class="bordered centred">
<thead><tr><td>Language</td><td>Name(s) of helper function(s)</td></tr></thead>
<tr><td>C++</td><td>`cpp`</td></tr>
</table>
