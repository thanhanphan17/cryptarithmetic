import sys
import itertools
import os

found_solution = False

def get_outer_parentheses_content(expression):
    # Function to extract all expressions within outermost parentheses and return as a list
    # Example input string: -(MONEY-(SEND+MORE))+SEND+MORE+(OR-DIE)=NUOYI
    # Returns a list: [MONEY-(SEND+MORE), OR-DIE]
    content = []
    stack = []
    start = None

    for i, char in enumerate(expression):
        if char == "(":
            if not stack:
                start = i + 1
            stack.append(char)
        elif char == ")":
            stack.pop()
            if not stack:
                content.append(expression[start:i])

    return content

def swap_operator(expression):
    # Function to swap '-' with '+' and '+' with '-'
    placeholder = "@@"
    expression = expression.replace("-", placeholder)
    expression = expression.replace("+", "-")
    expression = expression.replace(placeholder, "+")
    return expression

def compress_expression(expression):
    # Function to compress operators
    expression = expression.replace("--", "+")
    expression = expression.replace("+-", "-")
    expression = expression.replace("-+", "-")
    expression = expression.replace("++", "+")
    return expression

def process_string(expression):
    # Function to process the string for level 3
    # The function converts level 3 problems to level 2 by moving parentheses-contained expressions to the beginning and processing them first.
    # Example: AB+(BC-CD)=ACD
    # The function will return BC-CD+AB=ACD

    if expression is None:  # If there are no more parentheses, the function terminates
        return expression

    # Get all strings within parentheses
    parentheses_content = get_outer_parentheses_content(expression)

    # Preprocess each parentheses-contained expression
    for i in range(len(parentheses_content)):
        # Check the sign at the beginning of the string, if none, add '+'
        if parentheses_content[i] != "-":
            parentheses_content[i] = "+" + parentheses_content[i]

        # Add '+' before '(' to avoid array index issues
        parentheses_content[i] = parentheses_content[i].replace("(", "+(")

        # Compress the operators
        parentheses_content[i] = compress_expression(parentheses_content[i])

    # Process each parentheses-contained expression recursively until no more parentheses remain
    for i in range(len(parentheses_content)):
        start = expression.find("(")  # Find the position of the first '(' in the string
        length = len(parentheses_content[i])  # Get the length of the inner expression within parentheses
        inner_expression = parentheses_content[i]

        # Recursively process each inner expression to remove parentheses until there are no more
        inner_expression = process_string(inner_expression)

        # If there was a '-' before the parentheses, swap the sign of all elements in the expression
        if expression[start - 1] == "-":
            inner_expression = swap_operator(inner_expression)
            inner_expression = compress_expression(inner_expression)

        # Replace the original expression with the processed inner expression
        expression = inner_expression + "+" + expression[: start - 1] + expression[start + length + 1 :]
        expression = compress_expression(expression)

    return expression

def analy_string(input_str):
    # Main function to analyze the input string and solve the cryptarithmetic puzzle
    expression = process_string(input_str)
    if expression[0] == "+":
        expression = expression[1:]
    operands = list()
    operators = list()
    operators.append("+")
    num = [True for i in range(10)]
    alphab = {}
    alphab["."] = 0
    temp = ""
    result = ""
    maxsize = 0
    type = 1

    for i in range(len(expression)):
        if "A" <= expression[i] <= "Z":
            if expression[i] not in alphab:
                alphab[expression[i]] = -1
            if type == 1:
                temp = temp + expression[i]
            else:
                result = result + expression[i]
        else:
            if expression[i] == "+" or expression[i] == "-":
                operands.append(temp)
                if len(temp) > maxsize:
                    maxsize = len(temp)
                temp = ""
                operators.append(expression[i])
            else:
                operands.append(temp)
                if len(temp) > maxsize:
                    maxsize = len(temp)
                type = 2
    if maxsize < len(result):
        maxsize = len(result)
    n = len(operands)
    matrix = [["." for _ in range(maxsize)] for _ in range(len(operands) + 1)]
    for i in range(n):
        k = len(operands[i]) - 1
        for j in range(maxsize - 1, -1, -1):
            if k != -1:
                matrix[i][j] = operands[i][k]
                k = k - 1
            else:
                break

    alphab = dict(sorted(alphab.items()))
    for i in range(maxsize):
        matrix[n][i] = result[i]
    checkcolumn(0, matrix, 0, alphab, operators, n, num)
    showresult(0, None)

