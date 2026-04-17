
#Slice the inputs for formatting
def evaluator(data):
    item =[]
    symbol = ['+', '-', '*', '/', '(', ')']
    p = 0
    while p< len(data):
        if data[p].isspace():
            p+=1
        elif data[p].isdigit() or data[p] == '.':
            number = ''
            while p < len(data) and (data[p].isdigit() or data[p] =='.'):
                number += data[p]
                p+=1
            item.append(number)
        elif data[p] in symbol:
            item.append(data[p])
            p+=1
        else:
            return None 
    return item 

#Formats and labels characters
def format(item):
    symbol = ['+', '-', '*', '/', '(', ')']
    if item is None: return 'ERROR'
    result = []
    for check in item:
        if check in symbol:
            if check =='(':
                result.append('[LPAREN:(]')
            elif check ==')':
                result.append('[RPAREN:)]')
            else:
                result.append(f"[OP:{check}]")
        else:
            result.append(f'[NUM{check}]')
    result.append('[END]')
    return' '.join(result)

#Looking forward to what comes next for planning
def look(item, position):
    if item is None or position[0] >= len(item):
        return None 
    return item[position[0]]

#take positon and move forward for use
def grab(item, position):
    character = item[position[0]]
    position[0]+=1
    return character

#look for parentheses, and positive/negative signs infrom of numbers 
def unary(item, position):
    value = look(item, position)
    if value is None:
        return 'ERROR'
    if value == '+':
        return 'ERROR'
    if value.replace('.', '', 1).isdigit():
        return ('num', float(grab(item,position)))
    if value == '-':
        grab(item, position)
        post_value = unary(item, position)
        if post_value == 'ERROR':
            return 'ERROR'
        else:
            return('neg', post_value)    
    if value =='(':
        grab(item, position)
        solve = add_sub(item, position)
        if look(item, position) ==')':
            grab(item,position)
            return solve
        return 'ERROR'
    return 'ERROR'

#Multiplications and division
def mult_div(item, position):
    pre_value = unary(item, position)
    if pre_value == 'ERROR':
        return 'ERROR'
    while True:
        value = look(item, position)
        if value in ('*', '/'):
            operation = grab(item, position)
            post_value = unary(item, position)
            if post_value=='ERROR':
                return 'ERROR'
            pre_value = (operation,pre_value,post_value)
        elif value is not None and (value =='(' or value.replace('.', '', 1).isdigit()):
            operation = '*'
            post_value = unary(item,position)
            if post_value =='ERROR':
                return 'ERROR'
            pre_value = (operation,pre_value,post_value)
        else:
            break 
    return pre_value 

#Perform Adding and Subtracting after Multiplication and division
def add_sub(item, position):
    pre_value = mult_div(item, position)
    if pre_value == "ERROR":
        return 'ERROR'
    while True:
        value = look(item, position)
        if value in ('+', '-'):
            operation = grab(item, position)
            post_value = mult_div(item, position)
            if post_value =='ERROR':
                return 'ERROR'
            pre_value = (operation,pre_value,post_value)
        else:
            break 
    return pre_value 

#Layout calcualtion format
def tree_string(branch):
    if branch == 'ERROR' or branch is None:
        return 'ERROR'
    if branch[0] == 'num':
        value = branch[1]
        return str(int(value)) if float(value).is_integer() else str(value) 
    if branch[0] =='neg':
        return f'(neg{tree_string(branch[1])})'
    operation, pre_branch, post_branch = branch[0], branch[1], branch[2]
    return f"({ operation} {tree_string(pre_branch)} {tree_string(post_branch)}"

#Performs calculations
def tree_calc(branch):
    if branch == 'ERROR':
        return 'ERROR'
    if branch[0] == 'num':
        return  branch[1]
    if branch[0] == 'neg':
        value = tree_calc(branch[1])
        return -value if value != "ERROR" else "ERROR"
    operation, pre_branch, post_branch = branch[0], branch[1], branch[2]
    pre_value = tree_calc(pre_branch)
    post_value = tree_calc(post_branch)
    if pre_value == 'ERROR' or post_value == 'ERROR':
        return 'ERROR'
    if operation =='+': 
        return pre_value + post_value
    if operation =='-': 
        return pre_value - post_value
    if operation =='*': 
        return pre_value * post_value
    if operation == '/':
        if post_value == 0:
            return 'ERROR'
        else:
            return pre_value / post_value

#Procesing
def process(lines):
    item = evaluator(lines)
    if item is None:
        return 'ERROR', 'ERROR', 'ERROR'
    token = format(item) 
    position = [0]
    tree = add_sub(item, position)
    if tree == 'ERROR' or position[0] < len(item):
        return 'ERROR', token, 'ERROR'
    branch_string = tree_string(tree)
    result = tree_calc(tree)
    if result != 'ERROR':
        res_float = float(result)
        if res_float.is_integer():
            result = int(res_float) 
        else:
            result = round(res_float, 4) 
    if branch_string == 'ERROR':
        return 'ERROR', token, 'ERROR'
    return branch_string, token, result

#read inputs and write output
def evaluator_file(input_path):
    output = []
    with open(input_path, 'r') as f, open('output.txt', 'w') as f_output:
        for lines in f:
            line = lines.strip()
            if not line: 
                continue 
            tree, tokens, result = process(line)
            input= {'input': line, 'tree': tree, 'tokens': tokens, 'result': result }
            output.append(input)

            f_output.write(f'input: {line} \ntree: {tree} \ntokens: {tokens} \nresult: {result}\n\n')
    return output
if __name__ == '__main__':
    evaluator_file('sample_input.txt')