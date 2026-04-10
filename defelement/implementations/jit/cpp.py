"""C++ just-in-time compilation."""

import os
import re
from collections.abc import Callable
from defelement.implementations.jit import tools
from defelement.implementations.jit.argument_types import ArgType
from webtools.tools import join

from cffi import FFI

here = os.path.dirname(os.path.realpath(__file__))


def compile(
    *,
    function: str,
    inputs: list[ArgType] = [],
    outputs: list[ArgType] = [],
    imports: str | None = None,
    id: str | None = None,
    packages: list[tuple[str, str]] = [],
) -> Callable:
    """Just-in-time compile a C++ function."""
    folder = tools.source_dir("cpp", id)

    library_name = "defelement_function"
    project_name = "DefElementFunction"

    true_outputs = [o for o in outputs if not o.in_out]
    in_out = [o for o in outputs if o.in_out]
    function_inputs = ", ".join(f"{i.function_input('cpp')}" for i in inputs + in_out)
    function_inputs_no_in_out = ", ".join(f"{i.function_input('cpp')}" for i in inputs)
    if len(true_outputs) == 0:
        output_type = "void"
    elif len(true_outputs) == 1:
        output_type = true_outputs[0].type("cpp")
    else:
        raise NotImplementedError("Functions with more than one output not currently supported")
    function_def = f"{output_type} function({function_inputs})"

    custom_types = []
    for i in inputs + outputs:
        ct = i.define_custom_type("cpp")
        if ct is not None:
            custom_types.append(ct)
    metadata_functions = []
    for o in in_out:
        mf = o.metadata_function_signature("cpp", function_inputs_no_in_out)
        if mf is not None:
            metadata_functions.append(mf)

    if not os.path.isfile(join(folder, "build", f"lib{library_name}.so")):
        try:
            # function.h
            code = 'extern "C" {\n'
            code += tools.add_indent("\n".join(custom_types), 2)
            code += "\n"
            code += tools.add_indent("\n".join(f"{i};" for i in metadata_functions), 2)
            code += "\n"
            code += tools.add_indent(function_def, 2) + ";"
            code += "\n"
            code += "}"
            with open(join(folder, "function.h"), "w") as f:
                f.write(code)

            # function.cpp
            code = (
                '#include "function.h"\n'
                '#include "mdspan.hpp"\n'
                "template <typename T, std::size_t d> "
                "using mdspan = MDSPAN_IMPL_STANDARD_NAMESPACE::mdspan"
                "<T, MDSPAN_IMPL_STANDARD_NAMESPACE::dextents<std::size_t, d>>;\n"
            )
            if imports is not None:
                code += imports.strip("\n")
            code += "\n\n"
            for i in inputs + outputs:
                init_i = i.init_custom_type("cpp")
                if init_i is not None:
                    code += init_i + "\n\n"
            for vars, out in [(inputs + in_out, False), (true_outputs, True)]:
                for i in vars:
                    if i.initialise("cpp", output=out) != "":
                        if f"INIT {i.variable};" not in function:
                            function = i.initialise("cpp", output=out) + "\n" + function
            if o in in_out:
                mf = o.metadata_function_signature("cpp", function_inputs_no_in_out)
                if mf is not None:
                    code += f"{mf}{{\n"
                    code += tools.add_indent(o.metadata_function_impl("cpp", function), 2)
                    code += "\n"
                    code += "}\n\n"
            code += f"{function_def} {{\n"
            code += tools.add_indent(function, 2)
            code += "\n"
            if len(true_outputs) > 0:
                if len(true_outputs) == 1:
                    code += tools.add_indent(true_outputs[0].function_output("cpp"), 2)
                    code += "\n"
                else:
                    raise NotImplementedError(
                        "Functions with more than one output not currently supported"
                    )
            code += "}\n"
            for vars, out in [(inputs + in_out, False), (true_outputs, True)]:
                for i in vars:
                    # TODO: indent
                    code = re.sub(
                        r"( *)INIT " + i.variable,
                        lambda matches: tools.add_indent(
                            i.initialise("cpp", output=out), len(matches[1])
                        ),
                        code,
                    )
            with open(join(folder, "function.cpp"), "w") as f:
                f.write(code)

            # other files
            find_packages = "\n".join(
                f"find_package({libname} REQUIRED)" for libname, _ in packages
            )
            target_link_libraries = "\n".join(
                f"target_link_libraries({library_name} {libname}::{namespace})"
                for libname, namespace in packages
            )

            for source, target in [
                ("cmake_template", "CMakeLists.txt"),
                ("mdspan.hpp", "mdspan.hpp"),
                ("Config.cmake.in", "DefElementFunctionConfig.cmake.in"),
            ]:
                with open(join(here, "cpp", source)) as f:
                    template = f.read()

                with open(join(folder, target), "w") as f:
                    f.write(
                        template.replace("<!project_name>", project_name)
                        .replace("<!library_name>", library_name)
                        .replace("<!find_packages>", find_packages)
                        .replace("<!target_link_libraries>", target_link_libraries)
                    )

            if not os.path.isdir(join(folder, "build")):
                os.mkdir(join(folder, "build"))
            assert (
                os.system(f"cmake -DCMAKE_INSTALL_PREFIX:PATH=. -B{folder}/build -S{folder}") == 0
            )
            assert os.system(f"make -C {folder}/build") == 0
            assert os.system(f"make -C {folder}/build install") == 0

        except BaseException as e:
            tools.save_error(folder, e)

    tools.check_for_error(folder)

    ffi = FFI()
    ffi.cdef(
        "\n".join(custom_types)
        + "\n"
        + "\n".join(f"{mf};" for mf in metadata_functions)
        + "\n"
        + function_def
        + ";"
    )
    lib = ffi.dlopen(join(folder, "build", f"lib{library_name}.so"))

    def wrapped_function(*args):
        if len(args) != len(inputs):
            raise TypeError(
                f"Incorrect number of arguments passed to function: expecting {len(inputs)}, received {len(args)}"
            )
        c_inputs = [i.to_raw(lib, ffi, a) for i, a in zip(inputs, args)]
        in_out_args = tuple(i.empty(lib, ffi, c_inputs) for i in in_out)
        c_in_out = [i.to_raw(lib, ffi, a) for i, a in zip(in_out, in_out_args)]
        result = lib.function(*c_inputs, *c_in_out)
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
                    raise NotImplementedError(
                        "Functions with more than one output not currently supported"
                    )
        if len(out) > 0:
            if len(out) == 1:
                return out[0]
            return out

    return wrapped_function
