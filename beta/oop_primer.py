# Create function that returns the average of an integer list
def average_numbers(num_list): 
    avg = sum(num_list)/float(len(num_list)) # divide by length of list
    return avg

# Take the average of a list: my_avg
my_avg = average_numbers([1, 2, 3, 4, 5, 6])

# Print out my_avg
print(my_avg)


# Create class: DataShell
class DataShell:

    # Declare a class variable family, and assign value of "DataShell"
    family = "DataShell"
    
    # Initialize class with self, identifier and data arguments
    def __init__(self, identifier, data):
      
    		# Set identifier and data as instance variables,
        # assigning value of input arguments
        self.identifier = identifier
        self.data = data

# Declare variable x with value of 100, and y with list of integers from 1 to 5
x = 100
y = [1, 2, 3, 4, 5]

# Instantiate DataShell passing x and y as arguments: my_data_shell
my_data_shell = DataShell(x, y)

# Print my_data_shell.identifier
print(my_data_shell.family)
print(my_data_shell.identifier)
print(my_data_shell.data)

# Override the my_data_shell.family value with "NotDataShell"
my_data_shell.family = "NotDataShell"

# Print my_data_shell class variable family once again
print(my_data_shell.family)