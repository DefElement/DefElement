"""Build DefElement website."""

import argparse
import json
import os
import typing
from datetime import datetime

import symfem
import sympy
from symfem import create_element
from webtools.citations import make_bibtex, markup_citation
from webtools.code_markup import python_highlight
from webtools.html import make_html_forwarding_page, make_html_page
from webtools.markup import cap_first, heading, heading_with_self_ref, markup
from webtools.tools import comma_and_join, html_local, insert_author_info, parse_metadata

from defelement import plotting, settings
from defelement.element import Categoriser
from defelement.examples import markup_example
from defelement.families import keys_and_names
from defelement.implementations import implementations, parse_example, verifications
from defelement.markup import insert_links
from defelement.rss import make_rss

start_all = datetime.now()

parser = argparse.ArgumentParser(description="Build defelement.org")
parser.add_argument("destination", metavar="destination", nargs="?",
                    default=None, help="Destination of HTML files.")
parser.add_argument("--test", metavar="test", default=None,
                    help="Builds a version of the website with fewer elements.")
parser.add_argument("--github-token", metavar="github_token", default=None,
                    help="Provide a GitHub token to get update timestamps.")
parser.add_argument("--processes", metavar="processes", default=None,
                    help="The number of processes to run the building of examples on.")
parser.add_argument("--verification-json", metavar="verification_json", default=None,
                    help="Provide a verification JSON.")
parser.add_argument("--no-cache", action="store_true", help="Build without using cache.")

sitemap = {}


def write_html_page(
    path: str, title: typing.Optional[str], content: str,
    extra_head: typing.Optional[str] = None
):
    """Write a HTML page.

    Args:
        path: Page path
        title: Page title
        content: Page content
        extra_head: Extra HTML to include inside <head>
    """
    assert html_local(path) not in sitemap
    if title is not None:
        sitemap[html_local(path)] = title
    with open(path, "w") as f:
        f.write(make_html_page(content, title, extra_head=extra_head))


args = parser.parse_args()
if args.destination is not None:
    settings.set_html_path(args.destination)

if args.no_cache:
    settings.caching = False

if args.processes is not None:
    settings.set_processes(int(args.processes))

if args.github_token is not None:
    settings.set_github_token(args.github_token)

if args.verification_json is not None:
    settings.set_verification_json(args.verification_json)

if args.test is None:
    test_elements = None
elif args.test == "auto":
    test_elements = [
        "buffa-christiansen", "direct-serendipity", "dual", "hellan-herrmann-johnson",
        "hsieh-clough-tocher", "lagrange", "nedelec1", "raviart-thomas", "regge",
        "serendipity", "taylor-hood", "vector-bubble-enriched-Lagrange", "enriched-galerkin"]
else:
    test_elements = args.test.split(",")

# Prepare paths
if os.path.isdir(settings.html_path):
    os.system(f"rm -rf {settings.html_path}")
os.mkdir(settings.html_path)
os.mkdir(settings.htmlelement_path)
os.mkdir(settings.htmlindices_path)
os.mkdir(settings.htmlfamilies_path)
os.mkdir(settings.htmlimg_path)
os.mkdir(os.path.join(settings.html_path, "badges"))

os.system(f"cp -r {settings.dir_path}/people {settings.htmlimg_path}")
os.mkdir(os.path.join(settings.htmlelement_path, "bibtex"))
os.mkdir(os.path.join(settings.htmlelement_path, "examples"))

os.system(f"cp -r {settings.files_path}/* {settings.html_path}")

with open(os.path.join(settings.html_path, "CNAME"), "w") as f:
    f.write("defelement.org")

# Make pages
for file in os.listdir(settings.pages_path):
    if file.endswith(".md"):
        start = datetime.now()
        fname = file[:-3]
        print(f"{fname}.html", end="", flush=True)
        with open(os.path.join(settings.pages_path, file)) as f:
            metadata, content = parse_metadata(f.read())

        if "authors" in metadata:
            content = insert_author_info(content, metadata["authors"], f"{fname}.html")

        content = markup(content)

        write_html_page(os.path.join(settings.html_path, f"{fname}.html"),
                        metadata["title"], content)
        end = datetime.now()
        print(f" (completed in {(end - start).total_seconds():.2f}s)")

# Load categories and reference cells
categoriser = Categoriser()
categoriser.load_categories(os.path.join(settings.data_path, "categories"))
categoriser.load_references(os.path.join(settings.data_path, "references"))
categoriser.load_families(os.path.join(settings.data_path, "families"))

# Load elements from .def files
categoriser.load_folder(settings.element_path)

cdescs = {
    "L2": "Discontinuous.",
    "H1": "Function values are continuous.",
    "H2": "Function values and derivatives are continuous.",
    "H3": "Function values and first and second derivatives are continuous.",
    "H(div)": "Components normal to facets are continuous",
    "H(curl)": "Components tangential to facets are continuous",
    "H(div div)": "Inner products with normals to facets are continuous",
    "H(curl curl)": "Inner products with tangents to facets are continuous",
    "H(curl div)": "Tangent-normal inner products on facets are continuous",
    "H1(div)": "Function values and divergence are continuous.",
    }

VHistoryDict = typing.TypedDict('VHistoryDict', {'date': str, 'pass': int, 'total': int})

verification: typing.Dict[str, typing.Dict[str, typing.Dict[str, typing.List[str]]]] = {}
vhistory: typing.Dict[str, typing.List[VHistoryDict]] = {}
v_date = None
if os.path.isfile(settings.verification_json):
    with open(settings.verification_json) as f:
        v_json = json.load(f)
        verification = v_json["verification"]
        v_date = v_json["metadata"]["date"]
if os.path.isfile(settings.verification_history_json):
    with open(settings.verification_history_json) as f:
        vhistory = json.load(f)

icon_style = "font-size:150%;vertical-align:middle"
icon_style_small = "font-size:80%;vertical-align:middle"
text_style = "font-size:80%;vertical-align:middle"
green_check = ("<i class='fa-solid fa-square-check' style='color:"
               f"{symfem.plotting.Colors.GREEN};{icon_style}'></i>")
orange_check = ("<i class='fa-solid fa-square-xmark' style='color:"
                f"{symfem.plotting.Colors.ORANGE};{icon_style}'></i>")
red_check = ("<i class='fa-solid fa-square-xmark' style='color:"
             f"#FF0000;{icon_style}'></i>")
blue_minus = ("<i class='fa-solid fa-square-minus' style='color:"
              f"{symfem.plotting.Colors.BLUE};{icon_style}'></i>")
green_check_small = green_check.replace(icon_style, icon_style_small)
orange_check_small = orange_check.replace(icon_style, icon_style_small)
red_check_small = red_check.replace(icon_style, icon_style_small)
blue_minus_small = blue_minus.replace(icon_style, icon_style_small)

