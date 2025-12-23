--
title: Reference cell numbering
--
This page illustrates the entity numbering used for each reference cell. In general, the following conventions are used when numbering cells on DefElement.

### Convention 1: vertex numbering

If \(a=(a_0,...,a_{d-1}\) and \(b=(a_0,...,b_{d-1}\) are two vertices of a reference cell then the index of vertex
\(a\) is less than the index of vertex \(b\) if and only if \((a_{d-1},...,a_0)<(b_{d-1},...,b_0)\) (where the meaning of \(<\) is as in Pyhton for tuples).

Note that dual cells are treated as a special case, with the vertices numbered in an anticlockwise order.

### Convention 2: sub-entity numbering

Let \(a\) and \(b\) be two sub-entities of a reference cell with vertices \(v_a\) and \(v_b\).
The index of sub-entity \(a\) is less that the index of sub-entity \(b\) if and only if
\(v_a < v_b\).


{{REFERENCE_CELL_NUMBERING}}
