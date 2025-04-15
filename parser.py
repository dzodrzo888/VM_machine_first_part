"""This module is used to parse the code."""

class Parser:
    def __init__(self):
        self.file_struc = ["@256", "D=A", "@SP", "M=D"]
        self.SP = 256
        self.label_count = 0
        self.current_file = ""

        def command_parser(self, line: str) -> list:
        if line.startswith("//") or line == "":
            return
        # Remove inline comments
        line = line.split("//")[0].strip()
        if not line:
            return
            
        self.file_struc.append(f"// {line}")
        
        if line in ["add", "sub", "neg", "eq", "lt", "gt", "and", "or", "not"]:
            self.arithmetic_logic(line)
        elif "push" in line or "pop" in line:
            self.push_pop_execute(line)
        elif line.startswith("label"):
            self.handle_label(line)
        elif line.startswith("goto"):
            self.handle_goto(line)
        elif line.startswith("if-goto"):
            self.handle_if_goto(line)
        elif line.startswith("function"):
            self.handle_function(line)
        elif line.startswith("call"):
            self.handle_call(line)
        elif line.startswith("return"):
            self.handle_return()

    def handle_label(self, line: str):
        _, label = line.split()
        self.file_struc.append(f"({self.current_file}${label})")

    def handle_goto(self, line: str):
        _, label = line.split()
        self.file_struc.extend([
            f"@{self.current_file}${label}",
            "0;JMP"
        ])

    def handle_if_goto(self, line: str):
        _, label = line.split()
        self.file_struc.extend([
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            f"@{self.current_file}${label}",
            "D;JNE"
        ])

    def handle_function(self, line: str):
        _, function_name, num_locals = line.split()
        self.file_struc.append(f"({function_name})")
        for _ in range(int(num_locals)):
            self.file_struc.extend([
                "@0",
                "D=A",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
            ])

    def handle_call(self, line: str):
        _, function_name, num_args = line.split()
        return_address = f"RETURN_{self.label_count}"
        self.label_count += 1

        self.file_struc.extend([
            f"@{return_address}",
            "D=A",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            "@LCL",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            "@ARG",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            "@THIS",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            "@THAT",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            f"@{int(num_args) + 5}",
            "D=A",
            "@SP",
            "D=M-D",
            "@ARG",
            "M=D",
            "@SP",
            "D=M",
            "@LCL",
            "M=D",
            f"@{function_name}",
            "0;JMP",
            f"({return_address})"
        ])

    def handle_return(self):
        self.file_struc.extend([
            "@LCL",
            "D=M",
            "@R13",
            "M=D",
            "@5",
            "A=D-A",
            "D=M",
            "@R14",
            "M=D",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "@ARG",
            "A=M",
            "M=D",
            "@ARG",
            "D=M+1",
            "@SP",
            "M=D",
            "@R13",
            "AM=M-1",
            "D=M",
            "@THAT",
            "M=D",
            "@R13",
            "AM=M-1",
            "D=M",
            "@THIS",
            "M=D",
            "@R13",
            "AM=M-1",
            "D=M",
            "@ARG",
            "M=D",
            "@R13",
            "AM=M-1",
            "D=M",
            "@LCL",
            "M=D",
            "@R14",
            "A=M",
            "0;JMP"
        ])

    def push_pop_execute(self, line: str):
        parts = line.split()
        cmd = parts[0]
        segment = parts[1]
        index = parts[2]
        
        if cmd == "push":
            self.handle_push(segment, index)
        elif cmd == "pop":
            self.handle_pop(segment, index)
    
    def handle_push(self, segment, index):
        if segment == "constant":
            self.file_struc.extend([
                f"@{index}",
                "D=A",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
            ])
        elif segment in ["local", "argument", "this", "that"]:
            seg_map = {
                "local": "LCL",
                "argument": "ARG",
                "this": "THIS",
                "that": "THAT"
            }
            self.file_struc.extend([
                f"@{index}",
                "D=A",
                f"@{seg_map[segment]}",
                "A=M+D",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
            ])
        elif segment == "temp":
            self.file_struc.extend([
                f"@{index}",
                "D=A",
                "@5",
                "A=A+D",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
            ])
        elif segment == "pointer":
            ptr = "THIS" if index == "0" else "THAT"
            self.file_struc.extend([
                f"@{ptr}",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
            ])
        elif segment == "static":
            self.file_struc.extend([
                f"@{self.current_file}.{index}",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
            ])
    
    def handle_pop(self, segment, index):
        if segment in ["local", "argument", "this", "that"]:
            seg_map = {
                "local": "LCL",
                "argument": "ARG",
                "this": "THIS",
                "that": "THAT"
            }
            self.file_struc.extend([
                f"@{index}",
                "D=A",
                f"@{seg_map[segment]}",
                "D=M+D",
                "@R13",
                "M=D",
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                "@R13",
                "A=M",
                "M=D"
            ])
        elif segment == "temp":
            self.file_struc.extend([
                f"@{index}",
                "D=A",
                "@5",
                "D=A+D",
                "@R13",
                "M=D",
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                "@R13",
                "A=M",
                "M=D"
            ])
        elif segment == "pointer":
            ptr = "THIS" if index == "0" else "THAT"
            self.file_struc.extend([
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                f"@{ptr}",
                "M=D"
            ])
        elif segment == "static":
            self.file_struc.extend([
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                f"@{self.current_file}.{index}",
                "M=D"
            ])
    
    def arithmetic_logic(self, command):
        if command == "add":
            self.add()
        elif command == "sub":
            self.sub()
        elif command == "neg":
            self.neg()
        elif command == "eq":
            self.eq()
        elif command == "gt":
            self.gt()
        elif command == "lt":
            self.lt()
        elif command == "and":
            self.and_()
        elif command == "or":
            self.or_()
        elif command == "not":
            self.not_()
    
    def add(self):
        self.file_struc.extend([
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "@SP",
            "M=M-1",
            "A=M",
            "M=M+D",
            "@SP",
            "M=M+1"
        ])
    
    def sub(self):
        self.file_struc.extend([
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "@SP",
            "M=M-1",
            "A=M",
            "M=M-D",
            "@SP",
            "M=M+1"
        ])
    
    def neg(self):
        self.file_struc.extend([
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "D=-D",
            "M=D",
            "@SP",
            "M=M+1"
        ])
    
    def eq(self):
        true_label = f"EQ_TRUE_{self.label_count}"
        false_label = f"EQ_FALSE_{self.label_count}"
        end_label = f"EQ_END_{self.label_count}"
        
        self.file_struc.extend([
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M-D",
            f"@{true_label}",
            "D;JEQ",
            f"@{false_label}",
            "0;JMP",
            f"({true_label})",
            "@SP",
            "A=M",
            "M=-1",
            f"@{end_label}",
            "0;JMP",
            f"({false_label})",
            "@SP",
            "A=M",
            "M=0",
            f"({end_label})",
            "@SP",
            "M=M+1"
        ])
        self.label_count += 1
    
    def lt(self):
        true_label = f"LT_TRUE_{self.label_count}"
        false_label = f"LT_FALSE_{self.label_count}"
        end_label = f"LT_END_{self.label_count}"
        
        self.file_struc.extend([
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M-D",
            f"@{true_label}",
            "D;JLT",
            f"@{false_label}",
            "0;JMP",
            f"({true_label})",
            "@SP",
            "A=M",
            "M=-1",
            f"@{end_label}",
            "0;JMP",
            f"({false_label})",
            "@SP",
            "A=M",
            "M=0",
            f"({end_label})",
            "@SP",
            "M=M+1"
        ])
        self.label_count += 1
    
    def gt(self):
        true_label = f"GT_TRUE_{self.label_count}"
        false_label = f"GT_FALSE_{self.label_count}"
        end_label = f"GT_END_{self.label_count}"
        
        self.file_struc.extend([
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M-D",
            f"@{true_label}",
            "D;JGT",
            f"@{false_label}",
            "0;JMP",
            f"({true_label})",
            "@SP",
            "A=M",
            "M=-1",
            f"@{end_label}",
            "0;JMP",
            f"({false_label})",
            "@SP",
            "A=M",
            "M=0",
            f"({end_label})",
            "@SP",
            "M=M+1"
        ])
        self.label_count += 1
    
    def and_(self):
        self.file_struc.extend([
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "@SP",
            "M=M-1",
            "A=M",
            "M=M&D",
            "@SP",
            "M=M+1"
        ])
    
    def or_(self):
        self.file_struc.extend([
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "@SP",
            "M=M-1",
            "A=M",
            "M=M|D",
            "@SP",
            "M=M+1"
        ])
    
    def not_(self):
        self.file_struc.extend([
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "D=!D",
            "M=D",
            "@SP",
            "M=M+1"
        ])

    def file_parser(self, file, filename) -> list:
        self.current_file = filename.split("/")[-1].split(".")[0]
        for line in file:
            line_read = line.rstrip().strip()
            self.command_parser(line=line_read)
        
        return self.file_struc