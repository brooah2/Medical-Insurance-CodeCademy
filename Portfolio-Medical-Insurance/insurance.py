import csv
import datetime
from re import compile
import os

insurance = []
session_log = []

# SCHEMA insurance.csv: age,sex,bmi,children,smoker,region,charges
# SCHEMA log.csv: date,fields,results

# Main runs the function and allows the user to Search the data, access the Log, or Quit the program
def main():
    # Open CSV file to be searched
    with open('insurance.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
            row = to_numbers(row)
            insurance.append(row)
    
    # Create list of keys
    keys = insurance[0].keys()

    # Program functionality
    requests = 0
    while True:
        greet(requests)
        prompt = input("Instructions: ")
        requests += 1
        if prompt == "Search":
            requests += 1
            search(keys)

        elif prompt == "Log":
            requests += 1
            get_log()

        elif prompt == "Quit":
            os.system('clear')
            break

        else:
            os.system('clear')
            greet(requests)
    
    return


# Function to determine what greeting to give the user
def greet(requests):
    welcome = "Welcome to Insurance.\n"
    instruction = """To search for new data, enter the command "Search".\nTo access the log, enter the command "Log".\nTo quit this program, enter the command "Quit"\n"""
    if requests == 0:
        print(welcome)
        print(instruction)
    else:
        print(instruction)
        
    return


# Function to convert CSV values into floats and ints
def to_numbers(row):
    for key, value in row.items():
        l = len(value.split('.'))
        if l == 1:
            if value.isdigit():
                row[key] = int(value)
        elif l == 2:
            row[key] = float(value)

    return row


# Log function that uses a separate CSV and a list to log any requests
def log(fields, result):
    time = datetime.datetime.now()
    log_date = time.strftime("%Y") + "-" + time.strftime("%m") + "-" + time.strftime("%d")
    log_time = time.strftime("%H") + ":" + time.strftime("%M") + ":" + time.strftime("%S")
    
    # Add to CSV file
    with open('log.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([log_date, fields, result])
    
    # Add to today's log
    session_log.append({log_time: [fields, result]})

    return


# Function to retrieve the log either from today or from a previous date
def get_log():
    # Format year, month, day
    # Format hour, minute, second
    while True:
        print("""Enter the date you would like to access the log for.\nTo access this session's log, enter the command "Session".\nTo return to the previous prompt, enter the command "Back".\n""")
        prompt = input("Instructions: ")

        pattern = compile(r'^\d{4}-\d{2}-\d{2}$')

        if prompt == "Back":
            return

        elif prompt == "Session":
            n = 0
            for item in session_log:
                n += 1
                print(item)
            if n == 0:
                print("No items are available for today.")

            break

        elif pattern.match(prompt):
            matches = []
            with open('log.csv') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["date"] == prompt:
                        matches.append(row)
            for match in matches:
                print(match)

        else:
            print("Invalid format. Please use the date format YYYY-MM-DD.\n")

    return


# Search function to equip user to run searches in console
def search(keys):
    os.system('clear')

    keys_str = ''
    for key in keys:
        keys_str = keys_str + key + ', '
    keys_str.strip(', ')

    print("Please input the field(s) you would like the relevant statistics for.\n")
    print("Keys: " + keys_str)
    prompt = input("Field(s): ")
    if prompt == "Back":
        return

    fields = prompt.split(",")
    for i in range(0, len(fields)):
        fields[i] = fields[i].strip().lower()

    if len(fields) == 0:
        print("""Please provide one or more fields to search, or enter the command "Back" to go back.\n""")

    elif len(fields) == 1:
        fields = fields[0]
        single_search(fields)

    elif len(fields) == 2:
        double_search(fields)

    else:
        print("Please provide no more than two quantitative fields or one qualitative field.")

    return


# Function that takes a trait as an input and returns vital statistics; qualitatively returns 
def single_search(field):
    results = {}
    
    if type(insurance[0][field]) in [float, int]:
        # Quantitatives statistics
        results = {"field": field, "value": None, "total": 0, "count": 0, "average": 0}
        for item in insurance:
            results["total"] += item[field]
            results["count"] += 1
        results["average"] = round(results["total"] / results["count"], 2)

        # Print Results
        message = "The average {0} in this data set of {1} entries is {2}.".format(field, results["count"], results["average"])
        print(message)
    
    else:
        # Qualitatives statistics
        keys = []
        proportions = {}
        for item in insurance:
            n += 1
            if item[field] in keys:
                results[item[field]]["count"] += 1
            else:
                keys.append(item[field])
                results[item[field]] = {"field": field, "value": item[field], "proportion": 0.0, "count": 1}

        for key in keys:
            results[key]["proportion"] = round(results[key]["count"] / n, 4) * 100
            
            # Print Results
            message = "The total number of people whose {0} value is {1} in this data set of {2} entries is {3}, or {4}%.".format(field, key, n, results[key], results[key]["proportion"])
            print(message)
        
    # Store in Log
    log(field, results)

    return results


# Function that takes two traits and returns relevant comparison data
def double_search(fields):
    results = [] # List of calculations
    single_results = []  # List of dictionaries resulting from single_search of each
    qual_message = "Please use two quantitative fields for comparison between two fields; any field can be used for single-field analysis."

    # Individual data
    for i in [0, 1]:
        single_results.append(single_search(fields[i]))
        print("--")
    
    # Identify quantitative vs. qualitative data type for each
    if type(insurance[0][fields[0]]) in [float, int]:
        if type(insurance[0][fields[1]]) in [float, int]:
            # Quantitative and Quantitative -- both dicts in results[] are one-dimensional
            proportion1 = single_results[0]["total"] / single_results[1]["total"]
            proportion2 = single_results[1]["total"] / single_results[0]["total"]

            message = """The proportion of {0} to {1} in this set is {2}.\nThe proportion of {1} to {0} in this set is {3}.""".format(single_results[0]["field"], single_results[1]["field"], proportion1, proportion2)
            print(message + "\n--")
            
            results.append([single_results[0]["field"], single_results[1]["field"], {"0:1":proportion1, "1:0":proportion2}])
        else:
            print(qual_message)
    else:
        print(qual_message)

    # Can be expanded to acommodate more direct comparisons between qualitative sources, but without use of SQL this becomes particularly onerous.

    # Store in Log
    log(fields, results)
    return


main()