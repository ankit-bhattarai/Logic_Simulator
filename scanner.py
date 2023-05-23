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
single_line_comment = "#"
multi_line_comment = "!"
comment = {single_line_comment, multi_line_comment}


class Symbol:
    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self, string, id, line_number, column_number):
        """Initialise symbol properties."""
        self.id = id
        self.type = self.determine_type(string)
        self.line_number = line_number
        self.column_number = column_number

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
        self.path = path
        self.names = names
        self.list_of_symbols = []
        self.file = None
        self.current_line_number = 1
        self.current_column_number = 1
        self.current_char = None
        self.symbol_counter = -1

    def reset_symbol_counter(self):
        """Reset the symbol counter to -1."""
        self.symbol_counter = -1

    def open_file(self):
        """Open the file."""
        self.file = open(self.path, "r")

    def close_file(self):
        """Close the file."""
        self.file.close()

    def get_next_char(self):
        """Get the next character.

        Along with getting the next character, this method also updates the
        current line and column numbers.

        If the previous character was a new line, the current line number is
        incremented and the current column number is reset to 1.

        Returns
        -------
        character: string
        """
        prev_char = self.current_char
        character = self.file.read(1)
        self.current_column_number += 1
        if prev_char == "\n":  # At the start of a new line
            self.current_line_number += 1
            self.current_column_number = 1
        self.current_char = character
        return character

    def get_next_number(self, first_number):
        """Seek any subsequent numbers in the file after first_number.

        get_symbol() has already found that the first character is a digit.
        This method will find any subsequent digits and return them together
        as a string. The next character after the number must also be returned.

        If this is at the end of the file, the next character will be "".
        Here it should return (first_number, "")

        Parameters
        ----------
        first_number: string
            The first number that was found

        Returns
        -------
        number: string
            The number that was found as a string
        next_character: string
            The next character after the number
        """
        met_numbers = first_number
        while True:
            character = self.get_next_char()
            if character.isdigit():
                # If the character is a digit, add it to the string of numbers
                # previously found before this current character
                met_numbers += character
            else:  # Current character is not a digit
                return (met_numbers, character)  # This works for both end of
            # normal numbers as well as the end of the file

    def get_next_name(self, first_letter):
        """Seek any name characters after first_letter and return them.

        get_symbol() has already found a letter. This method will find any
        subsequent alphanumeric characters and underscores and return them
        along with the  next non-alpha_numeric character

        If this is at the end of the file, the next character will be "".
        Here it should return (first_letter, "")

        Parameters
        ----------
        first_letter: string
            The first letter that was found

        Returns
        -------
        name: string
            The name that was found
        next_character: string
            The next non alpha_numeric or '_' character after the name
        """
        met_name_characters = first_letter
        while True:
            character = self.get_next_char()
            if character.isalnum() or character == "_":
                met_name_characters += character
            else:  # Current character is not an alpha_numeric or '_'
                # character but have encountered them until now
                return (met_name_characters, character)
            # This automatically handles the end of the flie case

    def skip_spaces(self):
        """Skip over spaces and tabs and return the next non-space character.

        Returns
        -------
        character: string
            The next non-space character
        """
        while True:
            character = self.get_next_char()
            if character.isspace():
                continue
            return character

    def skip_comment(self, comment_character):
        """When a comment is detected, skip over the rest of the line.

        Method is called when a comment is detected. For a single line comment
        it  skips over the rest of the line and returns the first character of
        the next line or "" if the end of the file has been reached. For a
        multi-line comment, it skips over all the content until it reaches the
        terminating comment character and returns the first character after it.
        If the end of the file is reached before the terminating comment, it
        will return None.
        For multi-line comment the start and terminating comment characters
        are the same.

        Parameters
        ----------
        comment_character: string
            The character that was detected as the start of a comment

        Returns
        -------
        character: string or None
            The first character after the comment or None if a multi-line
            comment was not terminated before the end of the file
        """
        if comment_character == single_line_comment:  # Single line comment
            while True:
                character = self.get_next_char()
                if character == "\n":  # Reached end of line
                    return self.get_next_char()  # Move to next line
                if character == "":  # Reached end of file
                    return character
                continue
        else:  # Multi-line comment
            while True:
                character = self.get_next_char()
                if character == multi_line_comment:  # Reached end of comment
                    return self.get_next_char()  # Move to next character
                if character == "":  # Reached end of file
                    return None
                continue

    def create_symbol(self, string, column_number, line_number):
        """Create a symbol.

        In the process of creating the symbol, the type of the symbol from its
        string as well as its ID from names is determined.
        The line number of the symbol and the column number of the symbol's
        first character are also determined.

        Parameters
        ----------
        str: str
            The string which will be used to create the symbol.

        Returns
        -------
        symbol: Symbol
            The symbol created from the string.
        """
        symbol_id = self.names.lookup([string])[0]  # Lookup requires a list
        symbol = Symbol(string, symbol_id, line_number, column_number)
        return symbol

    def get_symbols(self):
        """Read the input file and converts them into symbols.

        Most involved function in Scanner. Dynamically determines the methods
        being called and the state of the scanner based on the current
        and any previous characters read.

        It calls methods to get the next name or number based on the first
        character. The appropriate methods then return the name or number plus
        the next character after that!

        It has a continuous loop where it first evaluates the current character
        and then determines how it wants to proceed and read subsequent
        characters based on that.

        Cases are:
        1. Current character is end of file - Finishes the loop
        2. Current character is a digit - Calls get_next_number()
        3. Current character is a letter - Calls get_next_name()
        4. Current character is a space or tab - Calls skip_spaces()
        5. Current character is the start of a comment - Calls skip_comment()
        6. Current character is a non-comment punctuation, must be true when
        none of the above cases are true

        In cases 2, 3, 4, 5 it obtains the next character after either the
        symbol or the whitespace. In case 6, symbols will be made just from the
        current character and as such, the next character needs to be evaluated
        before the loop ends.

        In each case, after a symbol is created, it is added to the list of
        symbols and the loop continues.
        """
        self.open_file()
        self.list_of_symbols = []
        self.line_number = 1
        self.column_number = 1
        character = self.get_next_char()  # Only need to do this at the start
        while True:
            column_number = self.current_column_number
            line_number = self.current_line_number
            if character == "":  # Case 1 - End of file
                break  # Exit loop
            elif character.isdigit():  # Case 2 - Digit
                # Gets the rest of the number and the next character after it
                (number, character) = self.get_next_number(character)
                # Creates the symbol and adds it to the list of symbols
                symbol = self.create_symbol(number, column_number, line_number)
                self.list_of_symbols.append(symbol)
            elif character.isalpha():  # Case 3 - Letter
                # Gets the rest of the name and the next character after it
                column_number = self.current_column_number
                (string, character) = self.get_next_name(character)
                # Creates the symbol and adds it to the list of symbols
                symbol = self.create_symbol(string, column_number, line_number)
                self.list_of_symbols.append(symbol)
            elif character.isspace():  # Case 4 - Space or tab
                character = self.skip_spaces()
            elif character in comment:  # Case 5 - Comment
                character = self.skip_comment(character)
            else:  # Case 6 - Non-comment punctuation
                symbol = self.create_symbol(character, column_number,
                                            line_number)
                self.list_of_symbols.append(symbol)
                character = self.get_next_char()
        self.close_file()

    def verify_file_scanned(self):
        """Verify that the file has been scanned.

        Will scan the file and store the symbols if they have not been scanned

        Returns
        -------
        success:bool
        """
        if self.list_of_symbols == []:
            self.get_symbols()
        return True

    def get_symbol(self):
        """Return the next symbol from the list of symbols.

        Returns
        -------
        symbol: Symbol
            The next symbol from the list of symbols.
        """
        self.verify_file_scanned()
        next_symbol = self.symbol_counter + 1
        if next_symbol < len(self.list_of_symbols):  # Within the file
            self.symbol_counter += 1
            return self.list_of_symbols[self.symbol_counter]
        return None  # End of file

    def get_list_of_symbols(self):
        """Return the list of symbols.

        If the list of symbols is empty, it calls get_symbols() to populate it.

        Returns
        -------
        list_of_symbols: list of Symbol
            The list of symbols created from the input file.
        """
        self.verify_file_scanned()
        return self.list_of_symbols

    def get_line(self, line_number):
        """Read a line from the input file and return it.

        Parameters
        ----------
        line_number: int
            The line number of the line to be read from the file.

        Returns
        -------
        interested_line: str
            The specified line read from the file.
        """
        self.open_file()
        interested_line = self.file.readlines()[line_number - 1]
        self.close_file()
        return interested_line

    def print_error(self, symbol, index_of_arrow, message):
        """Print an error message as well as the line where the error occured.

        Prints an error message along with the line in the definition file
        where the error occured and an arrow pointing to the exact location

        Parameters
        ----------
        symbol: Symbol
            The symbol where the error occured
        index_of_arrow: int
            The index of the exact error in the line from the start of symbol's
            first character
        message: str
            The error message to be printed

        Returns
        -------
        success: bool
            Returns True if able to successfully print the error message
        """
        try:
            line_number = symbol.line_number
            line_string = self.get_line(line_number)
            column_number = symbol.column_number
            position_of_arrow = column_number + index_of_arrow
            arrow_string = " " * (position_of_arrow - 1) + "^"
            print(message)
            print(line_string.rstrip())  # Remove trailing newline from end
            print(arrow_string)
            return True
        except Exception:
            return False
