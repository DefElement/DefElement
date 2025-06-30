# Reusing & citing

## Reusing content from DefElement
The text, images, and other content on this website (excluding Font Awesome, which is released under [its own license](https://github.com/DefElement/DefElement/blob/main/files/fontawesome/LICENSE.txt))
may be reused under the terms of a
[Creative Commons Attribution 4.0 International (CC BY 4.0) license](https://creativecommons.org/licenses/by/4.0/): this means
that you can reuse any of the content as long as you attribute DefElement.
For reuse on a website, you could attribute us by including a link to DefElement;
for reuse in print, you could attribute us by including "DefElement" somewhere near the image or information;
for reuse in a paper, you could cite DefElement.

The DefElement logo can be found on the [branding page](branding.md).

## Citing DefElement

The code used to generate this website is available on [GitHub](https://github.com/DefElement/DefElement)
under an [MIT license](https://github.com/DefElement/DefElement/blob/main/LICENSE).

On each of the element definition pages, you can find citations for the paper(s) that introduced
that element. These papers should be cited when using a given element. If you wish to cite this
website, you can use the following BibTeX:

```
@misc{defelement,
       AUTHOR = {{{list contributors|bibtex}}},
        TITLE = {{DefElement}: an encyclopedia of finite element definitions},
         YEAR = {{{{date:Y}}}},
 HOWPUBLISHED = {\url{https://defelement.org}},
         NOTE = {[Online; accessed {{date:D-M-Y}}]}
}
```

This will create a reference along the lines of:

<ul class='citations'>
<li>{{list contributors|citation}}. <i>DefElement: an encyclopedia of finite element definitions</i>, {{date:Y}}, <a href='https://defelement.org'>https://defelement.org</a> [Online; accessed: {{date:D-M-Y}}].</li>
</ul>

### DefElement paper

You may also wish to cite the [DefElement paper](https://arxiv.org/abs/2506.20188), which is currently available as a preprint on ar&Chi;iv.
To cite this, you can use the following BibTeX:

```
@unpublished{2025-defelement,
       AUTHOR = {Scroggs, Matthew W.
                 and Brubeck, Pablo D.
                 and Dean, Joseph P.
                 and Dokken, J{\o}rgen S.
                 and Marsden, India},
        TITLE = {{DefElement:} an encyclopedia of finite element definitions},
         YEAR = {2025},
         NOTE = {submitted to Computational Science and Engineering},
          DOI = {10.48550/arXiv.2506.20188}
}
```

This will create a reference along the lines of:

<ul class='citations'>
<li>M. W. Scroggs, P. D. Brubeck, J. P. Dean, J. S. Dokken, I. Marsden. <i>DefElement: an encyclopedia of finite element definitions</i>, 2025, submitted to Computational Science and Engineering, <a href='https://doi.org/10.48550/arXiv.2506.20188'>https://doi.org/10.48550/arXiv.2506.20188</a>.</li>
</ul>

## DefElement poster
The [DefElement poster](https://doi.org/10.6084/m9.figshare.23294939.v1) was first presented at [FEniCS 2023](https://fenicsproject.org/fenics-2023/).

If you'd like a copy of the poster, you can download
[the A0 poster](/pdfs/poster-a0.pdf),
[the A0 poster (with bleed for printing)](/pdfs/poster-a0-bleed.pdf),
[the A1 poster](/pdfs/poster-a1.pdf),
[the A1 poster (with bleed for printing)](/pdfs/poster-a1-bleed.pdf),
[the A4 poster](/pdfs/poster-a4.pdf), or
[the A4 poster (with bleed for printing)](/pdfs/poster-a4-bleed.pdf).
These are all available under the same [Creative Commons Attribution 4.0 International (CC BY 4.0) license](https://creativecommons.org/licenses/by/4.0/)
as the rest of DefElement.

If you wich to cite the poster, you can use the following BibTeX:

```
@misc{defelement-poster,
       AUTHOR = {Scroggs, Matthew W.},
        TITLE = {{DefElement}: an encyclopedia of finite element definitions},
         YEAR = {2023},
 HOWPUBLISHED = {Poster presented at FEniCS 2023, Cagliari, Italy},
          DOI = {10.6084/m9.figshare.23294939.v1},
}
```

This will create a reference along the lines of:

<ul class='citations'>
<li>M. W. Scroggs. <i>DefElement: an encyclopedia of finite element definitions</i>, 2023, Poster presented at FEniCS 2023, Cagliari, Italy, <a href=https://doi.org/10.6084/m9.figshare.23294939.v1>https://doi.org/10.6084/m9.figshare.23294939.v1</a>.</li>
</ul>
