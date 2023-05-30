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
terminate_name_scan_characters = {";", ":", ",", ".", ""}
punctuation = {";": "semi-colon", ":": "colon", ",": "comma", ".": "dot",
               ">": "arrow"}
single_line_comment = "#"
multi_line_comment = "!"
comment = {single_line_comment, multi_line_comment}


class Symbol:
    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    string: The string that the symbol represents.
    id: The id of the symbol.
    line_number: The line number of the symbol.
    column_number: The column number of the symbol.

    Public methods
    --------------
    is_string(string): Return True if string is alphanumeric plus underscore.

    is_name(cls, string): Return True if string is lowercase alphanumeric plus
                     underscore and starts with a lowercase letter.

    index_not_name(cls, string): Return the index of the first character in
                                 the string that violates the name rules.

    is_number(cls, string): Return True if string only has digits.

    is_integet(string): Return True if string only has digits and starts with
                        a non-zero digit.

    determine_type(cls, string): Return the type of the string.
    """

    def __init__(self, string, id, line_number, column_number):
        """Initialise symbol properties.

        Parameters
        ----------
        string: str
            The string that the symbol represents.
        id: int
            The id of the symbol.
        line_number: int
            The line number of the symbol.
        column_number: int
            The column number of the symbol.
        """
        self.id = id
        self.type = self.determine_type(string)
        self.line_number = line_number
        self.column_number = column_number

    def __eq__(self, other):
        """Return True if symbols are equal."""
        if self.id != other.id:
            return False
        if self.type != other.type:
            return False
        if self.line_number != other.line_number:
            return False
        if self.column_number != other.column_number:
            return False
        return True

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
        """Return True if string is lowercase alphanumeric plus underscore.

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

    @classmethod
    def index_not_name(cls, string):
        """Return index of first character that violates name rules.

        Iterate through string and return the index of the first character that
        doesn't satisfy the rules for a name. If all characters satisfy the
        rules, return None.

        It also returns a code to indicate the type of error:
        - 1: First character is not a lowercase letter
        - 2: Specific character is not a letter, digit or underscore
        - 3: Specific character is not lowercase
        - None: No errors

        Parameters
        ----------
        string: str

        Returns
        -------
        error_loc_and_code: tuple of Int or None
            If no errors, returns None. Otherwise, returns a tuple of integers
            with first element being the index of the first character that
            violates the rules and the second element consisting of the error
            code.

        Examples
        --------
        >>> Symbol.index_not_name("a")
        >>> Symbol.index_not_name("a1")
        >>> Symbol.index_not_name("a_1")
        >>> Symbol.index_not_name("1a")
        (0, 1)
        >>> Symbol.index_not_name("_a")
        (0, 1)
        >>> Symbol.index_not_name("aA")
        (1, 3)
        >>> Symbol.index_not_name("a1A")
        (2, 3)
        >>> Symbol.index_not_name("a_1AB") # Only first error is returned
        (3, 3)
        >>> Symbol.index_not_name("a!a")
        (1, 2)
        >>> Symbol.index_not_name("a1+a")
        (2, 2)
        """
        # First character must be a lowercase letter
        # If either of the conditions in the or statement are true, return 0
        if (not string[0].isalpha()) or (not string[0] == string[0].lower()):
            return (0, 1)
        for i, char in enumerate(string[1:], 1):
            # Subsequent characters must be lowercase letters, digits or _
            if not char.isalnum() and char != "_":
                return (i, 2)
            # Must be lowercase
            if not char == char.lower():
                return (i, 3)
        return None

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

    reset_symbol_counter(self): Resets the symbol counter to -1.

    open_file(self): Opens the file.

    close_file(self): Closes the file.

    get_next_char(self): Gets the next character from the file.

    get_next_number(self, first_number): When a digit character is encountered,
                                        this method is called to get the
                                        entire number from the file.

    get_next_name(self, first_letter): When a letter character is encountered,
                                        this method is called to get the entire
                                        name from the file.

    skip_spaces(self): Skips over spaces, tabs and returns the next non-space
                        character.

    skip_comments(self, comment_character): Skips over comments and returns
                                            the next non-comment character.

    create_symbol(self, string, line_number,
                  column_number): Creates a symbol object from the given
                                  quantities and returns it.

    get_symbols(self): Gets all the symbols from the file and stores them in
                        the object's list_of_symbols attribute.

    verify_file_scanned(self): Verifies that the entire file has been scanned,
                                scanning it if it hasn't.

    get_symbol(self): Returns the next symbol from the list_of_symbols.

    get_list_of_symbols(self): Returns the list_of_symbols.

    get_line(self, line_number): Reads the specified line from the file and
                                returns it.

    print_error(self, symbol, index_of_arrow,
                message): Gets the appropriate line from the file and either
                            prints the error message to the console or adds it
                            to the error_messages attribute to be shown in the
                            GUI.

    get_error_messages(self): Returns the error_messages attribute.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        self.path = path
        self.names = names
        self.list_of_symbols = []
        self.file = None
        self.current_line_number = 1
        self.current_column_number = 0
        self.current_char = None
        self.symbol_counter = -1
        self.error_messages = ""
        self.print_to_gui = False
        self.get_symbols()

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
        """Seek any characters after first_letter and return them.

        get_symbol() has already found a letter. This method will find any
        subsequent characters that aren't whitespace or these characters:
        - semi-colon (;)
        - colon (:)
        - comma (,)
        - dot (.)
        and return them together as a string. The next character after the
        name will also be returned. The above characters are stored in
        terminate_name_scan_characters.

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
            The next non-white space or non (semi-colon, colon, comma, dot)
            character after the name
        """
        met_name_characters = first_letter
        while True:
            character = self.get_next_char()
            if character.isspace() or character in terminate_name_scan_characters:
                return (met_name_characters, character)
            else:
                # Current character is not a space or a terminating character
                met_name_characters += character

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
        self.current_line_number = 1
        self.current_column_number = 0
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
        self.reset_symbol_counter()
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
        where the error occured and an arrow pointing to the exact location.
        If print_to_gui is True, it will store all the error messages in a
        string from the parser and return it to the GUIInterface when needed.

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
            line_number_string = "Line " + str(line_number) + ": "
            position_of_arrow = len(line_number_string) + \
                column_number + index_of_arrow

            arrow_string = " " * (position_of_arrow - 1) + "^"
            if not self.print_to_gui:
                print(message)
                # Remove trailing newline from end
                print(line_number_string + line_string.rstrip())
                print(arrow_string)
            else:  # Printing to the gui, just store error messages
                self.error_messages += message + "\n"
                self.error_messages += line_number_string
                self.error_messages += line_string.rstrip() + "\n"
                self.error_messages += arrow_string + "\n"
            return True
        except Exception:
            return False

    def get_error_messages(self):
        """Return the error messages to the GUIInterface.

        Returns
        -------
        error_messages: str
            The error messages from the parser
        """
        return self.error_messages
