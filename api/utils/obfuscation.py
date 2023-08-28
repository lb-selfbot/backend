"""
Obfuscation module for the API.
"""
import ast
import subprocess
import tempfile
import os

import pyobf2.lib as pyobf2

py_obfuscators = [
    "logicTransformer",
    "removeTypeHints",
    "fstrToFormatSeq",
    "encodeStrings",
    "stringCollector",
    "floatsToComplex",
    "intObfuscator",
    "renamer",
    "typeAliasTransformer",
    "replaceAttribSet",
]
pyobf2.set_config_dict({f"{obf}.enabled": True for obf in py_obfuscators})


def obfuscate_python(code: str) -> str:
    """
    Obfuscates Python code.
    """
    parsed = ast.parse(code, "code.py")
    obfuscated = pyobf2.do_obfuscation_single_ast(parsed, "code.py")

    return ast.unparse(obfuscated)


def obfuscate_lua(code: str) -> str:
    """
    Obfuscates Lua code.
    """
    name = ""

    with tempfile.NamedTemporaryFile(suffix=".lua", delete=False) as f:
        name = f.name

        f.write(code.encode())
        f.flush()

        subprocess.check_call(["lua", "./prometheus/cli.lua", "--preset", "Weak", name])

    name = name.replace(".lua", ".obfuscated.lua")

    with open(name, "r") as f:
        code = f.read()

    return code


js_options = [
    "--compact",
    "true",
    "--control-flow-flattening",
    "true",
    "--control-flow-flattening-threshold",
    "1",
    "--numbers-to-expressions",
    "true",
    "--simplify",
    "true",
    "--string-array-shuffle",
    "true",
    "--split-strings",
    "true",
    "--string-array-threshold",
    "1",
    # "--string-array-encoding base64",
]


def obfuscate_javascript(code: str) -> str:
    """
    Obfuscates Javascript code.
    """
    with tempfile.NamedTemporaryFile(suffix=".js", delete=False) as code_file:
        code_file.write(code.encode())
        code_file.flush()

        os.environ["PATH"] = (
            "/root/.nvm/versions/node/v19.4.0/bin:" + os.environ["PATH"]
        )

        subprocess.run(
            [
                "npx",
                "javascript-obfuscator",
                code_file.name,
                "-o",
                code_file.name,
                *js_options,
            ],
            shell=True,
        )

        with open(code_file.name, "r") as f:
            code = f.read()

        os.remove(code_file.name)

    return code
