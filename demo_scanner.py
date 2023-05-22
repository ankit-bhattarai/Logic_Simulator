"""File contains a demonstration of how the scanner can be used."""
from names import Names
from scanner import Scanner

names_1 = Names()
scanner_1 = Scanner("def1.txt", names_1)

names_2 = Names()
scanner_2 = Scanner("def2.txt", names_2)

list_of_symbols_1 = scanner_1.get_list_of_symbols()
list_of_symbols_2 = scanner_2.get_list_of_symbols()

print("Contents of def1.txt")
for symbol in list_of_symbols_1:
    id = symbol.id
    name = names_1.get_name_string(id)
    if name == "CONNECT" or name == "MONITOR" or name == "END":
        print()
    print(name, end=" ")
print()

print("Contents of def2.txt")
for symbol in list_of_symbols_2:
    id = symbol.id
    name = names_2.get_name_string(id)
    if name == "CONNECT" or name == "MONITOR" or name == "Q":
        print()
    print(name, end=" ")
print()

# Let's check the error printing capability of the scanner

second_last_symbol = list_of_symbols_2[-2]
scanner_2.print_error(second_last_symbol, index_of_arrow=0,
                      message="Error message should point at E")
scanner_2.print_error(second_last_symbol, index_of_arrow=1,
                      message="Error message should point at N")
scanner_2.print_error(second_last_symbol, index_of_arrow=2,
                      message="Error message should point at D")
