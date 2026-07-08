import numpy as np
from defelement.implementations import jit


def test_cpp():
    """Test that a C++ function that creates a scalar times the identity matrix is correctly JIT compiled."""
    f = jit.cpp(
        inputs=[jit.integer("dimension"), jit.double("scale")],
        function=(
            "for (std::size_t i = 0; i < dimension; ++i) {\n"
            "  for (std::size_t j = 0; j < dimension; ++j)\n"
            "    matrix(i, j) = 0.0;\n"
            "  matrix(i, i) = scale;\n"
            "}"
        ),
        outputs=[jit.ndarray("matrix", 2, shape=("dimension", "dimension"))],
        id="test_jit",
    )

    m1 = f(3, 1.0)
    assert m1.shape == (3, 3)
    for i in range(3):
        for j in range(3):
            assert np.isclose(m1[i, j], 1.0 if i == j else 0.0)

    m2 = f(5, 2.0)
    assert m2.shape == (5, 5)
    for i in range(5):
        for j in range(5):
            assert np.isclose(m2[i, j], 2.0 if i == j else 0.0)
