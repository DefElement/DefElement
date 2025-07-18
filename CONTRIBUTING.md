# Contributing to DefElement

## Making suggestions

### Reporting mistakes
If you find a mistake in the DefElement database, please report it on the
[issue tracker](https://github.com/DefElement/DefElement/issues/new?assignees=&labels=bug&template=mistake-report.md&title=)
using the *Mistake report* template.

### Suggesting new elements
If you want to suggest a new element to be added to DefElement, suggest it on the
[issue tracker](https://github.com/DefElement/DefElement/issues/new?assignees=&labels=new+element&template=new-element.md&title=Add+%5BNAME%5D+element)
using the *New element* template.

### Suggesting improvements
If you want to suggest a new feature or improvement to DefElement, suggest it on the
[issue tracker](https://github.com/DefElement/DefElement/issues/new?assignees=&labels=feature+request&template=suggest-an-improvement.md&title=)
using the *Suggest an improvement* template.

### Discussion ideas for new features
You can use [GitHub's Discussions](https://github.com/DefElement/DefElement/discussions) to discuss
ideas you have for features (that perhaps aren't fully formed enough yet to make an issue) or to
discuss other people's ideas. You're welcome to also use the Discussions to just chat to other
members of the community.

## Contributing directly

### Submitting a pull request
If you want to directly submit changes to DefElement, you can do this by forking the [DefElement GitHub repository](https://github.com/DefElement/DefElement),
making changes, then submitting a pull request.
If you want to contribute, but are unsure where to start, have a look at the
[issue tracker](https://github.com/DefElement/DefElement/labels/good%20first%20issue) for issues labelled "good first issue".

The functional information and examples on the element pages are generated using
[Symfem](https://github.com/mscroggs/symfem), a symbolic finite element definition library.
Before adding an element to DefElement, it should first be implemented in Symfem.

### Defining an element
Elements in the DefElement database are defined using a yaml file in the `elements/` folder.
The entries in this yaml file are:

<table class='bordered align-left'>
<thead>
<tr><td>Name</td><td>Required</td><td>Description</td></tr>
</thead>
<tr><td>`name`</td><td>{{tick}}</td><td>The name of the element (ascii).</td></tr>
<tr><td>`html&#8209;name`</td><td>{{tick}}</td><td>The name of the element, including HTML special characters.</td></tr>
<tr><td>`reference&#8209;cells`</td><td>{{tick}}</td><td>The reference cell(s) that this finite element can be defined on.</td></tr>
<tr><td>`alt&#8209;names`</td><td></td><td>Alternative (HTML) names of the element.</td></tr>
<tr><td>`legacy&#8209;names`</td><td></td><td>Filenames that have previously been used for this element and/or filenames of elements that were merged into this element. Pages that redirect from the old names to new name will be created if this is set.</td></tr>
<tr><td>`short&#8209;names`</td><td></td><td>Abbreviated names of the element.</td></tr>
<tr><td>`variants`</td><td></td><td>Variants of this element.</td></tr>
<tr><td>`complexes`</td><td></td><td>Any discretiations of complexes that this element is part of.</td></tr>
<tr><td>`dofs`</td><td></td><td>Description of the DOFs of this element.</td></tr>
<tr><td>`ndofs`</td><td></td><td>The number of DOFs the element has and the A-numbers of the [OEIS](http://oeis.org) sequence(s) giving the number of DOFs.</td></tr>
<tr><td>`entity&#8209;ndofs`</td><td></td><td>The number of DOFs the element has per subentity type and the A-numbers of the [OEIS](http://oeis.org) sequence(s) giving the number of DOFs.</td></tr>
<tr><td>`polynomial&#8209;set`</td><td></td><td>The polynomial set of this element. This can use sets defined in the file [`/data/polysets`](https://github.com/DefElement/DefElement/blob/main/data/polysets). Other sets can be given by writing `<k>[LaTeX definition of set]`. Unions of multiple sets can be given, separated by ` && `.</td></tr>
<tr><td>`mixed`</td><td></td><td>If this element is a mixed element, the subelements that it contains.</td></tr>
<tr><td>`mapping`</td><td></td><td>The mapping used to push/pull values foward/back from/to the reference cell.</td></tr>
<tr><td>`sobolev`</td><td></td><td>The Sobolev space the element lives in.</td></tr>
<tr><td>`min&#8209;degree`</td><td></td><td>The minimum degree of the element</td></tr>
<tr><td>`max&#8209;degree`</td><td></td><td>The maximum degree of the element</td></tr>
<tr><td>`polynomial-subdegree`</td><td></td><td>The degree of the highest degree complete polynomial space that is a subspace of this element's polynomial space</td></tr>
<tr><td>`polynomial-superdegree`</td><td></td><td>The degree of the lowest degree complete polynomial space that is a superspace of this element's polynomial space</td></tr>
<tr><td>`lagrange-subdegree`</td><td></td><td>The degree of the highest degree Lagrange space that is a subspace of this element's polynomial space</td></tr>
<tr><td>`lagrange-superdegree`</td><td></td><td>The degree of the lowest degree Lagrange space that is a superspace of this element's polynomial space</td></tr>
<tr><td>`degree`</td><td></td><td>Degree that is use to index this element, should be `polynomial-subdegree`, `polynomial-superdegree`, `lagrange-subdegree`, `lagrange-superdegree`</td></tr>
<tr><td>`examples`</td><td></td><td>Reference cells and degrees to be included in the examples section of the entry.</td></tr>
<tr><td>`notes`</td><td></td><td>Notes about the element.</td></tr>
<tr><td>`references`</td><td></td><td>References to where the element is defined.</td></tr>
<tr><td>`categories`</td><td></td><td>Categories the element belongs to. Categories are defined in the file [`/data/categories`](https://github.com/DefElement/DefElement/blob/main/data/categories).</td></tr>
<tr><td>`implementations`</td><td></td><td>Strings/enum entries/etc to create this element in supported implementations.</td></tr>
</table>

#### Implementations
In the `implementations` fields, parameters can be passed to the implementation using syntax like
this:

```yaml
implementations:
  libraryname: String param_name1=param_value1 param_name2=param_value2
```

There are a few special parameters (written in ALL CAPS) that can be used here:

<table>
<thead>
<tr><td>Parameter</td><td>Purpose</td></tr>
</thead>
<tr><td>`DEGREES`</td><td>A list of degrees for which this element is defined in this implementation, eg `1,2,4:8` denotes that degrees 1 and 2 and 4 to 8 (including 4 but not including 8) are supported. Note that if `DEGREEMAP` is set, the degrees used here should correspond to the DefElement convention, not the degree after the degree map is applied.</td></tr>
<tr><td>`DEGREEMAP`</td><td>A map to apply to the degree used on DefElement to obtain the degree used by this library. The value here will be parsed using Sympy, with the variable `k` equal to the degree (using DefElement's convention).</td></tr>
</table>

### Testing your contribution
When you open a pull request, a series of tests and style checks will run via GitHub Actions.
(You may have to wait for manual approval for these to run.)
These tests and checks must pass before the pull request can be merged.
If the tests and checks fail, you can click on them on the pull request page to see where the failure is happening.

The style checks will check that the Python scripts that generate DefElement pass flake8 checks.
If you've changed these scripts, you can run these checks locally by running:

```bash
python3 -m flake8 defelement build.py test
```

Before you can run the tests or do a test build, you'll need to install DefElement's requirements:

```bash
python3 -m pip install -r requirements.txt
```

The DefElement tests can be run using:

```bash
python3 -m pytest test/
```

To test that DefElement successfully builds, you can pass `--test auto` to the `build.py` script.
This will build the website including examples for a small set of elements, and will take much less time
then building the full website.

```bash
python3 build.py _test_html --test auto --processes 4
```

If you've updated an element, then you can test this element by replacing `auto` with the filename of the element you have edited.
If you've updated multiple elements, you can use multiple filenames separated by commas. For example:

```bash
python3 build.py _test_html --test dpc --processes 4
python3 build.py _test_html --test lagrange,vector-lagrange --processes 4
```

### Adding an implementation
To add a library to the implementations section of DefElement, you must add a file containing to the folder
[`/defelement/implementations`](https://github.com/DefElement/DefElement/blob/main/defelement/implementations).
This file should define a class that is a subclass of [`Implementation`](https://github.com/DefElement/DefElement/blob/main/defelement/implementations/template.py).
This class should include:

<table class='bordered align-left'>
<thead>
<tr><td>Item</td><td>Type</td><td>Use</td></tr>
</thead>
<tr><td>`format`</td><td>method</td><td>This method should take an implementation string and a set of parameters as inputs and return the implementation information for the library, as it will be displayed on each element's page.</td></tr>
<tr><td>`example`</td><td>method</td><td>This method should take a DefElement `Element` object as an input and return a block of Python (as a string) that creates all the examples of that element using the library.</td></tr>
<tr><td>`verify`</td><td>method (optional)</td><td>This method should take a DefElement `Element` object, an example, and a set of points as inputs and returns the element for that example tabulated at the set of points and the number of DOFs associated with each sub-entity as a tuple of tuples. The shape of the first output is `(number of points, value size, number of basis functions)`. These functions are used to [verify](https://defelement.org/verification.html) that the implementation spans the same space as Symfem.</td></tr>
<tr><td>`notes`</td><td>method (optional)</td><td>This method should take a DefElement `Element` object and return a list of notes about the implementation to include on the element's page.</td></tr>
<tr><td>`references`</td><td>method (optional)</td><td>This method should take a DefElement `Element` object and return a list of references relevant to the implementation to include on the element's page.</td></tr>
<tr><td>`id`</td><td>variable</td><td>The unique identifier for your library. This will be used in .def files.</td></tr>
<tr><td>`name`</td><td>variable</td><td>The name of your library.</td></tr>
<tr><td>`install`</td><td>variable</td><td>Code snippet to install you library (preferably using `pip3`)</td></tr>
<tr><td>`url`</td><td>variable</td><td>URL where the source code of your library is avaliable (eg a GitHub link).</td></tr>
<tr><td>`verification`</td><td>variable (optional)</td><td>Should be set to `True` if the `verify` function is implemented.</td></tr>
</table>

Once these steps are done, you can start adding implementation details for your library to
the `implementation` field of elements in the [`elements`](https://github.com/DefElement/DefElement/blob/main/elements)
folder.

## Style guide
When contributing to DefElement, you should follow [the DefElement style guide](https://defelement.org/style-guide.html).

## Adding yourself to the contributors list
Once you have contributed to DefElement, you should add your name and some information about yourself to the [contributors page](https://defelement.org/contributors.html).
To do this, you should add info about yourself to the file [data/contributors](https://github.com/DefElement/DefElement/blob/main/data/contributors). If you wish to include a picture of yourself,
add a square-shaped image to the [pictures/](https://github.com/DefElement/DefElement/blob/main/pictures/) folder.

## Code of conduct
We expect all our contributors to follow our [code of conduct](CODE_OF_CONDUCT.md). Any unacceptable
behaviour can be reported to Matthew (defelement@mscroggs.co.uk).