def checkcolumn(col, matrix, debt, alphab, operators, n, num):
    global found_solution
    if found_solution == True:
        return

    # Recursive function to check each column of the matrix for possible solutions
    if col == len(matrix[0]):
        showresult(1, alphab)
        found_solution = True
        return

    num_operands = 0
    con = []
    unknow_al = []
    al_copy = {}
    for i in range(n):
        oper = 1
        if operators[i] == "-":
            oper = -1
        if "A" <= matrix[i][col] <= "Z":
            num_operands += 1

            # Check whether the letter needs to start with a non-zero digit
            if col == 0 or matrix[i][col - 1] == ".":
                con.append(matrix[i][col])

            if matrix[i][col] in al_copy:
                al_copy[matrix[i][col]] = al_copy[matrix[i][col]] + oper
            else:
                al_copy[matrix[i][col]] = oper
            if alphab[matrix[i][col]] == -1 and matrix[i][col] not in unknow_al:
                unknow_al.append(matrix[i][col])
            if matrix[i][col] in unknow_al and al_copy[matrix[i][col]] == 0:
                unknow_al.remove(matrix[i][col])
    al_copy = dict(sorted(al_copy.items()))

    # If the column contains only the result character, it must be generated by the operation in the next column
    if num_operands == 0:
        index = 1
        while index < n:
            alphab[matrix[n][col]] = index
            num[index] = False
            checkcolumn(col + 1, matrix, -index, alphab, operators, n, num)
            num[index] = True
            index += 1
        return

    res = matrix[n][col]
    if col == 0 or matrix[n][col - 1] == ".":
        con.append(res)
    if alphab[res] == -1 and res not in unknow_al:
        unknow_al.append(res)

    # Perform loop and backtracking here

    # unknow_al: List of characters that need to be assigned numbers
    # num: List of available digits
    # al_copy: Dictionary of characters present in the current column's operation
    # res: Result character (may appear in unknow_al)
    # debt: Debt from the previous operation, will turn the result into 10*debt+res

    # Mapping between unknow_al and num to find suitable combinations of characters and numbers
    unique_digits = set(range(10))
    available_digits = [digit for digit, can_assign in zip(unique_digits, num) if can_assign]

    mappings = []
    for permutation in itertools.permutations(available_digits, len(unknow_al)):
        mapping = dict(zip(unknow_al, permutation))
        if all(mapping[char] == digit for char, digit in zip(unknow_al, permutation) if digit):
            # If a valid mapping is found, check whether the operation is correct or not
            # The check function will return:
            # 0: If the operation is correct, proceed to the next column
            # Negative number: If the operation is incorrect but can be fixed by carrying 1 from the next column (e.g., 8=9? => 8+1=9)
            # Positive number: If the operation is incorrect but can be fixed by borrowing 1 from the next column (e.g., 9=8 => 9-1=8 => 9=8+1)
            # None: If there is no possible solution
            flag = True
            for c in con:
                if c in unknow_al and mapping[c] == 0:
                    flag = False
                    break
            if not flag:
                continue
            alphab, num = add_to_check(alphab, mapping, num)
            check_goal = check(alphab, al_copy, res, debt, n)
            if check_goal is None or (check_goal != 0 and col == len(matrix[0]) - 1):
                alphab, num = remove(alphab, mapping, num)
                continue
            else:
                checkcolumn(col + 1, matrix, check_goal, alphab, operators, n, num)
                alphab, num = remove(alphab, mapping, num)

def add_to_check(alphab, mapping, num):
    # Function to add the temporary mapping to the main mapping and update the num list
    for c in mapping:
        alphab[c] = mapping[c]
        num[mapping[c]] = False
    return alphab, num

def remove(alphab, mapping, num):
    # Function to remove the temporary mapping from the main mapping and update the num list
    for c in mapping:
        alphab[c] = -1
        num[mapping[c]] = True
    return alphab, num

def check(alphab, al_copy, res, debt, n):
    # Function to check if the current operation is valid
    result = 0
    math = 0
    for c in al_copy:
        math = math + al_copy[c] * alphab[c]
    result = alphab[res]
    if debt >= 0:
        math = math + 10 * debt
    else:
        result = result + 10 * (-debt)
    if math == result:
        return 0

    # If the operation is only a bit smaller than the desired result and the number is <= n-1
    if 0 < result - math < n:
        return -(result - math)

    # If the operation is only a bit larger than the desired result and the number is <= n-1
    if 0 < math - result < n:
        return math - result

    return None


current_script_path = os.path.abspath(__file__)
# Extract the directory from the script path
current_folder = os.path.dirname(current_script_path)

input_file = current_folder + "\\testcases\\input\\input3.txt"
output_file = current_folder + "\\testcases\\output\\output3.txt"

def showresult(t, res):
    # Function to write the result to an output file
    global output_file
    file_name = output_file
    try:
        with open(file_name, "a") as file:
            if t == 0:  # If no solution is found
                file.write("NO SOLUTION")
            else:
                for c in res:
                    if c != ".":
                        file.write(c)
                file.write("=")
                for c in res:
                    if c != ".":
                        num = str(res[c])
                        file.write(num)

                file.write("\n")

    except IOError:
        print("An error occurred while writing to the file.")

file_name = input_file
try:
    with open(file_name, "r") as file:

        for line in file:
            string_input = line.strip()
            print(string_input)
            found_solution = False
            analy_string(string_input)

except FileNotFoundError:
    print("File not found. Please check the file path.")
except IOError:
    print("An error occurred while reading the file.")
