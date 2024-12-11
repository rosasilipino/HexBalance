# Name: Rosa Lisa Silipino
# Date: Dec 10, 2024
# SDSU ID: 130403608
# Assignment: Final Project: HexBalance Interpreter
# File Name: interpreter.py
# # I have neither given nor received unauthorized aid in completing 
# this work, nor have I presented someone else's work as my own.

import re

"""
A class that tokenizes mathematical and logical expressions.
Utilizes the operators defined in the EsolangInterpreter class to know supported operators and precedence.
"""
class Lexer:
    def __init__(self, operators):
        self.operators = operators

    """
    Function creates a list of tokens from a given expression returning a list of tokens.
    Breaks down the expression into individual tokens such as :
    - Numeric values
    - String literals
    - Variables
    - Operators
    """
    def tokenize(self, expr):
        tokens = []
        current_token = ''
        i = 0
        # Iterate through the expression and build tokens
        while i < len(expr):
            char = expr[i]
            # Handle whitespace.
            if char.isspace():
                if current_token:
                    tokens.append(current_token)
                    current_token = ''
            # Handle parentheses as separate tokens.
            elif char in '()': 
                # If current token is not empty, add it to the list of tokens.
                if current_token:
                    tokens.append(current_token)
                tokens.append(char)
                current_token = ''
            # Handle multi-character operators like //.
            elif expr[i:i + 2] in self.operators:
                if current_token:
                    tokens.append(current_token)
                tokens.append(expr[i:i + 2])
                current_token = ''
                i += 1
            # Handle single-character operators.
            elif char in self.operators:
                if current_token:
                    tokens.append(current_token)
                tokens.append(char)
                current_token = ''
            # Handle alphanumeric characters.
            else:
                current_token += char
            i += 1
        if current_token:
            tokens.append(current_token)
        return tokens

