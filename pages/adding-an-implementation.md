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

## Adding snippets to element pages