# Generate element pages
all_examples = []
for e in categoriser.elements:
    print(e.name)
    content = heading_with_self_ref("h1", cap_first(e.html_name))
    element_data = []
    impl = []

    # Link to ciarlet.html
    content += "<p><small><a href='/ciarlet.html'>"
    content += "Click here to read what the information on this page means."
    content += "</a></small></p>"

    # Alternative names
    alt_names = e.alternative_names(include_complexes=False)
    if len(alt_names) > 0:
        element_data.append(("Alternative names", ", ".join(alt_names)))
    c_names = e.complexes()
    if "de-rham" in c_names:
        element_data.append(("De Rham complex families", ", ".join(c_names["de-rham"])))

    # Short names
    short_names = e.short_names()
    if len(short_names) > 0:
        element_data.append(("Abbreviated names", ", ".join(short_names)))

    # Variants
    variants = e.variants()
    if len(variants) > 0:
        element_data.append(("Variants", "<br />".join([insert_links(v) for v in variants])))

    simplex_only = len([
        i for i in e.reference_cells(False)
        if i not in ["point", "interval", "triangle", "tetrahedron"]
    ]) == 0

    if simplex_only:
        degree_names = {
            "polynomial-subdegree": "polynomial subdegree",
            "polynomial-superdegree": "polynomial superdegree",
            "lagrange-subdegree": "polynomial subdegree",
            "lagrange-superdegree": "polynomial superdegree",
        }
    else:
        degree_names = {
            "polynomial-subdegree": "polynomial subdegree",
            "polynomial-superdegree": "polynomial superdegree",
            "lagrange-subdegree": "Lagrange subdegree",
            "lagrange-superdegree": "Lagrange superdegree",
        }
    # Degrees
    if e.degree_convention() is None:
        element_data.append(("Degrees", e.degree_range()))
    else:
        element_data.append((
            "Degrees",
            f"{e.degree_range()}<br />where \\(k\\) is the {degree_names[e.degree_convention()]}"))
    if e.polynomial_subdegree() is not None:
        element_data.append(("Polynomial subdegree", e.polynomial_subdegree()))
    if e.polynomial_superdegree() is not None:
        element_data.append(("Polynomial superdegree", e.polynomial_superdegree()))
    if not simplex_only:
        if e.lagrange_subdegree() is not None:
            element_data.append(("Lagrange subdegree", e.lagrange_subdegree()))
        if e.lagrange_superdegree() is not None:
            element_data.append(("Lagrange superdegree", e.lagrange_superdegree()))

    # Reference cells
    refs = e.reference_cells()
    element_data.append(("Reference cells", ", ".join(refs)))

    # Mixed elements
    if e.is_mixed:
        subelements = e.sub_elements()
        element_data.append(
            ("Definition",
             "This is a mixed element containing these subelements:"
             "<ul>" + "\n".join(subelements) + "</ul>"))

    # Polynomial set
    psets = e.make_polynomial_set_html()
    if len(psets) > 0:
        element_data.append(("Polynomial set", psets))

    # DOFs
    dofs = e.make_dof_descriptions()
    if len(dofs) > 0:
        element_data.append(("DOFs", dofs))

    # Number of DOFs
    ndofs = e.dof_counts()
    if len(ndofs) > 0:
        element_data.append(("Number of DOFs", ndofs))

    # Number of DOFs on subentities
    ndofs = e.entity_dof_counts()
    if len(ndofs) > 0:
        element_data.append(("Number of DOFs<breakable>on subentities", ndofs))

    # Mapping
    mapping = e.mapping()
    if mapping is not None:
        element_data.append(("Mapping", mapping))

    # Continuity
    sobolev = e.sobolev()
    if sobolev is not None:
        if isinstance(sobolev, dict):
            element_data.append(("continuity", "<br />".join([
                f"{cdescs[c]} (\\({n}\\))" for n, c in sobolev.items()])))
        else:
            element_data.append(("continuity", cdescs[sobolev]))

    # Notes
    notes = e.notes
    if isinstance(notes, str):
        notes = [notes]
    if len(notes) > 0:
        element_data.append(
            ("Notes", "<br />\n".join([insert_links(i) for i in notes])))

    # Implementations
    libraries = [
        (i, j.name, j.url, j.install)
        for i, j in implementations.items()
    ]
    libraries.sort(key=lambda i: i[0])
    for codename, libname, url, pip in libraries:
        if e.implemented(codename):
            info = e.list_of_implementation_strings(codename)
            assert libname is not None
            short_info = libname

            if e.has_implementation_examples(codename):
                jscodename = codename.replace('.', '_').replace('-', '_')
                info += (
                    "<br />"
                    f"<a class='show_eg_link' id='show_{jscodename}_link' "
                    f"href='javascript:show_{jscodename}_eg()' style='display:block'>"
                    f"&darr; Show {libname} examples &darr;</a>"
                    f"<a class='hide_eg_link' id='hide_{jscodename}_link' "
                    f"href='javascript:hide_{jscodename}_eg()' style='display:none'>"
                    f"&uarr; Hide {libname} examples &uarr;</a>"
                    f"<div id='{jscodename}_eg' style='display:none'>"
                    f"Before running this example, you must install <a href='{url}'>{libname}</a>")
                if pip is None:
                    info += ". "
                else:
                    info += ":<p class='pcode'>" + pip.replace("\n", "<br />") + "</p>"
                info += "This element can then be created with the following lines of Python:"

                info += "<p class='pcode'>" + python_highlight(
                    e.make_implementation_examples(codename)) + "</p>"
                info += "</div>"
                if codename == "symfem":
                    short_info += f" {green_check_small}"
                    info += (
                        f"{green_check} <span style='{text_style}'>"
                        "This implementation is used to compute the examples below and "
                        "verify other implementations.</span>")
                if e.filename in verification and codename in verification[e.filename]:
                    v = verification[e.filename][codename]
                    if len(v["fail"]) == 0:
                        if len(v["not implemented"]) == 0:
                            short_info += f" {green_check_small}"
                            info += (
                                f"{green_check} <span style='{text_style}'>"
                                "This implementation is correct for all the examples below."
                                "</span>")
                        else:
                            short_info += f" {green_check_small}"
                            info += (
                                f"{green_check} <span style='{text_style}'>"
                                "This implementation is correct for all the examples below "
                                "that it supports."
                                "</span>"
                                f"<div style='display:block;margin-left:30px;{text_style}' "
                                f"id='{jscodename}-showverification'>"
                                f"<a href='javascript:show_{jscodename}_verification()'>"
                                "&darr; Show more &darr;</a></div>"
                                f"<div style='display:none;' id='{jscodename}-hiddenverification'>"
                                f"<div style='margin-left:30px;{text_style}'>"
                                f"<a href='javascript:hide_{jscodename}_verification()'>"
                                "&uarr; Hide &uarr;</a></div>"
                                f"<div style='margin-left:70px;text-indent:-40px;{text_style}'>"
                                f"{green_check} "
                                f"<b>Correct</b>: {'; '.join(v['pass'])}</div>"
                                f"<div style='margin-left:70px;text-indent:-40px;{text_style}'>"
                                f"{blue_minus} "
                                f"<b>Not implemented</b>: {'; '.join(v['not implemented'])}</div>"
                                "</div>"
                                "</div>"
                                "<script type='text/javascript'>\n"
                                f"function show_{jscodename}_verification(){{"
                                "\n"
                                f"document.getElementById('{jscodename}-showverification')"
                                ".style.display = 'none'\n"
                                f"document.getElementById('{jscodename}-hiddenverification')"
                                ".style.display = 'block'\n}\n"
                                f"function hide_{jscodename}_verification(){{"
                                "\n"
                                f"document.getElementById('{jscodename}-showverification')"
                                ".style.display = 'block'\n"
                                f"document.getElementById('{jscodename}-hiddenverification')"
                                ".style.display = 'none'\n}\n</script>")
                    elif len(v["pass"]) > 0:
                        short_info += f" {orange_check_small}"
                        info += (
                            f"{orange_check} <span style='{text_style}'>"
                            "This implementation is correct for some of "
                            "the examples below.</span>"
                            f"<div style='display:block;margin-left:30px;{text_style}' "
                            f"id='{jscodename}-showverification'>"
                            f"<a href='javascript:show_{jscodename}_verification()'>"
                            "&darr; Show more &darr;</a></div>"
                            f"<div style='display:none;' id='{jscodename}-hiddenverification'>"
                            f"<div style='margin-left:30px;{text_style}'>"
                            f"<a href='javascript:hide_{jscodename}_verification()'>"
                            "&uarr; Hide &uarr;</a></div>"
                            f"<div style='margin-left:70px;text-indent:-40px;{text_style}'>"
                            f"{green_check} "
                            f"<b>Correct</b>: {'; '.join(v['pass'])}</div>"
                            f"<div style='margin-left:70px;text-indent:-40px;{text_style}'>"
                            f"{red_check} "
                            f"<b>Incorrect</b>: {'; '.join(v['fail'])}</div>")
                        if len(v["not implemented"]) > 0:
                            short_info += f" {blue_minus_small}"
                            info += (
                                f"<div style='margin-left:70px;text-indent:-40px;{text_style}'>"
                                f"{blue_minus} "
                                f"<b>Not implemented</b>: {'; '.join(v['not implemented'])}</div>"
                                "</div>")
                        info += (
                            "</div>"
                            "<script type='text/javascript'>\n"
                            f"function show_{jscodename}_verification(){{"
                            "\n"
                            f"document.getElementById('{jscodename}-showverification')"
                            ".style.display = 'none'\n"
                            f"document.getElementById('{jscodename}-hiddenverification')"
                            ".style.display = 'block'\n}\n"
                            f"function hide_{jscodename}_verification(){{"
                            "\n"
                            f"document.getElementById('{jscodename}-showverification')"
                            ".style.display = 'block'\n"
                            f"document.getElementById('{jscodename}-hiddenverification')"
                            ".style.display = 'none'\n}\n</script>")
                    else:
                        short_info += f" {red_check_small}"
                        info += (
                            f"{red_check} <span style='{text_style}'>"
                            "This implementation is incorrect for this element.</span>")
                notes = e.implementation_notes(codename)
                if notes is not None:
                    for note in notes:
                        info += f"<div style='{text_style};margin-top:5px'>Note: {note}</div>"

                info += (
                    "<script type='text/javascript'>\n"
                    f"function show_{jscodename}_eg(){{\n"
                    f" document.getElementById('show_{jscodename}_link').style.display='none'\n"
                    f" document.getElementById('hide_{jscodename}_link').style.display='block'\n"
                    f" document.getElementById('{jscodename}_eg').style.display='block'\n"
                    "}\n"
                    f"function hide_{jscodename}_eg(){{\n"
                    f" document.getElementById('show_{jscodename}_link').style.display='block'\n"
                    f" document.getElementById('hide_{jscodename}_link').style.display='none'\n"
                    f" document.getElementById('{jscodename}_eg').style.display='none'\n"
                    "}\n"
                    "</script>")

            impl.append(
                (f"<a href='/lists/implementations/{libname}.html'>{libname}</a>", info, short_info)
            )

    # Categories
    cats = e.categories()
    if len(cats) > 0:
        element_data.append(("Categories", ", ".join(cats)))

    # Write element data
    content += "<table class='element-info'>"
    for i, j in element_data:
        content += f"<tr><td>{i.replace(' ', '&nbsp;').replace('<breakable>', ' ')}</td>"
        content += f"<td>{j}</td></tr>"
    content += "</table>"

    # Write implementations
    if len(impl) > 0:
        content += heading_with_self_ref("h2", "Implementations")
        content += "This element is implemented in "
        content += comma_and_join([f"<span style='white-space:nowrap'>{i[2]}</span>" for i in impl])
        content += "."
        content += ("<a class='show_eg_link' id='implementation-more-link' "
                    "href='javascript:show_more_impl()' style='display:block'>"
                    "&darr; Show implementation detail &darr;</a>")
        content += (
            "<script type='text/javascript'>\n"
            "function show_more_impl(){\n"
            " document.getElementById('implementation-more-link').style.display='none'\n"
            " document.getElementById('implementation-more').style.display='block'\n"
            "}\n"
            "function hide_more_impl(){\n"
            " document.getElementById('implementation-more-link').style.display='block'\n"
            " document.getElementById('implementation-more').style.display='none'\n"
            "}\n"
            "</script>")
        content += "<div id='implementation-more' style='display:none'>"
        content += ("<a class='show_eg_link' "
                    "href='javascript:hide_more_impl()' style='display:block'>"
                    "&uarr; Hide implementation detail &uarr;</a>")
        content += "<table class='element-info'>"
        for i, j, _ in impl:
            content += f"<tr><td>{i.replace(' ', '&nbsp;')}</td><td>{j}</td></tr>"
        content += "</table></div>"

    # Write examples using symfem
    if e.has_examples:
        element_examples = []

        if test_elements is None or e.filename in test_elements:
            assert e.implemented("symfem")

            for eg in e.examples:
                cell, degree, variant, kwargs = parse_example(eg)
                symfem_name, _, params = e.get_implementation_string("symfem", cell, None, variant)

                fname = f"{cell}-{e.filename}"
                if variant is not None:
                    fname += f"-{variant}"
                fname += f"-{degree}.html"
                for s in " ()":
                    fname = fname.replace(s, "-")

                if "DEGREEMAP" in params:
                    symfem_degree = int(
                        sympy.S(params["DEGREEMAP"]).subs(sympy.Symbol("k"), degree))
                else:
                    symfem_degree = degree
                name = f"{cell}<br />degree {degree}"
                if variant is not None:
                    name += f"<br />{e.variant_name(variant)} variant"
                for key, value in kwargs.items():
                    name += f"<br />{key}={str(value).replace(' ', '&nbsp;')}"

                eginfo = {
                    "name": name, "args": [cell, symfem_name, symfem_degree], "kwargs": kwargs,
                    "html_name": e.html_name, "element_filename": e.html_filename,
                    "filename": fname, "url": f"/elements/examples/{fname}"}
                if "variant" in params:
                    eginfo["kwargs"]["variant"] = params["variant"]
                if "legacy-names" in e.data:
                    eginfo["legacy-filenames"] = [
                        fname.replace(e.filename, i) for i in e.data["legacy-names"]
                    ]
                all_examples.append(eginfo)
                element_examples.append(eginfo)

        if len(element_examples) > 0:
            content += heading_with_self_ref("h2", "Examples")
            content += "<table class='element-info'>"
            for eg in element_examples:
                element = create_element(*eg['args'], **eg['kwargs'])
                content += (
                    f"<tr><td>{eg['name']}</td><td><center><a href='{eg['url']}'>"
                    f"{plotting.plot_dof_diagram(element, link=False)}"
                    "<br /><small>(click to view basis functions)</small></a></center></td></tr>")
            content += "</table>"

    # Write references section
    refs = e.references()
    if len(refs) > 0:
        content += heading_with_self_ref("h2", "References")
        content += "<ul class='citations'>\n"
        for rindex, r in enumerate(refs):
            content += f"<li>{markup_citation(r)}"
            content += f" [<a href='/elements/bibtex/{e.filename}-{rindex}.bib'>BibTeX</a>]</li>\n"
            with open(os.path.join(settings.htmlelement_path,
                                   f"bibtex/{e.filename}-{rindex}.bib"), "w") as f:
                f.write(make_bibtex(f"{e.filename}-{rindex}", r))
        content += "</ul>"

    # Write created and updated dates
    if e.created is not None:
        content += heading_with_self_ref("h2", "DefElement stats")
        content += "<table class='element-info'>"
        content += f"<tr><td>Element&nbsp;added</td><td>{e.created.strftime('%d %B %Y')}</td></tr>"
        content += "<tr><td>Element&nbsp;last&nbsp;updated</td>"
        content += f"<td>{e.modified.strftime('%d %B %Y')}</td></tr>"
        content += "</table>"

    # Write file
    write_html_page(os.path.join(settings.htmlelement_path, e.html_filename),
                    e.html_name, content)

    # Make redirects from legacy filenames
    for fname in e.legacy_filenames:
        with open(os.path.join(settings.htmlelement_path, f"{fname}.html"), "w") as f:
            f.write(make_html_forwarding_page(f"/elements/{e.html_filename}"))