"""
A customer interpreter for HexBalance esoteric programming language.

Primary focus of this class is to interpreter two sections of the HexBalance code:
- LOGIC: Contains rules and conditions to be evaluated.
- FORCE: Contains commands to be executed.
"""
class EsolangInterpreter:
    
    # Attributes are initialized in the constructor to store rules, variables, and operators.
    def __init__(self):
        self.rules = {}  
        self.variables = {}  
        self.initialized_variables = set()
        self.operators = {
            '+': (lambda a, b: a + b, 5),
            '-': (lambda a, b: a - b, 5),
            '*': (lambda a, b: a * b, 6),
            '/': (lambda a, b: a / b, 6),
            '//': (lambda a, b: a // b, 6),
            '%': (lambda a, b: a % b, 6),
            '==': (lambda a, b: a == b, 4),
            'not': (lambda a, b: a != b, 4),
            '<': (lambda a, b: a < b, 4),
            '>': (lambda a, b: a > b, 4),
            'and': (lambda a, b: a and b, 3),
            'or': (lambda a, b: a or b, 2),
        }
        self.lexer = Lexer(self.operators)
        
    """
    Method tokenizes the expression and evaluates it basaed on precedence of operators.
    Resolves variables and rules, while returning the evaluated result of the expression.
    """
    def evaluate_expression(self, expr):
    
        tokens = self.lexer.tokenize(expr)

        def get_prec(op):
            return self.operators[op][1]

        def apply_op(ops, vals):
            op_func = self.operators[ops.pop()][0]
            b = vals.pop()
            a = vals.pop()
            vals.append(op_func(a, b))

        values = []
        ops = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.isdigit():  # Handle numeric values
                values.append(int(token))
            elif token.startswith('"') and token.endswith('"'):  # Handle string literals
                values.append(token.strip('"'))
            elif token in self.variables:  # Use variable values
                if token not in self.initialized_variables:
                    raise RuntimeError(f"Variable '{token}' is not initialized. Use 'set' to initialize.")
                values.append(self.variables[token])
            elif token in self.rules:  # Evaluate rules as part of expressions
                rule_output = self.execute_rule(token)
                if rule_output is not None:
                    values.append(rule_output)
                else:
                    values.append(False)  # Consider failed rule evaluation as False
            elif token in self.operators:  # Handle operators
                while ops and ops[-1] in self.operators and get_prec(ops[-1]) >= get_prec(token):
                    apply_op(ops, values)
                ops.append(token)
            else:
                raise ValueError(f"Unrecognized token: {token}")
            i += 1

        while ops:
            apply_op(ops, values)
        return values[0]

    """ 
    Method that parses the LOGIC section of the HexBalance code.
    Key features include:
    - Parsing rules and storing them in a dictionary.
    - Printing the rules that have been added.
    - Handles conditions and results for each rule.
    Parameters:
    - logic_lines: List of lines in the LOGIC section.
    """
    def parse_logic(self, logic_lines):
        #Parse the LOGIC section and store rules.
        for line in logic_lines:
            # Get the name of the rule, by removing 'rule' and stores the statement after the ':'
            if line.startswith("rule"):
                _, name, operation = line.split(" ", 2)
                name = name.rstrip(":")
                condition = None
                result = None
                #  After the '->' store the condition, removing 'if' if a condition is present.
                if "->" in operation:
                    parts = operation.split("->", 1)
                    if parts[0].strip().startswith("if "):  
                        condition = parts[0].strip()[3:] 
                    result = parts[1].strip() # Items after '->' is the rules results.
                else:
                    condition = operation.strip()

                self.rules[name] = {"condition": condition, "result": result}
                print(f"Rule added: {name} -> {self.rules[name]}")

    """
    Method that parses the FORCE section of the HexBalance code.
    Key features include:
    - Handling 'set' for initialization.
    - Handling assignment of variables.
    - Rule execution
    - Handling 'ekko' statements
    - Control flow constructs like 'if', 'for', etc.
    Parameters:
    - force_lines: List of lines in the FORCE section.
    """
    def parse_force(self, force_lines):
            """Parse the FORCE section and execute commands."""
            i = 0
            while i < len(force_lines):
                line = force_lines[i].strip().split("#")[0].strip()  # Remove comments
                if not line or line in {"start", "end"}:
                    i += 1
                    continue
                
                if line.startswith("set "):  # Handle 'set' for initialization
                    var, value = map(str.strip, line[4:].split("=", 1))
                    value = value.strip("()")
                    if var in self.initialized_variables:
                        raise RuntimeError(f"Variable '{var}' is already initialized. Use assignment without 'set'.")
                    self.variables[var] = self.evaluate_expression(value)
                    self.initialized_variables.add(var)

                elif "=" in line:  # Handle assignment
                    var, value = map(str.strip, line.split("=", 1))
                    if var not in self.initialized_variables:
                        raise RuntimeError(f"Variable '{var}' is not initialized. Use 'set' to initialize.")
                    value = value.strip("()")
                    self.variables[var] = self.evaluate_expression(value)
                    
                    # **** HELPFUL DEBUGGING PRINT TO SEE VARIABLE UPDATES ****
                    #print(f"Debug: Variable {var} updated to {self.variables[var]}")

                elif line.startswith("ekko"):
                    _, content = line.split("(", 1)
                    content = content.rstrip(")")

                    # Handle string literals
                    if content.startswith('"') and content.endswith('"'):
                        print(content.strip('"'))

                    # Handle rule chaining with 'or'
                    else:
                        for sub_rule in content.split(" or "):
                            sub_rule = sub_rule.strip()
                            if sub_rule in self.rules:
                                output = self.execute_rule(sub_rule)
                                if output is not None:  # Print first valid result
                                    print(output)
                                    break
                            elif sub_rule.isdigit():  # Handle numeric values
                                print(int(sub_rule))
                                break
                            elif sub_rule in self.variables:  # Handle variables
                                if sub_rule in self.initialized_variables:
                                    print(self.variables[sub_rule])
                                    break
                                else:
                                    raise RuntimeError(f"Variable '{sub_rule}' is not initialized.")
                            else:
                                print(f"Unrecognized ekko content: {sub_rule}")

                # Handle other constructs (while, if, for, etc.)
                elif line.startswith("for "):
                    i = self.handle_for(line, force_lines, i)
                else:
                    print(f"Error: Unrecognized statement '{line}'")

                i += 1

    """
    Iterates over defined range with start and end values, incrementing by step value.
    Returns the index of the line after the for loop.
    Parameters:
    - line: Line containing the for loop.
    - lines: All the lines in the loop.
    - index: Index of the current line
    """
    def handle_for(self, line, lines, index):
        """Handle for loops."""
        _, loop_var, _, start, _, end, _, step = line.split()
        start = self.variables[start] if start in self.variables else int(start)
        end = self.variables[end] if end in self.variables else int(end)
        step = self.variables[step] if step in self.variables else int(step)

        self.variables[loop_var] = start
        loop_body = []
        index += 1
        while index < len(lines) and not lines[index].startswith("end"):
            loop_body.append(lines[index].strip())
            index += 1

        while self.variables[loop_var] <= end:
            self.parse_force(loop_body)
            self.variables[loop_var] += step
        return index
    
    """
    Checks if a rule (if any) is defined and executes if the condition is true.
    Returns the result of the rule if the condition is true or None if false.
    Parameters: 
    - rule_name: Name of the rule to be executed.
    """
    def execute_rule(self, rule_name):
        """Execute a defined rule."""
        if rule_name not in self.rules:
            print(f"Error: Undefined rule '{rule_name}'")
            return None
        rule = self.rules[rule_name]
        condition = rule["condition"]
        result = rule["result"]

        # Check condition
        if condition and not self.evaluate_expression(condition):
            return None  # Skip if condition is false

        # Return result if condition is true
        if result:
            # Handle result as expression, variable, or string
            if any(op in result for op in self.operators):
                return self.evaluate_expression(result)
            elif result in self.variables:
                return self.variables[result]
            return result.strip('"')

        return None
    
    """
    Parses the LOGIC and FORCE sections and executes FORCE based on LOGIC.
    Determines what lines belong in what code block in the program LOGIC or FORCE.
    Parameters:
    - file_path: Path to the file to be interpreted.  
    """
    def run(self, file_path):
        """Run the interpreter."""
        try:
            with open(file_path, 'r') as file:
                code = file.read()
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return
        lines = code.strip().split("\n")
        logic_section = []
        force_section = []
        in_logic = False
        in_force = False

        for line in lines:
            if line == "LOGIC":
                in_logic = True
                in_force = False
            elif line == "FORCE":
                in_logic = False
                in_force = True
            elif in_logic:
                logic_section.append(line.strip())
            elif in_force:
                force_section.append(line.strip())

        self.parse_logic(logic_section)
        self.parse_force(force_section)
        
def main():
    # Run the programs
    interpreter = EsolangInterpreter()

    print("Running math.hxbal:")
    interpreter.run("math.hxbal")

    print("\nRunning light.hxbal:")
    interpreter.run("light.hxbal")

    print("\nRunning helloworld.hxbal:")
    interpreter.run("helloworld.hxbal")

    print("\nRunning fizzbuzz.hxbal:")
    interpreter.run("fizzbuzz.hxbal")

if __name__ == "__main__":
    main()
