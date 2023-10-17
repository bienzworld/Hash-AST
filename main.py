import sqlparse
import hashlib
import unittest

def sql_to_ast(sql_query):
    parsed = sqlparse.parse(sql_query)
    statement = parsed[0]
    ast = statement.tokens
    return ast


def hash_column_names(ast):
    column_name_map = {}

    def traverse(tokens):
        for token in tokens:
            if token.ttype is sqlparse.tokens.Name and not isinstance(token, sqlparse.sql.Identifier):
                original_column_name = token.value
                hashed_column_name = hashlib.sha256(original_column_name.encode()).hexdigest()
                column_name_map[original_column_name] = hashed_column_name
                token.value = hashed_column_name

            elif isinstance(token, sqlparse.sql.TokenList):
                traverse(token.tokens)

    traverse(ast)
    return ast, column_name_map


def rebuild_sql_from_ast(ast):
    sql_query = ""
    for token in ast:
        if token.ttype is sqlparse.tokens.Name:
            sql_query += token.value
        else:
            sql_query += str(token)
    return sql_query



class TestSQLParsing(unittest.TestCase):
    def test_sql_to_ast(self):
        sql_query = "SELECT a, b FROM test WHERE a = 5"
        ast = sql_to_ast(sql_query)
        self.assertIsNotNone(ast)

    def test_hash_column_names(self):
        sql_query = "SELECT a, b FROM test WHERE a = 5"
        ast = sql_to_ast(sql_query)
        ast_with_hashed_names, column_name_map = hash_column_names(ast)

        self.assertNotEqual(sql_query, rebuild_sql_from_ast(ast_with_hashed_names))
        self.assertGreater(len(column_name_map), 0)

    def test_rebuild_sql_from_ast(self):
        sql_query = "SELECT a, b FROM test WHERE a = 5"
        ast = sql_to_ast(sql_query)
        ast_with_hashed_names, _ = hash_column_names(ast)
        hashed_sql = rebuild_sql_from_ast(ast_with_hashed_names)

        self.assertEqual(hashed_sql, rebuild_sql_from_ast(ast_with_hashed_names))



if __name__ == '__main__':
    sql_query = "SELECT a, b FROM test WHERE a = 5"
    ast = sql_to_ast(sql_query)
    ast_with_hashed_names, column_name_map = hash_column_names(ast)

    hashed_sql = rebuild_sql_from_ast(ast_with_hashed_names)

    print("Original SQL Query:")
    print(sql_query)
    print("\nModified SQL Query:")
    print(hashed_sql)

    print("\nColumn Name Mapping:")
    print(column_name_map)
    unittest.main()



