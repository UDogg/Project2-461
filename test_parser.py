import unittest
from grammarParserStudent import Lexer, Parser, Token, Node, TypeChecker, SymbolTable


class CustomTextTestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.passed_tests = 0
        self.total_score = 100  

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed_tests += 1

    def print_result(self):
        total_tests = self.testsRun
        if total_tests == 0:
            print("No tests were run.")
            return
        score_per_test = self.total_score / total_tests
        earned_score = self.passed_tests * score_per_test
        print(f"\nPassed {self.passed_tests} out of {total_tests} tests")
        print(f"Score: {earned_score}/{self.total_score}")


class CustomTextTestRunner(unittest.TextTestRunner):
    def __init__(self, stream=None, descriptions=True, verbosity=1, failfast=False,
                 buffer=False, resultclass=None, warnings=None, *, tb_locals=False):
        resultclass = CustomTextTestResult
        super().__init__(stream, descriptions, verbosity, failfast, buffer, resultclass, warnings, tb_locals=tb_locals)

    def run(self, test):
        result = super().run(test)
        result.print_result()
        return result


class TestLexerParser(unittest.TestCase):

    def _get_ast_from_code(self, input_code):
        lexer = Lexer(input_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse()

    def test_lexer(self):
        input_code = "a = 5 + 3;"
        lexer = Lexer(input_code)
        tokens = lexer.tokenize()
        expected_tokens = [
            Token('VARIABLE', 'a'),
            Token('ASSIGN', '='),
            Token('INTEGER', 5),
            Token('OPERATOR', '+'),
            Token('INTEGER', 3),
            Token('SEMICOLON', ';')
        ]
        self.assertEqual(tokens, expected_tokens)

    def test_parser_valid_input(self):
        input_code = "a = 5;"
        try:
            ast = self._get_ast_from_code(input_code)
            self.assertIsInstance(ast, Node)
            print(f"AST for {input_code} is {ast}")
        except Exception as e:
            self.fail(f"Test failed with valid input due to {e}")

            
    def test_parser_multi_line(self):
        input_code = """
        a = 5 + 3;
        b = a * 2;
        c = a + b;
        """
        try:
            ast = self._get_ast_from_code(input_code)
            self.assertIsInstance(ast, Node)
            print(f"AST for multi-line input is {ast}")
        except Exception as e:
            self.fail(f"Test failed with multi-line valid input due to {e}")

    def test_parser_multiple_operations(self):
        input_code = """
        a = 5 + 3;
        b = a * 2 - 1;
        c = (a + b) * 2;
        """
        try:
            ast = self._get_ast_from_code(input_code)
            self.assertIsInstance(ast, Node)
            print(f"AST for {input_code} is {ast}")
        except Exception as e:
            self.fail(f"Test case failed: {e}")

    def test_parser_nested_expressions(self):
        input_code = """
        a = ((5 + 3) * 2) - 1;
        b = (a+1) * 2;
        """
        try:
            ast = self._get_ast_from_code(input_code)
            self.assertIsInstance(ast, Node)
            print(f"AST for {input_code} is {ast}")
        except Exception as e:
            self.fail(f"Test failed with nested expressions due to {e}")

    def test_parser_invalid_assignment(self):
        input_code = "5 = a;"
        with self.assertRaises(Exception) as context:
           self._get_ast_from_code(input_code)
        self.assertTrue('Syntax error' in str(context.exception))

    def test_parser_invalid_character(self):
        input_code = "a = % 5;"
        lexer = Lexer(input_code)
        with self.assertRaises(Exception) as context:
            lexer.tokenize()
        self.assertTrue('Invalid character' in str(context.exception))

    def test_parser_invalid_operation(self):
        input_code = "a = (5 + );"
        lexer = Lexer(input_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        with self.assertRaises(Exception) as context:
            parser.parse()
        self.assertTrue('Syntax error' in str(context.exception))
    
    def test_parser_invalid_inputs(self):
        input_code = """
        a = 5 + ;
        b = * 2;
        """
        lexer = Lexer(input_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        with self.assertRaises(Exception) as context:
            parser.parse()
        self.assertTrue('Syntax error' in str(context.exception))


    def test_missing_semicolon(self):
        input_code = "a = 5"
        lexer = Lexer(input_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        with self.assertRaises(Exception) as context:
            parser.parse()
            print(context.exception) 
            self.assertTrue('Syntax error: unexpected end of input' in str(context.exception))


    def test_symbol_table_operations(self):
        symbol_table = SymbolTable()
        with self.assertRaises(Exception):
            symbol_table.lookup("a")  

        symbol_table.add("a", "INTEGER")
        self.assertEqual(symbol_table.lookup("a"), "INTEGER")
        with self.assertRaises(Exception):
            symbol_table.add("a", "FLOAT") 

        symbol_table.update("a", "FLOAT")
        self.assertEqual(symbol_table.lookup("a"), "FLOAT")

        with self.assertRaises(Exception):
            symbol_table.lookup("b") 

    def test_lexer_floats_chars(self):
        input_code = "a = 5.23; b = 'c';"
        lexer = Lexer(input_code)
        tokens = lexer.tokenize()
        expected_tokens = [
            Token('VARIABLE', 'a'),
            Token('ASSIGN', '='),
            Token('FLOAT', 5.23),
            Token('SEMICOLON', ';'),
            Token('VARIABLE', 'b'),
            Token('ASSIGN', '='),
            Token('CHAR', 'c'),
            Token('SEMICOLON', ';')
        ]
        self.assertEqual(tokens, expected_tokens)

    def test_parser_declaration(self):
        input_code = "int a = 5; char b = 'c'; float c = 5.23; a = b;"  
        lexer = Lexer(input_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        with self.assertRaises(Exception) as context:
            parser.parse()
        self.assertTrue('Type mismatch' in str(context.exception) or 'Undeclared variable' in str(context.exception))

    def test_type_checker(self):
        self.assertTrue(TypeChecker.check_assignment("FLOAT", "INTEGER"))
        self.assertTrue(TypeChecker.check_assignment("CHAR", "CHAR"))
        self.assertFalse(TypeChecker.check_assignment("INTEGER", "FLOAT"))
        self.assertTrue(TypeChecker.check_op("INTEGER", "+", "INTEGER"))
        self.assertTrue(TypeChecker.check_op("FLOAT", "+", "INTEGER"))
        self.assertFalse(TypeChecker.check_op("CHAR", "+", "CHAR"))

    def test_type_mismatch(self):
        input_code = "int a = 5.23;"
        lexer = Lexer(input_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        with self.assertRaises(Exception) as context:
            parser.parse()
        self.assertTrue('Type mismatch' in str(context.exception))

    def test_char_assignment_and_invalid_op(self):
        input_code = """
        char a = 'c';
        a = a + 5;
        """
        lexer = Lexer(input_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        with self.assertRaises(Exception) as context:
            parser.parse()
        self.assertTrue('Incompatible types for operation' in str(context.exception))
    
if __name__ == '__main__':
    unittest.main(testRunner=CustomTextTestRunner(verbosity=2))


    