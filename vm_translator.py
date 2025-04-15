"""This module is used as a main module for opening vm file, reading it and converting to to asm code."""
import sys
import os
import parser

class VMTranslator:
    @staticmethod
    def open_file():
        if len(sys.argv) != 2:
            print("Usage: python vm_translator.py file.vm or directory/")
            sys.exit(1)

        input_path = sys.argv[1]
        files = []

        if os.path.isdir(input_path):
            files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith(".vm")]
            output_file = os.path.join(input_path, os.path.basename(input_path) + ".asm")
        elif input_path.endswith(".vm"):
            files = [input_path]
            output_file = input_path.replace(".vm", ".asm")
        else:
            print("Error: Input must be a .vm file or a directory containing .vm files")
            sys.exit(1)

        parser_cls = parser.Parser()
        file_struc = []

        for file in files:
            try:
                with open(file) as vm_file:
                    filename = os.path.basename(file)
                    file_struc.extend(parser_cls.file_parser(file=vm_file, filename=filename))
            except FileNotFoundError as e:
                raise FileNotFoundError(f"File {file} was not found") from e

        with open(output_file, "w") as asm_file:
            asm_file.write("\n".join(file_struc))

        print(f"Successfully translated {len(files)} file(s) to {output_file}")

if __name__ == "__main__":
    VMTranslator.open_file()