# Verification badges
img = "data:image/png;base64,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"  # noqa: E501
badges = os.path.join(settings.html_path, "badges")
for i in verifications:
    if i != "symfem":
        good = 0
        total = 0
        for ver in verification.values():
            if i in ver:
                good += len(ver[i]["pass"])
                total += len(ver[i]["pass"]) + len(ver[i]["fail"])
        proportion = f"{good} / {total}"
        if good == total:
            col = symfem.plotting.Colors.GREEN
        elif good < total / 2:
            col = "#FF0000"
        else:
            col = symfem.plotting.Colors.ORANGE
        twidth = 50 + 70 * (len(proportion) - 2)
        width = 840 + 90 + twidth
        svgwidth = width // 10 if width % 10 == 0 else width / 10
        with open(os.path.join(badges, f"{i}.svg"), "w") as f:
            f.write(
                f"<svg width=\"{svgwidth}\" height=\"20\" viewBox=\"0 0 {width} 200\" "
                "xmlns=\"http://www.w3.org/2000/svg\" "
                "xmlns:xlink=\"http://www.w3.org/1999/xlink\" role=\"img\" "
                f"aria-label=\"DefElement verification: {proportion}\">\n"
                f"<title>DefElement verification: {proportion}</title>\n"
                "<linearGradient id=\"NcgeH\" x2=\"0\" y2=\"100%\">\n"
                "<stop offset=\"0\" stop-opacity=\".1\" stop-color=\"#EEE\"/>\n"
                "<stop offset=\"1\" stop-opacity=\".1\"/>\n</linearGradient>\n"
                f"<mask id=\"SeeOV\"><rect width=\"{width}\" height=\"200\" rx=\"30\" "
                "fill=\"#FFF\"/></mask>\n<g mask=\"url(#SeeOV)\">\n"
                "<rect width=\"840\" height=\"200\" fill=\"#555\"/>\n"
                f"<rect width=\"{twidth + 90}\" height=\"200\" fill=\"{col}\" x=\"840\"/>\n"
                f"<rect width=\"{width}\" height=\"200\" fill=\"url(#NcgeH)\"/>\n</g>\n"
                "<g aria-hidden=\"true\" fill=\"#fff\" text-anchor=\"start\" "
                "font-family=\"Verdana,DejaVu Sans,sans-serif\" font-size=\"110\">\n"
                "<text x=\"190\" y=\"148\" textLength=\"610\" fill=\"#000\" opacity=\"0.25\">"
                "verification</text>\n"
                "<text x=\"180\" y=\"138\" textLength=\"610\">verification</text>\n"
                f"<text x=\"895\" y=\"148\" textLength=\"{twidth}\" fill=\"#000\" opacity=\"0.25\">"
                f"{proportion}</text>\n"
                f"<text x=\"885\" y=\"138\" textLength=\"{twidth}\">{proportion}</text>\n</g>\n"
                f"<image x=\"40\" y=\"35\" width=\"100\" height=\"130\" xlink:href=\"{img}\"/>\n"
                "</svg>")
