"""Map variable names and string names to unique integers.

Used in the Logic Simulator project. Most of the modules in the project
use this module either directly or indirectly.

Classes
-------
Names - maps variable names and string names to unique integers.
"""


class Names:
    """Map variable names and string names to unique integers.

    This class deals with storing grammatical keywords and user-defined words,
    and their corresponding name IDs, which are internal indexing integers. It
    provides functions for looking up either the name ID or the name string.
    It also keeps track of the number of error codes defined by other classes,
    and allocates new, unique error codes on demand.

    Parameters
    ----------
    No parameters.

    Public methods
    -------------
    unique_error_codes(self, num_error_codes): Returns a list of unique integer
                                               error codes.

    query(self, name_string): Returns the corresponding name ID for the
                        name string. Returns None if the string is not present.

    lookup(self, name_string_list): Returns a list of name IDs for each
                        name string. Adds a name if not already present.

    get_name_string(self, name_id): Returns the corresponding name string for
                        the name ID. Returns None if the ID is not present.
    """

    def __init__(self):
        """Initialise names list."""
        self.error_code_count = 0  # how many error codes have been declared
        self.names_list = []

    def unique_error_codes(self, num_error_codes):
        """Return a list of unique integer error codes."""
        if not isinstance(num_error_codes, int):
            raise TypeError("Expected num_error_codes to be an integer.")
        self.error_code_count += num_error_codes
        return range(self.error_code_count - num_error_codes,
                     self.error_code_count)

    def query(self, name_string):
        """Return the corresponding name ID for name_string.

        If the name string is not present in names_list, return None.

        Parameters
        ----------
        name_string: str

        Returns
        -------
        index: int or None
            Returns an integer if name ID present otherwise None
        """
        if name_string in self.names_list:
            return self.names_list.index(name_string)
        return None

    def lookup(self, name_string_list):
        """Return a list of name IDs for each name string in name_string_list.

        If the name string is not present in the names list, add it.

        Parameters
        ----------
        name_string_list: list of str
            List of strings whose IDs need to be looked up

        Returns
        -------
        name_ids: list of int
            List of integer indexes of the names in name_string_list
        """
        name_ids = []
        for name_string in name_string_list:
            id = self.query(name_string)
            if id is None:
                self.names_list.append(name_string)
                # Added to end of list so index is length minus 1
                id = len(self.names_list) - 1
            name_ids.append(id)
        return name_ids

    def get_name_string(self, name_id):
        """Return the corresponding name string for name_id.

        If the name_id is not an index in the names list, return None.

        Parameters
        ----------
        name_id: int
            Integer index of the name string in the names list.
        Returns
        -------
        name_string: str or None
            Returns a string if name ID is a valid index otherwise None
        """
        if 0 <= name_id < len(self.names_list):
            return self.names_list[name_id]
        return None
