# 81.25/100

import re
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.type == other.type and self.value == other.value
        return False

    def __repr__(self):
        return f'Token({self.type}, {self.value})'

class Lexer:
    def __init__(self, input):
        self.input = input
        self.position = 0

    def tokenize(self):
        tokens = []  
        while self.position < len(self.input):
            char = self.input[self.position]  
            if char.isspace():  
                self.position += 1
                continue
            elif char.isalpha():  
                token = self.tokenize_variable()
            elif char.isdigit():  
                if (self.position+1 < len(self.input) and self.input[self.position+1] == '.'):
                    token = self.tokenize_float()
                else:
                    token = self.tokenize_integer()
            elif char in ['+', '-', '*', '/']:  
                token = self.tokenize_operator()
            elif char == '=':  
                token = self.tokenize_assign()
            elif char == ';':  
                token = self.tokenize_semicolon()
            elif char in ['(', ')']:  
                token = self.tokenize_parenthesis()
            elif char == "'":  # If it's a char
                token = self.tokenize_char()
            else:  
                raise Exception(f"Invalid character: {char}")
            tokens.append(token)  
        return tokens  

    def tokenize_variable(self):
        start = self.position
        while self.position < len(self.input) and self.input[self.position].isalpha():
            self.position += 1
        return Token('VARIABLE', self.input[start:self.position])

    def tokenize_integer(self):
        start = self.position
        while self.position < len(self.input) and self.input[self.position].isdigit():
            self.position += 1
        return Token('INTEGER', int(self.input[start:self.position]))

    def tokenize_float(self):
        start = self.position
        while self.position < len(self.input) and (self.input[self.position].isdigit() or self.input[self.position] == '.'):
            self.position += 1
        return Token('FLOAT', float(self.input[start:self.position]))

    def tokenize_char(self):
        start = self.position
        self.position += 1  # Skip the opening quote
        while self.position < len(self.input) and self.input[self.position] != "'":
            self.position += 1
        self.position += 1  # Skip the closing quote
        return Token('CHAR', self.input[start+1:self.position-1])

    def tokenize_operator(self):
        operator = self.input[self.position]
        self.position += 1
        return Token('OPERATOR', operator)

    def tokenize_assign(self):
        self.position += 1
        return Token('ASSIGN', '=')

    def tokenize_semicolon(self):
        self.position += 1
        return Token('SEMICOLON', ';')

    def tokenize_parenthesis(self):
        parenthesis = self.input[self.position]
        self.position += 1
        return Token('PARENTHESIS', parenthesis)



class SymbolTable:
    def __init__(self):
        self.table = {}

    def add(self, identifier, type, initialized=False):
        if identifier in self.table:
            raise Exception(f"Variable '{identifier}' already declared.")
        self.table[identifier] = {'type': type, 'initialized': initialized}

    def is_initialized(self, identifier):
        if identifier not in self.table:
            raise Exception(f"Variable '{identifier}' is not declared.")
        return self.table[identifier]['initialized']

    def set_initialized(self, identifier):
        if identifier not in self.table:
            raise Exception(f"Variable '{identifier}' is not declared.")
        self.table[identifier]['initialized'] = True

    def lookup(self, identifier):
        if identifier not in self.table:
            raise Exception(f"Variable '{identifier}' is not declared.")
        return self.table[identifier]['type']

    def update(self, identifier, new_type):
        if identifier not in self.table:
            raise Exception(f"Variable '{identifier}' is not declared.")
        self.table[identifier]['type'] = new_type


class TypeChecker:
    @staticmethod
    def check_assignment(target_type, value_type):
        if target_type == "INTEGER" and value_type == "FLOAT":
            return False
        return True

    @staticmethod
    def result_type_of_op(left_type, op, right_type):
        if left_type == "INTEGER" and right_type == "INTEGER":
            return "INTEGER"
        elif left_type == "FLOAT" or right_type == "FLOAT":
            return "FLOAT"
        elif left_type == "CHAR" and right_type == "CHAR":
            if op in ["+", "*"]:
                return "CHAR"
        return None

    @staticmethod
    def check_op(left_type, op, right_type):
        if left_type == "CHAR" and right_type == "CHAR" and op == "+":
            return False
        result_type = TypeChecker.result_type_of_op(left_type, op, right_type)
        if result_type is None:
            return False
        return True



