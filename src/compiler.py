
from tree_sitter import Language, Parser
import type_check


Language.build_library(
  # Store the library in the `build` directory
  './build/sql.so',

  # Include one or more languages
  [
    './tree-sitter-dbt-jinja',
  ]
)

JINJA2_LANGUAGE = Language('./build/sql.so', 'dbt_jinja')

refs = set()
sources = set()
configs = dict()

def text_from_node(source_bytes, node):
    return source_bytes[node.start_byte:node.end_byte].decode('utf8')

def named_children(node):
    return list(filter(lambda x: x.is_named, node.children))

def strip_quotes(text):
    if text:
        return text[1:-1]

# expects node to have NO ERRORS in any of its subtrees
def extract_refs(source_bytes, node, data):
    return data # TODO STUB

    # if node.type == 'dbt_jinja_ref':
    #     package_name = node.child_by_field_name('dbt_package_name')
    #     model_name = node.child_by_field_name('dbt_model_name') 
    #     fmodel_name = strip_quotes(text_at(string, model_name))
    #     if not package_name:
    #         ref = fmodel_name
    #     else:
    #         ref = (
    #             strip_quotes(text_at(string, package_name)),
    #             fmodel_name
    #         )
    #     data['refs'].add(ref)

    # elif node.type == 'dbt_jinja_source':
    #     source_name = node.child_by_field_name('dbt_source_name')
    #     table_name = node.child_by_field_name('dbt_source_table')
    #     source = (
    #         strip_quotes(text_at(string, source_name)),
    #         strip_quotes(text_at(string, table_name))
    #     )
    #     data['sources'].add(source)

    # elif node.type == 'dbt_jinja_config':
    #     config_nodes = [child for child in node.children if child.type == 'kwarg_expression']
    #     for config in config_nodes:
    #         try:
    #             arg, _, value = config.children
    #         except Exception as e:
    #             raise e

    #         arg_val = text_at(string, arg)
    #         val_val = strip_quotes(text_at(string, value))
    #         data['configs'][arg_val] = val_val

    # for child in node.children:
    #     extract_refs(string, child, data)

def error_count(node, count):
    total = count
    if node.type == 'ERROR':
        total += 1

    for child in node.children:
        total += error_count(child, total)

    return total

def get_parser():
    parser = Parser()
    parser.set_language(JINJA2_LANGUAGE)
    return parser

# entry point function
def parse_typecheck_extract(parser, string):
    source_bytes = bytes(string, "utf8")
    tree = parser.parse(source_bytes)
    count = error_count(tree.root_node, 0)
    data = {
        'refs': set(),
        'sources': set(),
        'configs': dict(),
        'python_jinja': False
    }
    # if there are no _parsing errors_ check for _type errors_
    if count <= 0:
        # checked should be a new typed ast, but we don't have that machinery yet.
        # this is the same untyped ast for now.
        checked_ast_or_error = type_check.type_check(source_bytes, tree.root_node)
        data2 = dict(data)
        # if there are type errors
        if isinstance(checked_ast_or_error, type_check.TypeCheckFailure):
            data2['python_jinja'] = True
            return data2
        # if there are no parsing errors and no type errors, extract stuff!
        else:
            typed_root = checked_ast_or_error
            extract_refs(source_bytes, typed_root, data2)
            return data2
    # if this limited tree-sitter implementaion can't parse it, python jinja will have to
    else:
        data2 = dict(data)
        data2['python_jinja'] = False
        return data2
