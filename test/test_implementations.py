import pytest
from defelement.implementations import implementations
from defelement.languages import languages


@pytest.mark.parametrize("i", implementations)
def test_languages(i):
    for lang in implementations[i].languages:
        assert lang in languages
