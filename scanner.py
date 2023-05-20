"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""
max_number_of_input_pins = 16
keywords = {'DEVICES', 'CONNECT', 'MONITOR', 'END', 'AND', 'NAND', 'OR', 'NOR',
            'DTYPE', 'XOR', 'SWITCH', 'CLOCK'}
dtype_input_pins = {"DATA", "SET", "CLEAR", "CLK"}
gate_pins = {f"I{i}" for i in range(1, max_number_of_input_pins + 1)}
input_pins = gate_pins.union(dtype_input_pins)
output_pins = {"Q", "QBAR"}
punctuation = {";": "semi-colon", ":": "colon", ",": "comma", ".": "dot",
               ">": "arrow"}


class Symbol:
    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None
        self.line_number = None
        self.column_number = None

    @staticmethod
    def is_string(string):
        """Return True if string is alphanumeric plus underscore.

        Parameters
        ----------
        string: str

        Returns
        -------
        is_type_string: bool
        """
        for char in string:  # Ensures all characters are alphanumeric or _
            if not char.isalnum() and char != "_":
                return False
        return True

    @classmethod
    def is_name(cls, string):
        """Return True if string is alphanumeric plus underscore.

        First character must be a lowercase letter and the rest of the string
        must also only contain lowercase letters, underscores and digits.

        Parameters
        ----------
        string: str

        Returns
        -------
        is_type_name: bool
        """
        is_type_string = cls.is_string(string)
        # Returns false if not composed of alphanumeric characters and _
        if not is_type_string:
            return False
        # Returns false if first character not a letter
        if not string[0].isalpha():
            return False
        # Returns false if any character is not a lowercase letter, _ or digit
        if not string == string.lower():
            return False
        # Passes the tests of being a lowercase string of alphanumeric chars
        # and _
        return True

    @staticmethod
    def is_number(string):
        """Return True if string only contains digits.

        Parameters
        ----------
        string: str

        Returns
        -------
        is_type_number: bool
        """
        if string.isdigit():
            return True
        return False

    @staticmethod
    def is_integer(string):
        """Return True if string only has digits and first one is not 0.

        Parameters
        ----------
        string: str

        Returns
        -------
        is_type_integer: bool
        """
        if string.isdigit() and string[0] != "0":
            return True
        return False

    @classmethod
    def determine_type(cls, string):
        """Determine the type of the symbol.

        Types of symbols:
        - input_pin - Strings defined in input_pins
        - output_pin - Strings defined in output_pins
        - keyword - Strings defined in keywords
        - name - Any string that begins with a letter and contains only
        lowercase letters, underscores and digits
        - string - Any string composed of any combination of alphanumeric
        characters and underscores
        - integer - Any string that contains only digits with the first digit
        being non-zero
        - number - Any string that contains only digits with the first digit
        being zero
        - semi-colon (;)
        - colon (:)
        - comma (,)
        - dot (.)
        - arrow (>)
        - other - Any other string types

        Parameters
        ----------
        string: str

        Returns
        -------
        symbol_type: str
        """
        if string in input_pins:
            return "input_pin"
        elif string in output_pins:
            return "output_pin"
        elif string in keywords:
            return "keyword"
        elif cls.is_number(string):
            if cls.is_integer(string):
                return "integer"
            return "number"
        elif cls.is_string(string):
            if cls.is_name(string):
                return "name"
            return "string"
        elif string in punctuation:
            return punctuation[string]
        return "other"


class Scanner:
    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
