# import sys
import random
#todo



var_num = 0 #范式中变量个数
clause_num = 0  #范式中子句个数
clause_list = []    #子句列表
varvalue = []   #存储变量的赋值

'''
class Cnf: #定义一个类存取cnf范式相关信息
    def __init__(self,var_num,clause_num,clause_lists):
        self.var_num = var_num  #范式中变量个数
        self.clause_num = clause_num    #范式中子句个数
        self.clause_list = []       #范式中字句列表
        for i in range(0,clause_num):
            self.clause_list.append(set(clause_lists[i]))

    def add_clause(self,clause):    #给范式添加子句
        self.clause_list.append(set(clause))
        self.clause_num = self.clause_num + 1
 
    def printlist(self):
        for i in range(0,8):
            print(self.clause_list[i])
'''

class Tnode:    #定义决策数的节点
    def __init__(self,var , value , level):
        self.var = var  #节点表示的变量
        self.value = value  #变量的取值 -1 or 1
        self.level = level  #节点所在决策层
        self.pre_var = []   #先验节点
        self.next_var = []  #后继继节点

    def add_prevar(self, var):  #添加前驱节点
        self.pre_var.append(var)

    def add_nextvar(self, var):     #添加后继节点
        self.next_var.append(var)

    def del_prevar(self,var):
        self.pre_var.remove(var)

    def del_nextvar(self,var):
        self.next_var.remove(var)

    def itself(self):
        print(self.var , self.value , self.level , self.pre_var, self.next_var)

class Tree:
    def __init__(self):
        self.tnodes = []    #节点列表，存树的节点

    def add_tnode(self,node):   #添加树的节点
        self.tnodes.append(node)

    def get_tnodenum(self,var):     #得到变量var在节点列表中的下标
        for index,tnode in enumerate(self.tnodes):
            if tnode.var == var:
                return index

    def printself(self):
        for t in self.tnodes:
            t.itself()


def dimacs_parser(file_path):
    f=open(file_path,"r")
    flag = 0
    global var_num
    global clause_num
    global clause_list
    for line in f.readlines():
        # 判断flag,p cnf之后开始遍历clause
        if flag:
            l = line.split(' ')
            c_l = []
            for key in l[:-1]:
                c_l.append(int(key))
            clause_list.append(set(c_l))
        if line[0]=='p':
            #标记p cnf开始
            flag = 1
            l = line.split(' ')
            var_num = int(l[2])
            clause_num = int(l[3])
    f.close()


#检查子句是否可满足
def check_impossible_clause(clause):
    u_var_num = 0   #未赋值的变量个数
    for v in clause:
        if varvalue[abs(v)-1] == None:  #若该元素未赋值
            u_var_num = u_var_num + 1
            u_var = v
            gener_literals = []
            for literal in clause : #将子句中其它元素添加到literal列表中
                if literal != u_var:
                    gener_literals.append(literal)
        elif (varvalue[abs(v)-1] == True and v > 0) or (varvalue[abs(v)-1] == False and v < 0):
            #判断为真的clause
            return False , None , None
    if u_var_num == 0:  #冲突
        return True , None , None
    if u_var_num == 1:  #有一个变量的值可以被确定
        return False , u_var , gener_literals
    #多个变量值未确定
    return False , None , None


#单位传播冲突判断
def unitpropagation_conflict(tree:Tree,level:int):
    for clause in clause_list:  #遍历所有的子句
#检查子句可能赋值情况，possible：当前赋值的子句是否冲突 u_literal:变量名 a_literals：子句其它变量集合
        possible , u_literal , a_literals = check_impossible_clause(clause)
        if possible:    #若单位传播冲突，返回True
            return True
        elif u_literal != None: #若有一个变量的值在单位传播中可以被确定
            value = True if u_literal > 0 else False    #给元素赋值 True(大于零) or False(小于零)
            varvalue[abs(u_literal)-1] = value
            tree.add_tnode(Tnode(abs(u_literal),value,level))   #将该元素添加进决策树中
            node_num = len(tree.tnodes) - 1 #tnode在tree list 中的下标
            for literal in a_literals:  #子句其它元素为该元素的先验节点
                pre_node_num = tree.get_tnodenum(abs(literal))
                tree.tnodes[pre_node_num].add_nextvar(node_num)
                tree.tnodes[node_num].add_prevar(pre_node_num)
            return unitpropagation_conflict(tree, level)    #继续进行单位传播冲突判断
    return False

