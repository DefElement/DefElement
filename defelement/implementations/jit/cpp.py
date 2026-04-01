"""C++ just-in-time compilation."""

import os
from collections.abc import Callable
from defelement.implementations.jit import tools
from defelement.implementations.jit.argument_types import ArgType
import numpy.typing as npt
import numpy as np


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

    if not os.path.isfile(os.path.join(os.path.join(folder, "build"), f"lib{library_name}.so")):
        try:
            if len(outputs) == 0:
                out_type = "void"
            if len(outputs) == 1:
                out_type = outputs[0].type("cpp")
            else:
                out_type = "std::tuple<" + ", ".join(o.type("cpp") for o in outputs) + ">"

            function_def = out_type + " function(" + ", ".join(f"{i.type('cpp')} {i.variable}" for i in inputs) + ")"

            with open(os.path.join(folder, "function.h"), "w") as f:
                f.write('#include "mdspan.hpp"\n')
                f.write("\n")
                f.write("template <typename T, std::size_t d> using mdspan = MDSPAN_IMPL_STANDARD_NAMESPACE::mdspan<T, MDSPAN_IMPL_STANDARD_NAMESPACE::dextents<std::size_t, d>>;\n")
                f.write("\n")
                f.write(f"{function_def};\n")

            with open(os.path.join(folder, "function.cpp"), "w") as f:
                f.write('#include "function.h"\n')
                if imports.strip("\n") != "":
                    f.write(imports.strip("\n") + "\n")
                f.write("\n")
                f.write(f"{function_def} {{\n")
                for o in outputs:
                    function = function.replace(f"INIT {o.variable};", o.initialise("cpp"))
                f.write("\n".join(f"  {line}" for line in function.split("\n")) + "\n")
                if len(outputs) == 1:
                    f.write(f"  return {outputs[0].variable};\n");
                elif len(outputs) > 0:
                    f.write("  return {" + ", ".join(o.variable for o in outputs) + "};\n");
                f.write("}\n")

            find_packages = "\n".join(
                f"find_package({libname} REQUIRED)"
                for libname, _ in packages
            )
            target_link_libraries = "\n".join(
                f"target_link_libraries(${{PROJECT_NAME}} {libname}::{namespace})"
                 for libname, namespace in packages
            )

            with open(os.path.join(os.path.join(folder, "cpp"), "cmake_template"), "w") as f:
                cmake_template = f.read()
            with open(os.path.join(folder, "CMakeLists.txt"), "w") as f:
                f.write(cmake_template
                    .replace("<!project_name>", project_name)
                    .replace("<!library_name>", library_name)
                    .replace("<!find_packages>", find_packages)
                    .replace("<!target_link_libraries>", target_link_libraries)
                )

            with open(os.path.join(folder, f"DefElementFunction{id_hash}Config.cmake.in"), "w") as f:
                f.write("@PACKAGE_INIT@\n")
                f.write("include(CMakeFindDependencyMacro)\n")
                f.write("if(NOT TARGET @PROJECT_NAME@)\n")
                f.write('  include("${CMAKE_CURRENT_LIST_DIR}/@PROJECT_NAME@Targets.cmake")\n')
                f.write("endif()\n")

            os.system(f"cp {os.path.dirname(os.path.realpath(__file__))}/cpp/mdspan.hpp {folder}")

            if not os.path.isdir(os.path.join(folder, "build")):
                os.mkdir(os.path.join(folder, "build"))
            assert os.system(f"cd {folder}/build && cmake -DCMAKE_INSTALL_PREFIX:PATH=. .. && make && make install") == 0

        except BaseException as e:
            tools.save_error(folder, e)

    tools.check_for_error(folder)

    return lambda x: np.zeros([x.shape[0], 1, 10])
