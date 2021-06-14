use std::fmt;
use std::fmt::Display;
use std::str::Utf8Error;

// TODO change Errors to contain &str not String?


// Top-level error type in the hierarchy
#[derive(Debug, Clone, Eq, PartialEq)]
pub enum ParseError {
    SourceE(SourceError),
    TypeE(TypeError),
}

impl Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ParseError::SourceE(e) => Display::fmt(e, f),
            ParseError::TypeE(e) => Display::fmt(e, f),
        }
    }
}

// TODO use crate `thiserror` to simplify boilerplate
#[derive(Debug, Clone, Eq, PartialEq)]
pub enum SourceError {
    TreeSitterError,
    Utf8Err(Utf8Error),
    BadBoolean(String),
    UnknownNodeType(String),
    MissingValue(String, String),
    ParseFailure,
}

impl Display for SourceError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            SourceError::TreeSitterError =>
                write!(f, "tree-sitter found an error"),
            SourceError::Utf8Err(e) =>
                e.fmt(f),
            SourceError::BadBoolean(s) =>
                write!(f, "Unknown Boolean value: {}", s),
            SourceError::UnknownNodeType(s) =>
                write!(f, "Unknown node type: {}", s),
            SourceError::MissingValue(outer, inner) =>
                write!(f, "{} is missing the required value {}", outer, inner),
            SourceError::ParseFailure =>
                write!(f, "tree-sitter failed to parse the source"),
        }
    }
}

#[derive(Debug, Clone, Eq, PartialEq)]
pub enum TypeError {
    BadAssignment(String, String),
    KwargsAreNotLast,
    // TODO expected should be a Vec<usize> (e.g. - ref takes 1 or 2 args)
    ArgumentMismatch { expected: String, found: usize },
    // use ExprU::type_string() when creating this exception to get the right human readable name for each type.
    // TODO add a new type `ExprType` that maps 1:1 values - types. Do string conversion after on that value.
    TypeMismatch { expected: String, got: String },
    UnrecognizedFunction(String),
    UnexpectedKwarg(String),
    ExcludedKwarg(String),
    UnsupportedConfigValue(String),
}

impl Display for TypeError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            TypeError::BadAssignment(outer, inner) =>
                write!(f, "{} cannot be assigned a {}", outer, inner),
            TypeError::KwargsAreNotLast =>
                write!(f, "Keyword arguments must come at the end of the argument list."),
            TypeError::ArgumentMismatch { expected, found } =>
                write!(f, "Expected {} arguments. Found {}.", expected, found),
            TypeError::TypeMismatch { expected, got } =>
                write!(f, "Expected {}. Got {} ", expected, got),
            TypeError::UnrecognizedFunction(name) =>
                write!(f, "Found unrecognized function named {}.", name),
            TypeError::UnexpectedKwarg(key) =>
                write!(f, "Found unexpected keyword argument {}.", key),
            TypeError::ExcludedKwarg(key) =>
                write!(f, "Excluded keyword argument found: {}.", key),
            TypeError::UnsupportedConfigValue(value_type) =>
                write!(f, "Config value cannot be of the type {}.", value_type),
        }
    }
}