#冲突分析
def conflict_analysis(tree:Tree , level:int):
    if level == 0:  #若第0层发生冲突，返回-1，表示范式无解
        return -1
    level_set = set()   #约束节点所处层集合
    node_set = set()    #新的约束节点集合
    for node in tree.tnodes[::-1]:  #倒序遍历决策树节点列表
        if node.level == level and node.pre_var != []:  #节点在当层，且有先验节点
            for i in node.pre_var:  #遍历先验节点
                if tree.tnodes[i].level < level or \
                        (tree.tnodes[i].level == level and tree.tnodes[i].pre_var == []):
                    node_set.add(tree.tnodes[i])
                    level_set.add(tree.tnodes[i].level)
        if node.level == level and node.pre_var == []:  #节点在当层，且无先验节点
            node_set.add(node)
            level_set.add(node.level)
        if node.level < level:  #节点所处层小于当层
            break
    literal_list = []
    for node in node_set:   #添加新的约束子句
        literal_list.append(-node.var if node.value else node.var)
    clause_list.append(literal_list)
    return min(level_set)

#回溯
def backtrack(tree:Tree , flag:int):
    end = None
    for i in range(len(tree.tnodes)):
        if tree.tnodes[i].level < flag: #若节点所在层小于回溯层，处理其先验和后继节点
            tree.tnodes[i].next_var = [var_n for var_n in tree.tnodes[i].next_var
                                       if tree.tnodes[i].level < flag]
            tree.tnodes[i].pre_var = [var_n for var_n in tree.tnodes[i].pre_var
                                      if tree.tnodes[i].level < flag]
        else:   #若节点所在层大于回溯层，则清空该节点
            if end == None: end = i
            varvalue[tree.tnodes[i].var - 1] = None
    if end == 0:    #截断[0:end]
        tree.tnodes = []
    else:
        tree.tnodes = tree.tnodes[:end]

def cdcl_solver(tree:Tree):
    level = 0   #从决策层0开始
    conflict = False    #预定义不冲突
    if unitpropagation_conflict(tree,level):    #单位传播冲突判断，若0层就冲突，则表达式无解
        return False
    while None in varvalue:     #直到所有变量都被赋值
        if conflict:    #单位传播冲突判断
            if unitpropagation_conflict(tree,level):
                return False    #若冲突，表达式无解
        for index , val in enumerate(varvalue):     #找到未赋值的变量
            if val == None:
                var_n = index
                var_v = random.randrange(0,2)   #随机赋值 True or False
        level = level + 1       #决策层加一
        varvalue[var_n] = bool(var_v)   #更新变量赋值列表
        tree.add_tnode(Tnode(abs(int(var_n)+1),bool(var_v),level))  #更新决策树
        conflict = unitpropagation_conflict(tree,level) #单位冲突判断
        if conflict:
            flag = conflict_analysis(tree,level)    #分析冲突原因
            if flag < 0:        #若回溯到第0层还发生冲突，表达式无解
                return False
            else:
                backtrack(tree,flag)    #回溯到第flag层
                level = flag - 1
    return True     #若所有变量均赋值且完成循环，则表达式有解

if __name__=="__main__":


    file_path = "tests/sat/test6.txt"
    # file_path = "/Users/tserr/Documents/iPROJECT/PyCharmProject/PyPrj/CDCL-based-SAT-solver/tests/sat/test1.txt"
    # print(file_path)
    # var_num,clause_num,clause_list = dimacs_parser(file_path)
    dimacs_parser(file_path)
    print(var_num,clause_num,clause_list)

    # print(c.printlist())
    for i in range(var_num):
        varvalue.append(None)
    print(varvalue)
    tree = Tree()
    print('-----------------')
    ans = cdcl_solver(tree)
    print(varvalue , ans)
    tree.printself()



[0, 1, 1, 1, 1, 0, 0, 1, 1, 1]