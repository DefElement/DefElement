"""C++ just-in-time compilation."""

import os
from collections.abc import Callable
from defelement.implementations.jit import tools
from defelement.implementations.jit.argument_types import ArgType
import numpy.typing as npt
import numpy as np
from webtools.tools import join

from cffi import FFI

here = os.path.dirname(os.path.realpath(__file__))

def compile(
    *,
    function: str,
    inputs: list[ArgType] = [],
    outputs: list[ArgType] = [],
    imports: str,
    id: str | None = None,
    packages: list[tuple[str, str]] = [],
) -> Callable:
    """Just-in-time compile a C++ function."""
    id_hash = tools.hash(id)
    folder = tools.source_dir("cpp", id)

    library_name = f"defelement_function_{id_hash}"
    project_name = f"DefElementFunction{id_hash}"

    if len(outputs) == 0:
        out_type = "void"
    if len(outputs) == 1:
        out_type = outputs[0].type("cpp")
    else:
        out_type = "std::tuple<" + ", ".join(o.type("cpp") for o in outputs) + ">"

    function_def = out_type + " function(" + ", ".join(f"{i.function_input('cpp')}" for i in inputs) + ")"

    if not os.path.isfile(join(folder, "build", f"lib{library_name}.so")):
        try:

            with open(join(folder, "function.h"), "w") as f:
                f.write("#include <tuple>\n")
                f.write("\n")
                f.write(f"{function_def};\n")

            with open(join(folder, "function.cpp"), "w") as f:
                f.write('#include "function.h"\n')
                f.write('#include "mdspan.hpp"\n')
                if imports.strip("\n") != "":
                    f.write(imports.strip("\n") + "\n")
                f.write("\n")
                f.write("template <typename T, std::size_t d> using mdspan = MDSPAN_IMPL_STANDARD_NAMESPACE::mdspan<T, MDSPAN_IMPL_STANDARD_NAMESPACE::dextents<std::size_t, d>>;\n")
                f.write("\n")
                f.write(f"{function_def} {{\n")
                for i in inputs:
                    f.write(i.initialise("cpp") + "\n")
                for o in outputs:
                    function = function.replace(f"INIT {o.variable};", o.initialise("cpp"))
                f.write("\n".join(f"  {line}" for line in function.split("\n")) + "\n")
                if len(outputs) == 1:
                    f.write(f"  return {outputs[0].function_output('cpp')};\n");
                elif len(outputs) > 0:
                    f.write("  return {" + ", ".join(o.function_output("cpp") for o in outputs) + "};\n");
                f.write("}\n")

            find_packages = "\n".join(
                f"find_package({libname} REQUIRED)"
                for libname, _ in packages
            )
            target_link_libraries = "\n".join(
                f"target_link_libraries(${{PROJECT_NAME}} {libname}::{namespace})"
                 for libname, namespace in packages
            )

            for source, target in [
                ("cmake_template", "CMakeLists.txt"),
                ("mdspan.hpp", "mdspan.hpp"),
                ("Config.cmake.in", f"DefElementFunction{id_hash}Config.cmake.in"),
            ]:
                with open(join(here, "cpp", source)) as f:
                    template = f.read()

                with open(join(folder, target), "w") as f:
                    f.write(template
                        .replace("<!project_name>", project_name)
                        .replace("<!library_name>", library_name)
                        .replace("<!find_packages>", find_packages)
                        .replace("<!target_link_libraries>", target_link_libraries)
                    )

            if not os.path.isdir(join(folder, "build")):
                os.mkdir(join(folder, "build"))
            assert os.system(f"cmake -DCMAKE_INSTALL_PREFIX:PATH=. -B{folder}/build -S{folder}") == 0
            assert os.system(f"make -C {folder}/build") == 0
            assert os.system(f"make -C {folder}/build install") == 0

        except BaseException as e:
            tools.save_error(folder, e)

    tools.check_for_error(folder)

    ffibuilder = FFI()
    print(function_def)
    ffibuilder.cdef(function_def + ";")
    ffibuilder.set_source(f"_{library_name}",
      r'#include "function.h"',
      include_dirs = [join(folder, "build")],
      libraries = [library_name],
      library_dirs = [join(folder, "build")],
    )

    from IPython import embed; embed()()

    return lambda x: np.zeros([x.shape[0], 1, 10])