with open(os.path.join(badges, "symfem.svg"), "w") as f:
    f.write(
        f"<svg width=\"186.6\" height=\"20\" viewBox=\"0 0 1866 200\" "
        "xmlns=\"http://www.w3.org/2000/svg\" "
        "xmlns:xlink=\"http://www.w3.org/1999/xlink\" role=\"img\" "
        "aria-label=\"DefElement: used as verification baseline\">\n"
        "<title>DefElement: used as verification baseline</title>\n"
        "<linearGradient id=\"NcgeH\" x2=\"0\" y2=\"100%\">\n"
        "<stop offset=\"0\" stop-opacity=\".1\" stop-color=\"#EEE\"/>\n"
        "<stop offset=\"1\" stop-opacity=\".1\"/>\n</linearGradient>\n"
        f"<mask id=\"SeeOV\"><rect width=\"1866\" height=\"200\" rx=\"30\" fill=\"#FFF\"/></mask>\n"
        "<g mask=\"url(#SeeOV)\">\n<rect width=\"200\" height=\"200\" fill=\"#555\"/>\n"
        f"<rect width=\"1666\" height=\"200\" fill=\"{symfem.plotting.Colors.GREEN}\" x=\"200\"/>\n"
        f"<rect width=\"1866\" height=\"200\" fill=\"url(#NcgeH)\"/>\n</g>\n"
        "<g aria-hidden=\"true\" fill=\"#fff\" text-anchor=\"start\" "
        "font-family=\"Verdana,DejaVu Sans,sans-serif\" font-size=\"110\">\n"
        f"<text x=\"255\" y=\"148\" textLength=\"1566\" fill=\"#000\" opacity=\"0.25\">"
        f"used as verification baseline</text>\n"
        f"<text x=\"245\" y=\"138\" textLength=\"1566\">used as verification baseline</text>\n</g>"
        f"\n<image x=\"40\" y=\"35\" width=\"100\" height=\"130\" xlink:href=\"{img}\"/>\n"
        "</svg>")

# Make verification pages
os.mkdir(os.path.join(settings.html_path, "verification"))

impl_content = {
    i: ""
    for i in verifications
    if i != "symfem"
}
for i in impl_content:
    title = f"{implementations[i].name} verification"
    if i in vhistory:
        good = vhistory[i][-1]["pass"]
        total = vhistory[i][-1]["total"]
        if good == total:
            col = symfem.plotting.Colors.GREEN
        elif good < total / 2:
            col = "#FF0000"
        else:
            col = symfem.plotting.Colors.ORANGE
        title += (
            "<span class='verification-total' "
            f"style='background-color:{col};margin-left:30px'>{good} / {total}</span>"
        )
    impl_content[i] += heading("h1", title)

content = heading_with_self_ref("h1", "Verification")
long_content = heading_with_self_ref("h1", "Verification: full detail")
if v_date is not None:
    year, month, day = [int(i) for i in v_date.split("-")]
    monthname = ["Zeromber", "January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"][month]
    updated = f"<small>Last updated: {day} {monthname} {year}</small><br /><br />"
    content += updated
    long_content += updated
    for i in impl_content:
        impl_content[i] += updated

for i in impl_content:
    if i in vhistory:
        hist = vhistory[i]
        impl_content[i] += (
            "<div id='verification-plot'></div>"
            "<script type='text/javascript'>\n")

        impl_content[i] += (
            "var vpassing = {\n"
            "  x: [")
        impl_content[i] += ",".join(f"\"{i['date']}\"" for i in hist)
        impl_content[i] += (
            "],\n"
            "  y: [")
        impl_content[i] += ",".join(f"\"{i['pass']}\"" for i in hist)
        impl_content[i] += (
            "],\n"
            "  type: 'scatter',\n"
            "  mode: 'lines',\n"
            "  name: \"Number of elements with passing verification\"\n,"
            "  line: {\n"
            f"    color: '{symfem.plotting.Colors.GREEN}',\n"
            "    width: 2"
            "  }\n"
            "};\n")

        impl_content[i] += (
            "var vtotal = {\n"
            "  x: [")
        impl_content[i] += ",".join(f"\"{i['date']}\"" for i in hist)
        impl_content[i] += (
            "],\n"
            "  y: [")
        impl_content[i] += ",".join(f"\"{i['total']}\"" for i in hist)
        impl_content[i] += (
            "],\n"
            "  type: 'scatter',\n"
            "  mode: 'lines',\n"
            "  name: \"Number of elements implemented\"\n,"
            "  line: {\n"
            "    dash: 'dash',\n"
            "    color: '#000000',\n"
            "    width: 3\n"
            "  }\n"
            "};\n")

        plotme = "vtotal, vpassing"

        green_hist = [h for h in hist if h["pass"] == h["total"]]
        if len(green_hist) > 0:
            impl_content[i] += (
                "var vpassing_green = {\n"
                "  x: [")
            impl_content[i] += ",".join(f"\"{i['date']}\"" for i in green_hist)
            impl_content[i] += (
                "],\n"
                "  y: [")
            impl_content[i] += ",".join(f"\"{i['pass']}\"" for i in green_hist)
            impl_content[i] += (
                "],\n"
                "  type: 'scatter',\n"
                "  mode: 'markers',\n"
                "  marker: {\n"
                f"    color: '{symfem.plotting.Colors.GREEN}',\n"
                "    size: 8"
                "  }\n"
                "};\n")
            plotme += ", vpassing_green"

        amber_hist = [h for h in hist if h["total"] / 2 <= h["pass"] < h["total"]]
        if len(amber_hist) > 0:
            impl_content[i] += (
                "var vpassing_amber = {\n"
                "  x: [")
            impl_content[i] += ",".join(f"\"{i['date']}\"" for i in amber_hist)
            impl_content[i] += (
                "],\n"
                "  y: [")
            impl_content[i] += ",".join(f"\"{i['pass']}\"" for i in amber_hist)
            impl_content[i] += (
                "],\n"
                "  type: 'scatter',\n"
                "  mode: 'markers',\n"
                "  marker: {\n"
                f"    color: '{symfem.plotting.Colors.ORANGE}',\n"
                "    size: 8"
                "  }\n"
                "};\n")
            plotme += ", vpassing_amber"

        red_hist = [h for h in hist if h["pass"] < h["total"] / 2]
        if len(red_hist) > 0:
            impl_content[i] += (
                "var vpassing_red = {\n"
                "  x: [")
            impl_content[i] += ",".join(f"\"{i['date']}\"" for i in red_hist)
            impl_content[i] += (
                "],\n"
                "  y: [")
            impl_content[i] += ",".join(f"\"{i['pass']}\"" for i in red_hist)
            impl_content[i] += (
                "],\n"
                "  type: 'scatter',\n"
                "  mode: 'markers',\n"
                "  marker: {\n"
                "    color: '#FF0000',\n"
                "    size: 8"
                "  }\n"
                "};\n")
            plotme += ", vpassing_red"

        impl_content[i] += (
            "var layout = {\n"
            "  showlegend: false,\n"
            "  height: 450,\n"
            "  xaxis: {title: 'Date'},\n"
            "  yaxis: {title: 'Number of elements', rangemode: 'tozero'},\n"
            "  margin: {t: 15}\n"
            "};\n"
            f"Plotly.newPlot('verification-plot', [{plotme}], layout);"
            "</script>"
        )

        impl_content[i] += "</script>"
        impl_content[i] += (
            "The plot above shows the number of elements passing verificiation (green line) "
            "out of the number of elements being verified (dashed black line) over time."
        )
        impl_content[i] += "<br /><br />"