class Node:
    def __init__(self, type, value=None, children=None):
        self.type = type
        self.value = value
        self.children = children if children is not None else []

    def __str__(self, level=0):
        ret = "\t" * level + f'{self.type}: {self.value}\n'
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens  # Stores  list of tokens 
        self.position = 0  # Keeps track of  current position within  tokens list

    def consume(self, expected_type=None):
        # Consume method is used to consume a token from  tokens list
        current_token = self.tokens[self.position]  # gets current token
        # Checks if  current token matches  expected token type
        if expected_type and current_token.type != expected_type:
            # No match, raise an exception
            raise Exception(f"Syntax error: expected {expected_type}, got {current_token.type}")
        self.position += 1  # Moves to next token
        return current_token  # Returns current token

    def peek(self):
        # This method is used to look at  next token in  tokens list without consuming it
        return self.tokens[self.position]# This is the same as consume, but it doesn't increment the position.

    def parse(self):
        # This method is used to parse  tokens into a syntax tree
        statements = []  # Stores  parsed statements
        # Loops through  tokens and parses each statement
        while self.position < len(self.tokens):
            statement = self.parse_statement()
            statements.append(statement)
        # If exists remaining tokens after parsing, raises an exception
        if self.position < len(self.tokens):
            raise Exception(f"Syntax error: unexpected tokens at the end")
        # Returns a new 'Program' node with parsed statements as children
        return Node('Program', children=statements)# I don't know if this is the best way to do it, but it passed the tests.

    def parse_statement(self):
        # This method is used to parse a statement
        # If  next token is a variable, parses an assignment
        if self.peek().type == 'VARIABLE':
            return self.parse_assignment()
        else:
            # If  next token is not a variable, raises an exception
            raise Exception(f"Syntax error: invalid statement {self.peek().type}")

    def parse_assignment(self):
        # Parses an assignment, which is a variable followed by an equals sign and an expression
        variable = self.consume('VARIABLE')  # Consume  variable
        self.consume('ASSIGN')  # Consume  equals sign
        expression = self.parse_expression()  # Parse  expression on  right of  equals sign
        # Next line, check if there is a semicolon at the end of the statement. I strugled with this part for a while.
        # because I was trying to check if the next token was a semicolon, but that would consume the token.
        # So I had to check if the position was less than the length of the tokens list, and then check if the
        # next token was a semicolon.
        if self.position < len(self.tokens) and self.peek().type == 'SEMICOLON':# Also I don't know if this is the best way to do it.
            self.consume('SEMICOLON')  # Consume the semicolon
        else:
            raise Exception("Syntax error: unexpected end of input")  # Raise an exception if there's no semicolon
        # I thought that I should put this in the parse function, but I think it makes more sense to put it here.
        # It passed the tests, so I think it's fine.
        # Return a new assignment node with the variable and the expression as children
        return Node('AssignmentStatement', value=variable.value, children=[expression])

    def parse_expression(self):
        term = self.parse_term()  # Parse the first term
        # If the next token is an operator, parse the operation
        while self.position < len(self.tokens) and self.peek().type == 'OPERATOR':
            operator = self.consume('OPERATOR')  # Consume the operator
            next_term = self.parse_term()  # Parse the next term
            term = Node('Expression', value=operator.value, children=[term, next_term])  # Create a new expression node
        return term  # Return the expression node

    def parse_term(self):
        # Check the type of the next token and parse accordingly
        if self.peek().type == 'PARENTHESIS' and self.peek().value == '(':
            self.consume()  # Consume the opening parenthesis
            expression = self.parse_expression()  # Parse the expression inside the parentheses
            self.consume('PARENTHESIS')  # Consume the closing parenthesis
            return expression
        elif self.peek().type == 'INTEGER':
            integer = self.consume('INTEGER')  # Consume the integer
            return Node('Term', value=integer.value)  # Return a new term node with the integer value
        elif self.peek().type == 'VARIABLE':
            variable = self.consume('VARIABLE')  # Consume the variable
            return Node('Term', value=variable.value)  # Return a new term node with the variable value
        else:
            raise Exception(f"Syntax error: invalid term {self.peek().type}")  # Raise an exception if the term is invalid