
# # # # # # # # # # # # # # # # # # # # # # # # # #
# disclaimer: please don't use this to learn how  #
# type checking works. This is mostly a hack.     #
# # # # # # # # # # # # # # # # # # # # # # # # # #
from dataclasses import dataclass

@dataclass
class TypeCheckFailure():
    msg: str

@dataclass
class TypeCheckPass():
    pass

# These type checking functions are naive and too concrete
# Error messages are to be read by dbt devs to determine where tree-sitter is failing.
# All failures will simply pass to python-jina, this will just prevent the successfully parsing
# incorrect dbt jinja.
# TODO make these more abstract so they can apply to future functions for free.

def ref_check(args):
    if len(args) < 1 or len(args) > 2:
        return TypeCheckFailure(f"expected ref to have 1 or 2 arguments. found {len(args)}")
    for arg in args:
        if arg.type == 'kwarg':
            return TypeCheckFailure(f"unexpected keyword argument in ref")
        if arg.type != 'lit_string':
            return TypeCheckFailure(f"unexpected argument type in ref")
    return TypeCheckPass()

def config_check(args):
    if len(args) < 1:
        return TypeCheckFailure(f"expected config to have at least one argument. found {len(args)}")
    for arg in args:
        if arg.type != 'kwarg':
            return TypeCheckFailure(f"unexpected non keyword argument in config")
    return TypeCheckPass()

def source_check(args):
    if len(args) != 2:
        return TypeCheckFailure(f"expected source to 2 arguments. found {len(args)}")
    for arg in args:
        if arg.type != 'kwarg' and arg.type != 'lit_string':
            return TypeCheckFailure(f"unexpected argument type in source")
        if arg[0].type == 'kwarg' and arg[0].child_by_field_name('arg') != 'source_name':
            return TypeCheckFailure(f"first keyword argument in source must be source_name found {arg[0].child_by_field_name('arg')}")
        if arg[1].type == 'kwarg' and arg[1].child_by_field_name('arg') != 'table_name':
            return TypeCheckFailure(f"second keyword argument in source must be table_name found {arg[0].child_by_field_name('arg')}")
    return TypeCheckPass()

# hack
type_checkers = { 
    'fn_call': {
        'ref': ref_check,
        'config': config_check,
        'sources': source_check
    }
}

def flatten(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]

# return ALL the results. don't just stop at the first error
def _type_check(results, node):
    if node.type == 'fn_call':
        name = node.child_by_field_name('fn_name')
        args = node.child_by_field_name('argument_list')
        res = type_checkers['fn_call'][name](args)
        return results + [res] + flatten(list(map(lambda x: _type_check([], x), node.children)))
    else:
        return results + [TypeCheckPass()]

def type_check(node):
    all_type_errors = list(filter(lambda x: isinstance(x, TypeCheckFailure), _type_check([], node)))
    if len(all_type_errors) <= 0:
        # This ast would normally be a new typed ast, but we're not doing any of that yet.
        # Just know we can safely take the info out of the untyped ast is good enough for now.
        return node
    else:
        return all_type_errors