content += "<table style='margin:auto' class='bordered align-left'>"
content += "<thead>"
content += "<tr><td>Element</td>"
long_content += "<table style='margin:auto' class='bordered align-left'>"
long_content += "<thead>"
long_content += "<tr><td>Element</td><td>Example</td>"
for i in impl_content:
    impl_content[i] += (
        "<table style='margin:auto' class='bordered align-left'>"
        "<thead>"
        "<tr><td>Element</td><td>Example</td><td></td></tr>"
        "</thead>")
vs = []
for i in verifications:
    if i != "symfem":
        vs.append(i)
        content += f"<td><a href='/verification/{i}.html'>{implementations[i].name}</a></td>"
        long_content += f"<td><a href='/verification/{i}.html'>{implementations[i].name}</a></td>"
content += "</tr></thead>"
long_content += "</tr></thead>"
rows = []
for e in categoriser.elements:
    n = 0
    row = "<tr>"
    row += f"<td><a href='/elements/{e.filename}.html'>{e.html_name}</a></td>"
    for i in vs:
        row += "<td>"
        if e.filename in verification and i in verification[e.filename]:
            result = verification[e.filename][i]
            if len(result["pass"]) > 0 or len(result["fail"]) > 0:
                n += 1
                if len(result["fail"]) == 0:
                    row += green_check
                elif len(result["pass"]) > 0:
                    row += orange_check
                else:
                    row += red_check
        row += "</td>"
    row += "</tr>"

    examples = []
    if e.filename in verification:
        for vv in verification[e.filename].values():
            for egs in vv.values():
                for eg in egs:
                    if eg not in examples:
                        examples.append(eg)
    sorted_examples = []
    for cell in [
        "interval", "triangle", "quadrilateral", "tetrahedron", "hexahedron",
        "prism", "pyramid", "dual"
    ]:
        sorted_examples += sorted([i for i in examples if i.startswith(cell)],
                                  key=lambda i: ",".join(i.split(",")[:0:-1]))
    assert len(examples) == len(sorted_examples)
    long_row = ""
    impl_rows: typing.Dict[str, typing.List[str]] = {i: [] for i in impl_content}
    for eg in sorted_examples:
        long_row += "<tr>"
        if long_row == "<tr>":
            long_row += (f"<td rowspan='{len(sorted_examples)}'>"
                         f"<a href='/elements/{e.filename}.html'>{e.html_name}</a></td>")
        long_row += f"<td style='font-size:80%'>{eg}</td>"
        for i in vs:
            long_row += "<td>"
            if e.filename in verification and i in verification[e.filename]:
                result = verification[e.filename][i]
                if eg in result["pass"]:
                    impl_rows[i].append(
                        f"<td style='font-size:80%'>{eg}</td><td>{green_check}</td>")
                    long_row += green_check
                elif eg in result["fail"]:
                    long_row += red_check
                    impl_rows[i].append(
                        f"<td style='font-size:80%'>{eg}</td><td>{red_check}</td>")
                else:
                    long_row += blue_minus
            else:
                long_row += blue_minus
            long_row += "</td>"
        long_row += "</tr>"

    for i, i_rows in impl_rows.items():
        if len(i_rows) > 0:
            impl_content[i] += (
                f"<tr><td rowspan='{len(i_rows)}'>"
                f"<a href='/elements/{e.filename}.html'>{e.html_name}</a></td>")
            impl_content[i] += "</tr><tr>".join(i_rows)
            impl_content[i] += "</tr>"

    rows.append((row, long_row, n))
rows.sort(key=lambda i: -i[2])
for r in rows:
    if r[2] > 0:
        content += r[0]
        long_content += r[1]

c = (
    "</table>"
    "<br /><br />"
    "For each element in the table above, the verification test passes for an example if:"
    "<ul>"
    "<li>The element's basis functions span the same space as Symfem.</li>"
    "<li>The number of DOFs associated with each sub-entity of the cell is the same as Symfem.</li>"
    "<li>The element has the same continuity between cells as Symfem.</li>"
    "</ul>"
    "The symbols in the table have the following meaning:")
content += c
content += (
    "<table style='margin:auto' class='bordered align-left'>"
    f"<tr><td>{green_check}</td><td>Verification passes from all the examples on the element's page"
    "</td></tr>"
    f"<tr><td>{orange_check}</td><td>Verification passes for some examples, but not all</td></tr>"
    f"<tr><td>{red_check}</td><td>Verification fails for all examples</td></tr>"
    "</table>"
    "<br /><br />You can view more details of which examples pass and fail on the "
    "<a href='/verification/detailed.html'>verification with full detail page</a>.")
long_content += c
long_content += (
    "<table style='margin:auto' class='bordered align-left'>"
    f"<tr><td>{green_check}</td><td>Verification passes</td></tr>"
    f"<tr><td>{red_check}</td><td>Verification fails</td></tr>"
    f"<tr><td>{blue_minus}</td><td>Example not implemented</td></tr>"
    "</table>"
    "<br /><br />You can view a summarised version of this information on the "
    "<a href='/verification/index.html'>verification page</a>.")
for i in impl_content:
    impl_content[i] += c
    impl_content[i] += (
        "<table style='margin:auto' class='bordered align-left'>"
        f"<tr><td>{green_check}</td><td>Verification passes</td></tr>"
        f"<tr><td>{red_check}</td><td>Verification fails</td></tr>"
        "</table>"
        "<br /><br />You can information about verification of other libraries on the "
        "<a href='/verification/index.html'>verification page</a>.")
if os.path.isfile(settings.verification_json):
    os.system(f"cp {settings.verification_json} {settings.html_path}/verification.json")
    c = ("<br /><br />The verification data is also available "
         "<a href='/verification.json' target='new'>in JSON format</a>.")
    content += c
    long_content += c

