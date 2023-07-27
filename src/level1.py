import os
import sys
import itertools

def analy_string(str):
    operands = list()
    sign=1
    num = [True for i in range(10)]
    alphab = {}
    alphab['.'] = 0
    temp = ""
    result =""
    maxsize=0
    type = 1
    for i in range(len(str)):
        if('A' <= str[i] <= 'Z'):
            if(str[i]not in alphab):
                alphab[str[i]] = -1
            if(type == 1):
                temp = temp + str[i]
            else:
                result = result + str[i]
        else:
            if(str[i]=='+' or str[i] =='-'):
                operands.append(temp)
                if(len(temp)>maxsize):
                    maxsize = len(temp)
                temp=""
                if(str[i]=='-'):
                    sign=-1
            else:
                operands.append(temp)
                if (len(temp) > maxsize):
                    maxsize = len(temp)
                type=2
    if(maxsize < len(result)):
        maxsize=len(result)
    n = len(operands)
    matrix = [['.' for _ in range(maxsize)] for _ in range(len(operands)+1)]
    for i in range(n):
        k=len(operands[i])-1
        for j in range(maxsize-1,-1,-1):
            if(k!=-1):
                matrix[i][j]=operands[i][k]
                k=k-1
            else:
                break

    alphab = dict(sorted(alphab.items()))
    j=len(result)-1
    for i in range(maxsize-1,-1,-1):
        if(j>=0):
            matrix[n][i]=result[j]
            j=j-1
    t = checkcolumn(0,matrix,0,alphab,sign,n,num)
    if(t==-1):
        showresult(0,None)

def checkcolumn(col,matrix,debt,alphab,sign,n,num):
    if(col == len(matrix[0])):
        showresult(1, alphab)
        return 1
    num_operands=0
    con=[]
    unknow_al=[]
    al_copy = {}
    for i in range(n):
        oper = 1
        if(sign==-1 and i>0):
            oper=-1
        if('A' <= matrix[i][col] <='Z'):
            num_operands+=1

            #kiếm tra xem chữ cái đó có phải đứng đầu hay không => check điều kiện để nó khác 0
            if(col==0 or matrix[i][col-1]=='.'):
                con.append(matrix[i][col])

            if(matrix[i][col] in al_copy):
                al_copy[matrix[i][col]] = al_copy[matrix[i][col]] + oper
            else:
                al_copy[matrix[i][col]] = oper
            if(alphab[matrix[i][col]] == -1 and matrix[i][col] not in unknow_al):
                unknow_al.append(matrix[i][col])
    al_copy=dict(sorted(al_copy.items()))

    #nếu cột đó chỉ có đúng dòng kết quả có chữ => chữ kết quả là sinh ra từ phép toán ở cột kế bên
    if(num_operands==0):
        index=1
        while (index<n):
            alphab[matrix[n][col]] = index
            num[index]=False
            t = checkcolumn(col+1,matrix,-index,alphab,sign,n,num)
            if(t==1):
                return t
            num[index]=True
            index+=1
        return -1

    res = matrix[n][col]

    if (col == 0 or matrix[n][col-1]=='.'):
        con.append(res)

    if (alphab[res] == -1 and res not in unknow_al):
        unknow_al.append(res)

    #thuc hien loop va backtracking tai day

    #unknow_al: Chuỗi chữ chưa biết cần đc thêm số dự đoán vào
    #num: chuỗi các số có thể được gán
    #al_copy: chuỗi chữ có mặt trong phép toán tại cột này
    #res: kết quả của phép toán tại cột này (có thể xuất hiện trong unknow_al)
    #debt: con nợ từ phép toán ở cột trước, sẽ biến kết quả thành 10*deb+res

    # Mapping giữa unkow_al và num để tìm tổ hợp chữ và số phù hợp
    unique_digits = set(range(10))
    available_digits = [digit for digit, can_assign in zip(unique_digits, num) if can_assign]

    for permutation in itertools.permutations(available_digits, len(unknow_al)):
        mapping = dict(zip(unknow_al, permutation))
        if all(mapping[char] == digit for char, digit in zip(unknow_al, permutation) if digit):
            flag=True
            for c in con:
                if(c in unknow_al and mapping[c]==0):
                    flag=False
                    break
            if(flag==False): continue
            alphab,num=add_to_check(alphab,mapping,num)
            check_goal=check(alphab,al_copy,res,debt,n)
            if(check_goal==None or (check_goal!=0 and col==len(matrix[0])-1)):
                alphab, num = remove(alphab, mapping, num)
                continue
            else:
                t = checkcolumn(col+1,matrix,check_goal,alphab,sign,n,num)
                if(t==1):
                    return 1
                alphab, num = remove(alphab, mapping, num)

    return -1

def add_to_check(alphab,mapping,num):
    for c in mapping:
        alphab[c] = mapping[c]
        num[mapping[c]]=False
    return alphab,num

def remove(alphab,mapping,num):
    for c in mapping:
        alphab[c] = -1
        num[mapping[c]] = True
    return alphab,num

def check(alphab,al_copy,res,debt,n):
    result=0
    math=0
    for c in al_copy:
        math=math+al_copy[c]*alphab[c]
    result=alphab[res]
    if(debt>=0):
        math=math+10*debt
    else:
        result=result+10*(-debt)
    if(math==result):
        return 0

    #nếu phép toán chỉ bé hơn kết quả mong muốn với số <=n-1
    if(0 < result-math<n):
        return -(result-math)

    # nếu phép toán chỉ lớn hơn kết quả mong muốn với số <=n-1
    if (0 < math-result < n):
        return (math-result)

    return  None

current_script_path = os.path.abspath(__file__)
# Extract the directory from the script path
current_folder = os.path.dirname(current_script_path)

input_file = current_folder + "\\testcases\\input\\input1.txt"
output_file = current_folder + "\\testcases\\output\\output1.txt"

def showresult(t,res):
    file_name = output_file
    try:
        with open(file_name, 'a') as file:
            if(t==0): #mean no solution found
                file.write("NO SOLUTION\n")
            else:
                for c in res:
                    if (c != '.'):
                        num = str(c)
                        file.write(num)
                file.write("=")
                for c in res:
                    if (c != '.'):
                        num = str(res[c])
                        file.write(num)
                file.write('\n')

    except IOError:
        print("An error occurred while writing to the file.")


file_name = input_file
try:
    with open(file_name, 'r') as file:
        case_tests = file.readlines()
        string_list = [case.strip() for case in case_tests]

    # create and reset output file
    file_name = output_file
    open(file_name, 'w')

    for string in string_list:
        print(string)
        analy_string(string)

except FileNotFoundError:
    print("File not found. Please check the file path.")
except IOError:
    print("An error occurred while reading the file.")


