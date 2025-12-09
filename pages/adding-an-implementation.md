--
authors:
  - Scroggs, Matthew W.
--

# Adding an implementation to DefElement

This walkthrough will take you through all the steps involved in adding an implementation to
DefElement.

## simplefem
As an example, this walkthrough will look at adding the
[simplefem](https://github.com/DefElement/simplefem) library to DefElement. simplefem is a simple
example finite element library (that was created in order to be used in this walkthrough): it can
create Lagrange elements on triangles and evaluate their basis functions. For example, the following
snippet will create a degree 3 Lagrange element on a triangle and evaluate its basis function with
index 5 at the point (0.3, 0.1):

```python
import simplefem
import numpy as np

e = simplefem.lagrange_element(3)
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

In order to information about an implementation to DefElement, we must implement three class methods
and set the values of four variables in this class. The first method to implement is `format`:

{{snippet::defelement/implementations/simplefem.py::format}}

{{snippet::defelement/implementations/simplefem.py::example}}

{{snippet::defelement/implementations/simplefem.py::variables}}

{{snippet::defelement/implementations/simplefem.py::verify}}

{{snippet::defelement/implementations/simplefem.py::verificationvariable}}
