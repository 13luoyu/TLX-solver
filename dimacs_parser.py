def parse(filename):
    clause_list = []
    # print(filename)
    with open(filename, "r") as file:
        for index, line in enumerate(file):
            # print(index,line)
            if index == 1:
                l = line.split()
                var_num, clause_num = int(l[2]), int(l[3])
            if index > 1:
                clause_list.append([int(num.strip()) for num in line.split()[:-1]])

    # print(clause_list)
    # print(var_num)
    # print(clause_num)
    return clause_list, var_num, clause_num