c = heading_with_self_ref("h2", "Verification GitHub badges")
c += "<table class='bordered align-left'>"
c += "<thead><tr><td>Implementation</td><td>Badge</td><td>Markdown</td></tr></thead>"
for i in verifications:
    if i == "symfem":
        url = "https://defelement.org/verification/"
    else:
        url = f"https://defelement.org/verification/{i}.html"
    c += (
        "<tr>"
        f"<td>{implementations[i].name}</td>"
        f"<td><a href='{url}'><img src='/badges/{i}.svg'></a></td>"
        "<td style='font-size:80%;font-family:monospace'>"
        f"[![DefElement verification](https://defelement.org/badges/{i}.svg)]"
        f"({url})</td>"
        "</tr>")
    if i in impl_content:
        impl_content[i] += heading_with_self_ref("h2", "Verification GitHub badge")
        impl_content[i] += (
            "<table class='bordered align-left'>"
            "<thead><tr><td>Badge</td><td>Markdown</td></tr></thead>"
            "<tr>"
            f"<td><img src='/badges/{i}.svg'></td>"
            "<td style='font-size:80%;font-family:monospace'>"
            f"[![DefElement verification](https://defelement.org/badges/{i}.svg)]"
            f"(https://defelement.org/verification/{i}.html)</td>"
            "</tr>"
            "</table>")

c += "</table>"
content += c
long_content += c
write_html_page(os.path.join(settings.html_path, "verification/index.html"),
                "Verification", content)
write_html_page(os.path.join(settings.html_path, "verification/detailed.html"),
                "Verification: full detail", long_content)
with open(os.path.join(settings.html_path, "verification.html"), "w") as f:
    f.write(make_html_forwarding_page("/verification/"))

for i in verifications:
    if i != "symfem":
        write_html_page(
            os.path.join(settings.html_path, f"verification/{i}.html"),
            f"{implementations[i].name} verification", impl_content[i],
            extra_head=(
                "<script src='https://cdn.plot.ly/plotly-2.27.0.min.js' charset='utf-8' "
                "type='text/javascript'></script>"))


def build_examples(egs: typing.List[typing.Dict[str, typing.Any]], process: str = ""):
    """Build examples.

    Args:
        egs: Examples
        process: String to print on this process
    """
    for eg in egs:
        start = datetime.now()

        element = create_element(*eg['args'], **eg['kwargs'])

        markup_example(
            element, eg['html_name'], f"/elements/{eg['element_filename']}",
            eg['filename'], eg['legacy-filenames'] if "legacy-filenames" in eg else [])

        end = datetime.now()
        print(f"  {process}{eg['args'][0]} {eg['args'][1]} {eg['args'][2]}"
              f" (completed in {(end - start).total_seconds():.2f}s)", flush=True)


# Make example pages
print("Making examples")
if settings.processes == 1:
    build_examples(all_examples)
