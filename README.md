# DefElement

|     | Badges |
| --- | ------ |
| Deployment | [![Build and deploy](https://github.com/DefElement/DefElement/actions/workflows/build.yml/badge.svg)](https://github.com/DefElement/DefElement/actions/workflows/build.yml) |
| CI | [![Test and build](https://github.com/DefElement/DefElement/actions/workflows/test-and-build.yml/badge.svg)](https://github.com/DefElement/DefElement/actions/workflows/test-and-build.yml) [![Check dependency versions](https://github.com/DefElement/DefElement/actions/workflows/check_dependency_versions.yml/badge.svg)](https://github.com/DefElement/DefElement/actions/workflows/check_dependency_versions.yml) |
| Verification | [![Verification](https://github.com/DefElement/DefElement/actions/workflows/verification.yml/badge.svg)](https://github.com/DefElement/DefElement/actions/workflows/verification.yml) |
| Archived snapshot | [![Zenodo archive](https://zenodo.org/badge/DOI/10.5281/zenodo.17904469.svg)](https://doi.org/10.5281/zenodo.17904469) |

This repo contains code to generate the website
[DefElement: an encylopedia of finite element definitions](https://defelement.org).

The examples included in DefElement are generated using [Symfem](https://github.com/mscroggs/symfem).

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
