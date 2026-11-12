# DefElement

This repo contains code to generate the website
[DefElement: an encylopedia of finite element definitions](https://defelement.org).

The examples included in DefElement are generated using [Symfem](https://github.com/mscroggs/symfem).

## Element URLs for other libraries

Install directly from GitHub, pinning a commit for reproducible docs builds:

```toml
[project.optional-dependencies]
docs = ["defelement @ git+https://github.com/DefElement/defelement.com.git@<commit>"]
```

```python
from defelement import get_urls

get_urls("fiat")["RaviartThomas"]
# ("https://defelement.org/elements/raviart-thomas.html",)
```

`get_urls(library)` maps implementation identifiers to sorted, unique URL tuples.
Identifiers are the names recorded by DefElement, such as FIAT class names;
Firedrake/UFL aliases must first be resolved by their owning library. Multiple
URLs are retained when an identifier implements different elements, such as
`FIAT.Lagrange` for Lagrange and P1-iso-P2. No URL is a default match. Unrecorded
identifiers are absent; libraries with no recorded implementations raise `KeyError`.

The same function supports every library recorded in `elements/*.def` and reads
those definitions from the installed package without network requests.

## Building the website

Before building the website, you must install the required Python dependencies:

```bash
pip3 install -r requirements.txt
```

The html files for the website can be built by running:

```bash
python build.py
```

A version of the website where only some elements are plotted can be built by using the
`--test` input arg. For example, the following can be run to build the website with only
plots for Lagrange and Raviart-Thomas (`lagrange` and `raviart-thomas` are
the filenames of the `.def` files in the `elements` folder that define these
elements):

```bash
python build.py --test lagrange,raviart-thomas
```

## Licensing

The code to generate and test the DefElement website (`defelement/`, `templates/`, `test/`, `build.py`, `verify.py`, `install_implementations.py`)
is released under an [MIT license](LICENSE.txt).

The content of the DefElement website itself (including `data/`, `elements/`, `files/`, `pages/`, `people/`)
is released under a [Creative Commons Attribution 4.0 International (CC BY 4.0) license](LICENSE-CC.txt).

Font Awesome (`files/fontawesome`) is released under a [Font Awesome Free License](files/fontawesome/LICENSE.txt).

## Archive
Archived snapshots of code for building DefElement and website builds can be found at https://doi.org/10.5281/zenodo.17904468