else:
    import multiprocessing

    p = settings.processes
    n_egs = len(all_examples)

    jobs = []
    for pindex in range(p):
        process = multiprocessing.Process(
            target=build_examples,
            args=(all_examples[n_egs * pindex // p: n_egs * (pindex + 1) // p], f"[{pindex}] ")
        )
        jobs.append(process)

    for job in jobs:
        job.start()

    for job in jobs:
        job.join()

    for job in jobs:
        assert job.exitcode == 0

# Index page
content = heading_with_self_ref("h1", "Index of elements")
# Generate filtering Javascript
content += "<script type='text/javascript'>\n"
content += "function do_filter_refall(){\n"
content += "    if(document.getElementById('check-ref-all').checked){\n"
for r in categoriser.references:
    content += f"        document.getElementById('check-ref-{r}').checked = false\n"
content += "    }\n"
content += "    do_filter()\n"
content += "}\n"
content += "function do_filter_catall(){\n"
content += "    if(document.getElementById('check-cat-all').checked){\n"
for c in categoriser.categories:
    content += f"        document.getElementById('check-cat-{c}').checked = false\n"
content += "    }\n"
content += "    do_filter()\n"
content += "}\n"
content += "function do_filter_cat(){\n"
content += "    if(document.getElementById('check-cat-all').checked){\n"
content += "        if("
content += " || ".join([f"document.getElementById('check-cat-{c}').checked"
                        for c in categoriser.categories])
content += "){\n"
content += "            document.getElementById('check-cat-all').checked = false\n"
content += "        }\n"
content += "    }\n"
content += "    do_filter()\n"
content += "}\n"
content += "function do_filter_ref(){\n"
content += "    if(document.getElementById('check-ref-all').checked){\n"
content += "        if("
content += " || ".join([f"document.getElementById('check-ref-{r}').checked"
                        for r in categoriser.references])
content += "){\n"
content += "            document.getElementById('check-ref-all').checked = false\n"
content += "        }\n"
content += "    }\n"
content += "    do_filter()\n"
content += "}\n"
content += "function do_filter(){\n"
content += "    var els = document.getElementsByClassName('element-on-list')\n"
content += "    for(var i=0; i < els.length; i++){\n"
content += "        var ref_show = false\n"
content += "        if(document.getElementById('check-ref-all').checked){\n"
content += "            ref_show = true\n"
content += "        } else {\n"
for r in categoriser.references:

    content += f"            if(document.getElementById('check-ref-{r}').checked"
    content += f" && els[i].id.indexOf('ref-{r}') != -1){{ref_show = true}}\n"
content += "        }\n"
content += "        var cat_show = false\n"
content += "        if(document.getElementById('check-cat-all').checked){\n"
content += "            cat_show = true\n"
content += "        } else {\n"
for c in categoriser.categories:

    content += f"            if(document.getElementById('check-cat-{c}').checked"
    content += f" && els[i].id.indexOf('cat-{c}') != -1){{cat_show = true}}\n"
content += "        }\n"
content += "        var name_show = true\n"
content += "        if(!document.getElementById('show-main-names').checked"
content += " && els[i].id.indexOf('name-main') != -1){\n"
content += "            name_show = false\n"
content += "        }\n"
content += "        if(!document.getElementById('show-alt-names').checked"
content += " && els[i].id.indexOf('name-alt') != -1){\n"
content += "            name_show = false\n"
content += "        }\n"
content += "        if(!document.getElementById('show-abrv-names').checked"
content += " && els[i].id.indexOf('name-abrv') != -1){\n"
content += "            name_show = false\n"
content += "        }\n"
content += "        if(cat_show && ref_show && name_show){\n"
content += "            els[i].style.display='block'\n"
content += "        } else {\n"
content += "            els[i].style.display='none'\n"
content += "        }\n"
content += "    }\n"
content += "}\n"
content += "function show_filtering(){\n"
content += "    document.getElementById('show-flink').style.display='none'\n"
content += "    document.getElementById('hide-flink').style.display='block'\n"
content += "    document.getElementById('the-filters').style.display='block'\n"
content += "}\n"
content += "function hide_filtering(){\n"
content += "    document.getElementById('show-flink').style.display='block'\n"
content += "    document.getElementById('hide-flink').style.display='none'\n"
content += "    document.getElementById('the-filters').style.display='none'\n"
content += "}\n"
content += "</script>"
content += "<a href='javascript:show_filtering()' id='show-flink' style='display:block'"
content += ">&darr; Show filters &darr;</a>\n"
content += "<a href='javascript:hide_filtering()' id='hide-flink' style='display:none'"
content += ">&uarr; Hide filters &uarr;</a>\n"
content += "<table id='the-filters' class='filters' style='display:none'>"
content += (
    "<tr><td>Alternative&nbsp;names</td><td>"
    "<label><input type='checkbox' id='show-main-names' checked onchange='do_filter()'>"
    "&nbsp;Show main names</label> "
    "<label><input type='checkbox' id='show-alt-names' onchange='do_filter()'>"
    "&nbsp;Show alternative names</label> "
    "<label><input type='checkbox' id='show-abrv-names' onchange='do_filter()'>"
    "&nbsp;Show abbreviated names</label> "
    "</td></tr>")
content += "<tr><td>Reference&nbsp;cells</td><td>"
content += "<label><input type='checkbox' checked id='check-ref-all' onchange='do_filter_refall()'"
content += ">&nbsp;show all</label> "
for r in categoriser.references:
    content += f"<label><input type='checkbox' id='check-ref-{r}' onchange='do_filter_ref()'"
    content += f">&nbsp;{r}</label> "
content += "</td></tr>"
content += "<tr><td>Categories</td><td>"
content += "<label><input type='checkbox' checked id='check-cat-all'onchange='do_filter_catall()'"
content += ">&nbsp;show all</label> "
for c in categoriser.categories:
    content += f"<label><input type='checkbox' id='check-cat-{c}'onchange='do_filter_cat()'"
    content += f">&nbsp;{categoriser.get_category_name(c)}</label> "
content += "</td></tr>"
content += "</table>\n"
# Write element list
elementlist = []
for e in categoriser.elements:
    id = " ".join([f"ref-{r}" for r in e.reference_cells(False)]
                  + [f"cat-{c}" for c in e.categories(False, False)])
    elementlist.append((e.html_name.lower(),
                        f"<li class='element-on-list' id='{id} name-main'>"
                        f"<a href='/elements/{e.html_filename}'>{e.html_name}</a></li>"))
    for name in e.alternative_names(False, False, False, True):
        elementlist.append((name.lower(),
                            f"<li class='element-on-list' id='{id} name-alt'>"
                            f"<a href='/elements/{e.html_filename}'>{name}</a></li>"))
    for name in e.short_names(False):
        elementlist.append((name.lower(),
                            f"<li class='element-on-list' id='{id} name-abrv'>"
                            f"<a href='/elements/{e.html_filename}'>{name}</a></li>"))
elementlist.sort(key=lambda x: x[0])
content += "<ul>" + "\n".join([i[1] for i in elementlist]) + "</ul>"
content += "<script type='text/javascript'>do_filter()</script>"

write_html_page(os.path.join(settings.htmlelement_path, "index.html"),
                "Index of elements", content)

# Recently updated elements
rss_icon = ("<span style='color:#FF8800;padding-left:10px'>"
            "<i class='fa fa-rss' aria-hidden='true'></i></span>")
content = heading_with_self_ref("h1", "Recent elements")
content += f"<h2>Recently added elements <a href='/new-elements.xml'>{rss_icon}</a></h2>\n"
content += "<ul>\n"
for e in categoriser.recently_added(10):
    content += f"<li><a href='/elements/{e.html_filename}'>{e.html_name}</a>"
    if e.created is not None:
        content += f" ({e.created.strftime('%d %B %Y')})"
    content += "</li>\n"
content += "</ul>\n"

content += f"<h2>Recently updated elements <a href='/updated-elements.xml'>{rss_icon}</a></h2>\n"
content += "<ul>\n"
for e in categoriser.recently_updated(10):
    content += f"<li><a href='/elements/{e.html_filename}'>{e.html_name}</a>"
    if e.modified is not None:
        content += f" ({e.modified.strftime('%d %B %Y')})"
    content += "</li>\n"
content += "</ul>\n"

write_html_page(os.path.join(settings.htmlindices_path, "recent.html"),
                "Recent elements", content)

with open(os.path.join(settings.html_path, "new-elements.xml"), "w") as f:
    f.write(make_rss(categoriser.recently_added(10), "recently added elements",
                     "Finite elements that have recently been added to DefElement", "created"))

with open(os.path.join(settings.html_path, "updated-elements.xml"), "w") as f:
    f.write(make_rss(categoriser.recently_updated(10), "recently updated elements",
                     "Finite element whose pages on DefElement have recently been updated",
                     "modified"))

# Category index
os.mkdir(os.path.join(settings.htmlindices_path, "categories"))
content = heading_with_self_ref("h1", "Categories")
for c in categoriser.categories:
    category_pages = []
    for e in categoriser.elements_in_category(c):
        for name in [e.html_name]:
            category_pages.append((name.lower(),
                                   f"<li><a href='/elements/{e.html_filename}'>{name}</a></li>"))

    category_pages.sort(key=lambda x: x[0])

    content += (f"<h2><a href='/lists/categories/{c}.html'>{categoriser.get_category_name(c)}"
                "</a></h2>\n<ul>")
    content += "".join([i[1] for i in category_pages])
    content += "</ul>"

    sub_content = heading_with_self_ref("h1", categoriser.get_category_name(c))
    sub_content += "<ul>"
    sub_content += "".join([i[1] for i in category_pages])
    sub_content += "</ul>"

    write_html_page(os.path.join(settings.htmlindices_path, f"categories/{c}.html"),
                    categoriser.get_category_name(c), sub_content)

write_html_page(os.path.join(settings.htmlindices_path, "categories/index.html"),
                "Categories", content)

# Implementations index
os.mkdir(os.path.join(settings.htmlindices_path, "implementations"))
content = heading_with_self_ref("h1", "Implemented elements")
for c, info in implementations.items():
    category_pages = []
    for e in categoriser.elements_in_implementation(c):
        names = {e.html_name}
        refs = set()
        for cname in categoriser.references:
            for i_str in e.list_of_implementation_strings(c, None):
                if "(" not in i_str or f"({cname})" in i_str:
                    refs.add(cname)
                    break
        for name in names:
            category_pages.append((name.lower(),
                                   f"<li><a href='/elements/{e.html_filename}'>{name}</a></li>"))

    category_pages.sort(key=lambda x: x[0])

    content += (f"<h2><a href='/lists/implementations/{c}.html'>Implemented in {info.name}"
                "</a></h2>\n<ul>")
    content += "".join([i[1] for i in category_pages])
    content += "</ul>"

    sub_content = f"<h1>Implemented in <a href='{info.url}'>{info.name}</a></h1>\n<ul>"
    sub_content += "".join([i[1] for i in category_pages])
    sub_content += "</ul>"

    write_html_page(os.path.join(settings.htmlindices_path, f"implementations/{c}.html"),
                    f"Implemented in {info.name}", sub_content)

write_html_page(os.path.join(settings.htmlindices_path, "implementations/index.html"),
                "Implemented elements", content)

# Reference cells index
os.mkdir(os.path.join(settings.htmlindices_path, "references"))
content = heading_with_self_ref("h1", "Reference cells")
for c in categoriser.references:
    refels = []
    for e in categoriser.elements_by_reference(c):
        for name in [e.html_name]:
            refels.append((name.lower(),
                           f"<li><a href='/elements/{e.html_filename}'>{name}</a></li>"))

    refels.sort(key=lambda x: x[0])

    content += f"<h2>{cap_first(c)}</h2>\n"
    content += "<ul>" + "".join([i[1] for i in refels]) + "</ul>"

    title = "Finite elements on a"
    if c[0] in "aeiou":
        title += "n"
    title += f" {c}"
    sub_content = heading_with_self_ref("h1", title)
    sub_content += "<ul>" + "".join([i[1] for i in refels]) + "</ul>"

    write_html_page(os.path.join(settings.htmlindices_path, f"references/{c}.html"),
                    title, sub_content)

write_html_page(os.path.join(settings.htmlindices_path, "references/index.html"),
                "Reference cells", content)

# Page showing numbering of references
content = heading_with_self_ref("h1", "Reference cell numbering")
content += "<p>This page illustrates the entity numbering used for each reference cell.</p>"
for cell in categoriser.references.keys():
    if cell == "dual polygon":
        for nsides in [4, 5, 6]:
            content += heading_with_self_ref("h2", f"Dual polygon ({nsides})")
            content += plotting.plot_reference(symfem.create_reference(f"dual polygon({nsides})"))
    else:
        content += heading_with_self_ref("h2", cap_first(cell))
        content += plotting.plot_reference(symfem.create_reference(cell))

write_html_page(os.path.join(settings.html_path, "reference_numbering.html"),
                "Reference cell numbering", content)


# Families
def linked_names(dim: str, fname: str, cell: str) -> str:
    """Create list of linked names.

    Args:
        dim: Dimension
        fname: Filename
        cell: Reference cell

    Returns:
        List of linked names
    """
    out = []
    for key, cname in keys_and_names:
        if key in data:
            out.append(
                f"<a href='/families/{fname}.html'>"
                "\\(" + cname(data[key], cell=cell, dim=dim) + "\\)"
                "</a>")
    return ", ".join(out)


def de_rham_row(family: typing.Dict[str, typing.Dict[str, typing.List[str]]],
                fname: str, cell: str, diff_form_deg: typing.List[str]) -> str:
    """Create HTML string of FEs.

    Args:
        family: Elements
        fname: Filename
        cell: Reference cell
        diff_form_deg: List of differential form degrees

    Returns:
        HTML string of FEs
    """
    row = ""
    if all(i in family[cell] for i in diff_form_deg):
        row += "<tr>"
        row += f"<td>{linked_names(str(len(diff_form_deg)-1), fname, cell)}</td>"
        for o in diff_form_deg:
            row += f"<td><a href='/elements/{family[cell][o][1]}'"
            row += " style='text-decoration:none'>"
            row += f"{family[cell][o][0]}</a></td>"
            if o != "d":
                row += "<td>&nbsp;</td>"
        row += "</tr>"
    return row


de_rham_3d: typing.List[str] = []
de_rham_2d_hdiv: typing.List[str] = []
de_rham_2d_hcurl: typing.List[str] = []

for fname, data in categoriser.families["de-rham"].items():
    family = data["elements"]
    cnames = []
    for key, cname in keys_and_names:
        if key in data:
            cnames.append("\\(" + cname(data[key], dim="3") + "\\)")
    if len(cnames) == 0:
        raise ValueError(f"No name found for family: {fname}")
    sub_content = heading_with_self_ref("h1", "The " + " or ".join(cnames) + " family")

    assert len([i for i in ["simplex", "tp"] if i in family]) == 1

    sub_content += "<ul>"
    for cell in ["simplex", "tp"]:
        if cell in family:

            for o in ["0", "1", "d-1", "d"]:
                if o in family[cell]:
                    sub_content += f"<li><a href='/elements/{family[cell][o][1]}'"
                    sub_content += " style='text-decoration:none'>"
                    sub_names = []
                    for key, cname in keys_and_names:
                        if key in data:
                            sub_names.append("\\(" + cname(data[key], o, cell) + "\\)")
                    sub_content += " or ".join(sub_names)
                    sub_content += f" ({family[cell][o][0]})</a></li>"

            de_rham_3d.append(de_rham_row(family, fname, cell, ["0", "1", "d-1", "d"]))
            de_rham_2d_hdiv.append(de_rham_row(family, fname, cell, ["0", "d-1", "d"]))
            de_rham_2d_hcurl.append(de_rham_row(family, fname, cell, ["0", "1", "d"]))
        sub_content += "</ul>"

    write_html_page(os.path.join(settings.htmlfamilies_path, f"{fname}.html"),
                    "The " + " or ".join(cnames) + " family", sub_content)

content = heading_with_self_ref("h1", "Complex families")
content += "<p>You can find some information about how these familes are defined "
content += "<a href='/de-rham.html'>here</a></p>"
content += heading_with_self_ref("h2", "De Rham complex in 3D")
content += "<table class='families'>\n"
content += "<tr>"
content += "<td><small>Name(s)</small></td>"
content += "<td>\\(H^1\\)</td>"
content += "<td>\\(\\xrightarrow{\\nabla}\\)</td>"
content += "<td>\\(\\textbf{H}(\\text{curl})\\)</td>"
content += "<td>\\(\\xrightarrow{\\nabla\\times}\\)</td>"
content += "<td>\\(\\textbf{H}(\\text{div})\\)</td>"
content += "<td>\\(\\xrightarrow{\\nabla\\cdot}\\)</td>"
content += "<td>\\(L^2\\)</td>"
content += "</tr>\n"
content += "\n".join(de_rham_3d)
content += "</table>"
content += heading_with_self_ref("h2", "De Rham complex in 2D")
content += "<p>In 2D, \\(\\textbf{H}(\\text{div})\\) and \\(\\textbf{H}(\\text{curl})\\) "
content += "are isomorphic via a 90 degree rotation \\(R\\). This means that we can define "
content += "the de Rham complex in two ways.</p>"
content += "<p>One variant uses \\(\\textbf{H}(\\text{div})\\) and the vector-valued "
content += "\\(\\textbf{curl}\\) operator, "
content += "\\(\\textbf{curl} \\, u = (\\partial_y u, -\\partial_x u)\\). "
content += "Note that \\(\\textbf{curl} \\, u = R \\, \\nabla u\\).</p>"
content += "<table class='families'>\n"
content += "<tr>"
content += "<td><small>Name(s)</small></td>"
content += "<td>\\(H^1\\)</td>"
content += "<td>\\(\\xrightarrow{\\textbf{curl}}\\)</td>"
content += "<td>\\(\\textbf{H}(\\text{div})\\)</td>"
content += "<td>\\(\\xrightarrow{\\nabla\\cdot}\\)</td>"
content += "<td>\\(L_2\\)</td>"
content += "</tr>\n"
content += "\n".join(de_rham_2d_hdiv)
content += "</table>"
content += "<p>The second variant uses \\(\\textbf{H}(\\text{curl})\\) and the scalar-valued "
content += "\\(\\text{curl}\\) operator, "
content += "\\(\\text{curl} \\, \\mathbf{u} = \\partial_x u_y - \\partial_y u_x\\). "
content += "Note that \\(\\text{curl} \\, \\mathbf{u} = \\nabla\\cdot R \\mathbf{u}\\).</p>"
content += "<table class='families'>\n"
content += "<tr>"
content += "<td><small>Name(s)</small></td>"
content += "<td>\\(H^1\\)</td>"
content += "<td>\\(\\xrightarrow{\\nabla}\\)</td>"
content += "<td>\\(\\textbf{H}(\\text{curl})\\)</td>"
content += "<td>\\(\\xrightarrow{\\text{curl}}\\)</td>"
content += "<td>\\(L_2\\)</td>"
content += "</tr>\n"
content += "\n".join(de_rham_2d_hcurl)
content += "</table>"
content += "<p>These two de Rham complex definitions in 2D account for the "
content += "double element diagrams in the orange boxes in the "
content += "<a href=https://www-users.cse.umn.edu/~arnold/femtable>"
content += "Periodic table of the finite elements</a>. That is also why the "
content += "boxes are orange, and not red nor yellow as in 3D.</p>"
write_html_page(os.path.join(settings.htmlfamilies_path, "index.html"), "Complex families", content)

# List of lists
content = heading_with_self_ref("h1", "Lists of elements")
content += "<ul>\n"
content += "<li><a href='/lists/categories'>Finite elements by category</a></li>\n"
content += "<li><a href='/lists/references'>Finite elements by reference cell</a></li>\n"
content += "<li><a href='/lists/recent.html'>Recently added/updated finite elements</a></li>\n"
content += "</ul>"
write_html_page(os.path.join(settings.htmlindices_path, "index.html"), "Lists of elements", content)

# Site map
sitemap[html_local(os.path.join(settings.html_path, "sitemap.html"))] = "List of all pages"


def list_pages(folder: str) -> str:
    """Create list of pages in a folder.

    Args:
        folder: The folder

    Returns:
        List of pages
    """
    items = []
    if folder == "":
        items.append(("A", "<li><a href='/index.html'>Front page</a>"))
    for i, j in sitemap.items():
        if i.startswith(folder):
            file = i[len(folder) + 1:]
            if "/" in file:
                subfolder, subfile = file.split("/", 1)
                if subfile == "index.html":
                    items.append((j.lower(), list_pages(f"{folder}/{subfolder}")))
            elif file != "index.html":
                items.append((j.lower(), f"<li><a href='{i}'>{j}</a></li>"))
    items.sort(key=lambda a: a[0])
    out = ""
    if folder != "":
        title = sitemap[f"{folder}/index.html"]
        out += f"<li><a href='{folder}/index.html'>{title}</a>"
    out += "<ul>" + "\n".join(i[1] for i in items) + "</ul>"
    if folder != "":
        out += "</li>"
    return out


content = heading_with_self_ref("h1", "List of all pages") + list_pages("")
with open(os.path.join(settings.html_path, "sitemap.html"), "w") as f:
    f.write(make_html_page(content))

end_all = datetime.now()
print(f"Total time: {(end_all - start_all).total_seconds():.2f}s")
