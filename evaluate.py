def tokenise(data):
    item = []
    valid_symbols = ["+", "-", "*", "/", "(", ")"]
    a = 0
    while a < len(data):
        if data[a].isspace():
            a += 1
        elif data[a].isdigit() or data[a] == '.':
            k = a
            while k < len(data) and (data[k].isdigit() or data[k] == '.'):
                k += 1
            item.append(data[a:k]) 
            a = k                
        elif data[a] in valid_symbols:
            item.append(data[a])
            a += 1
        else:
            # If we find an invalid character, return None to signal an error
            return None
    return item

def format_tokens(item):
    if item is None: return "ERROR"
    lookup = {'+': 'OP:+', '-': 'OP:-', '*': 'OP:*', '/': 'OP:/', '(': 'LPAREN:(', ')': 'RPAREN:)'}
    results = []
    for t in item:
        if t in lookup:
            results.append(f"[{lookup[t]}]")
        else:
            results.append(f"[NUM:{t}]")
    results.append("[END]")
    return " ".join(results)

def current(item, position):
    if item is None or position[0] >= len(item):
        return None
    return item[position[0]]

def consume(item, position):
    token = item[position[0]]
    position[0] += 1
    return token

def unary(item, position):
    char = current(item, position)
    if char == '-':
        consume(item, position)
        res = unary(item, position)
        return ('neg', res) if res != "ERROR" else "ERROR"
    if char == '+':
        consume(item, position)
        return unary(item, position)
    if char == '(':
        consume(item, position)
        node = add_sub(item, position)
        if current(item, position) == ')':
            consume(item, position)
            return node
        return "ERROR"
    
    val = current(item, position)
    if val is None: return "ERROR"
    consume(item, position)
    return ('num', float(val))

def mult_div(item, position):
    left = unary(item, position)
    if left == "ERROR": return "ERROR"
    
    while current(item, position) in ('*', '/'):
        op = consume(item, position)
        right = unary(item, position)
        if right == "ERROR": return "ERROR"
        left = (op, left, right)
    return left

def add_sub(item, position):
    left = mult_div(item, position)
    if left == "ERROR": return "ERROR"
    
    while current(item, position) in ('+', '-'):
        op = consume(item, position)
        right = mult_div(item, position)
        if right == "ERROR": return "ERROR"
        left = (op, left, right)
    return left

def tree_to_string(node):
    if node == "ERROR": return "ERROR"
    if node[0] == 'num':
        val = node[1]
        return str(int(val)) if val.is_integer() else str(val)
    if node[0] == 'neg':
        return f"(neg {tree_to_string(node[1])})"
    return f"({node[0]} {tree_to_string(node[1])} {tree_to_string(node[2])})"

def evaluate_tree(node):
    if node == "ERROR": return "ERROR"
    if node[0] == 'num': return node[1]
    
    if node[0] == 'neg':
        val = evaluate_tree(node[1])
        return -val if val != "ERROR" else "ERROR"
        
    op, l_n, r_n = node[0], node[1], node[2]
    l, r = evaluate_tree(l_n), evaluate_tree(r_n)
    
    if l == "ERROR" or r == "ERROR": return "ERROR"
    
    if op == '+': return l + r
    if op == '-': return l - r
    if op == '*': return l * r
    if op == '/':
        if r == 0: return "ERROR"
        return l / r

def process_line(line):
    tokens = tokenise(line)
    token_str = format_tokens(tokens)
    
    if tokens is None:
        return "ERROR", "ERROR", "ERROR"
    
    pos = [0]
    tree = add_sub(tokens, pos)
    
    # Check if we finished the whole list of tokens
    if pos[0] < len(tokens): 
        tree = "ERROR"
        
    tree_str = tree_to_string(tree)
    val = evaluate_tree(tree)
    
    if val != "ERROR":
        if float(val).is_integer():
            val = int(val)
        else:
            val = round(val, 4)
            
    return tree_str, token_str, val

def evaluate_file(input_path):
    with open(input_path, 'r') as f_in, open("output.txt", 'w') as f_out:
        for line in f_in:
            clean_line = line.strip()
            if not clean_line: continue
            
            t_out, k_out, r_out = process_line(clean_line)
            
            f_out.write(f"Input: {clean_line}\n")
            f_out.write(f"Tree: {t_out}\n")
            f_out.write(f"Tokens: {k_out}\n")
            f_out.write(f"Result: {r_out}\n\n")

if __name__ == "__main__":
    evaluate_file("evaluator_input.txt")