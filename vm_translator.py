"""This module is used as a main module for opening vm file, reading it and converting to to asm code."""
import sys
import os
import parser

class VMTranslator:
    @staticmethod
    def open_file():
        if len(sys.argv) != 2:
            print("Usage: python vm_translator.py file.vm")
            sys.exit(1)

        input_file = sys.argv[1]
        if not input_file.endswith(".vm"):
            print("Error: Input file must have .vm extension")
            sys.exit(1)

        output_file = input_file.replace(".vm", ".asm")
        
        parser_cls = parser.Parser()
        try:
            with open(input_file) as vm_file:
                filename = os.path.basename(input_file)
                file_struc = parser_cls.file_parser(file=vm_file, filename=filename)
                
            with open(output_file, "w") as asm_file:
                asm_file.write("\n".join(file_struc))
                
            print(f"Successfully translated {input_file} to {output_file}")
            
        except FileNotFoundError as e:
            raise FileNotFoundError("File was not found please input correct file") from e

if __name__ == "__main__":
    VMTranslator.open_file()