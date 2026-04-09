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

    true_outputs = [o for o in outputs if not o.in_out]
    in_out = [o for o in outputs if o.in_out]
    function_inputs = ", ".join(f"{i.function_input('cpp')}" for i in inputs + in_out)
    if len(true_outputs) == 0:
        output_type = "void"
    elif len(true_outputs) == 1:
        output_type = true_outputs[0].type("cpp")
    else:
        raise NotImplementedError("Functions with more than one output not currently supported")
    function_def = f"{output_type} function({function_inputs})"

    custom_types = "\n".join([i.define_custom_type("cpp") for i in inputs + outputs if i.define_custom_type("cpp") is not None])

    if not os.path.isfile(join(folder, "build", f"lib{library_name}.so")):
        try:

            with open(join(folder, "function.h"), "w") as f:
                f.write('extern "C" {\n')
                f.write("\n".join(f"  {i}" for i in custom_types.split("\n")))
                f.write("\n")
                f.write(f"  {function_def};\n")
                f.write("}")

            with open(join(folder, "function.cpp"), "w") as f:
                f.write('#include "function.h"\n')
                f.write('#include "mdspan.hpp"\n')
                if imports.strip("\n") != "":
                    f.write(imports.strip("\n") + "\n")
                f.write("\n")
                f.write("template <typename T, std::size_t d> using mdspan = MDSPAN_IMPL_STANDARD_NAMESPACE::mdspan<T, MDSPAN_IMPL_STANDARD_NAMESPACE::dextents<std::size_t, d>>;\n")
                f.write("\n")
                for i in inputs + outputs:
                    init_i = i.init_custom_type("cpp")
                    if init_i is not None:
                        f.write(init_i + "\n")
                f.write(f"{function_def} {{\n")
                for vars, out in [(inputs + in_out, False), (true_outputs, True)]:
                    for i in vars:
                        if i.initialise("cpp", output=out) != "":
                            if f"INIT {i.variable};" in function:
                                function = function.replace(f"INIT {i.variable};", i.initialise("cpp", output=out));
                            else:
                                f.write(i.initialise("cpp", 2, output=out) + "\n")
                f.write("\n".join(f"  {line}" for line in function.split("\n")) + "\n")
                if len(true_outputs) > 0:
                    if len(true_outputs) == 1:
                        f.write("\n".join(f"  {i}" for i in true_outputs[0].function_output('cpp').split("\n")))
                        f.write("\n")
                    else:
                        raise NotImplementedError("Functions with more than one output not currently supported")
                f.write("}\n")

            find_packages = "\n".join(
                f"find_package({libname} REQUIRED)"
                for libname, _ in packages
            )
            target_link_libraries = "\n".join(
                f"target_link_libraries({library_name} {libname}::{namespace})"
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

    ffi = FFI()
    ffi.cdef(f"{custom_types}\n{function_def};")
    lib = ffi.dlopen(join(folder, "build", f"lib{library_name}.so"))

    def function(*args):
        if len(args) != len(inputs):
            raise TypeError(f"Incorrect number of arguments passed to function: expecting {len(inputs)}, received {len(args)}")
        in_out_args = tuple(i.empty(lib, ffi) for i in in_out)
        result = lib.function(*[i.to_raw(lib, ffi, a) for i, a in zip(inputs + in_out, args + in_out_args)])
        out = []
        i = 0
        for o in outputs:
            if o.in_out:
                out.append(in_out_args[i])
                i += 1
            else:
                if len(true_outputs) == 1:
                    out.append(true_outputs[0].from_raw(lib, ffi, result))
                else:
                    raise NotImplementedError("Functions with more than one output not currently supported")
        if len(out) > 0:
            if len(out) == 1:
                return out[0]
            return out

    from IPython import embed; embed()

    return function
