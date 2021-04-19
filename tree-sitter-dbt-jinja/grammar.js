
function commaSep1(rule) {
    return sep1(rule, ',');
}

function sep1(rule, separator) {
    return seq(rule, repeat(seq(separator, rule)))
}


module.exports = grammar ({
  name: 'dbt_jinja',

  rules: {
    source_file: $ => repeat(
        choice(
            prec(10, $.jinja_macro_block),
            prec(10, $._jinja_block),
            prec(1, $._text)
        )
    ),

    _jinja_block: $ => seq(
        '{{',
        $._expr,
        '}}'
    ),

    // This is awkward regex because we aren't parsing anything
    // inside the block like a regular parser would want to.
    // TODO what about multiple linebreaks inside a jinja macro?
    jinja_macro_block: $ => seq(
        '{%',
        /(.*)([%].{1}|.{1}[}])/
        ),

    // This defines all the meat of the parser
    _expr: $ => choice(
        $.fn_call,
        $.list,
        $.dict,
        $.lit_string,
        $.bool,
    ),

    fn_call: $ => seq(
        field('fn_name', $.identifier),
        field('argument_list', $.argument_list)
    ),

    argument_list: $ => seq(
        '(',
        optional(commaSep1(
            choice(
                $._expr,
                $.kwarg
            )
        )),
        // TODO to match python add optional(','),
        ')'
    ),

    lit_string: $ => seq(
        choice(
            seq(
                "'",
                token(/[^']*/),
                "'",
            ),
            seq(
                '"',
                token(/[^"]*/),
                '"',
            )
        )
    ),

    bool: $ => choice(
        'True',
        'False'
    ),

    list: $ => seq(
        '[',
        optional(commaSep1($._expr)),
        optional(','),
        ']'
    ),

    dict: $ => seq(
        '{',
        optional(commaSep1($.pair)),
        optional(','),
        '}'
    ),

    pair: $ => seq(
        field('key', $.lit_string),
        ':',
        field('value', $._expr)
    ),

    identifier: $ => $._identifier,

    _identifier: $ => token(/[a-zA-Z_][a-zA-Z0-9_]*/),
    // Unicode identifiers like python does: /[_\p{XID_Start}][_\p{XID_Continue}]*/

    kwarg: $ => seq(
        field("key", $.identifier),
        '=',
        field("value", $._expr),
    ),

    _text: $ => /[^{}]+/

  }
});
