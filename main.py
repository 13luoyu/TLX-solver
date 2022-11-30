import dimacs_parser
import cnf_realisation
import cdcl


# import sys

# if len (sys.argv) < 2:
#     print("Wrong input")
#     exit(1)


if __name__=="__main__":

    file_path = "tests/sat/test6.txt"
    # file_path = "/Users/tserr/Documents/iPROJECT/PyCharmProject/PyPrj/CDCL-based-SAT-solver/tests/sat/test1.txt"
    # print(file_path)
    cl_list, vars_num, clauses_num = dimacs_parser.parse(file_path)
    c = cnf_realisation.Cnf(cl_list, vars_num, clauses_num)
    # print(c.clause_list[0] | c.clause_list[1])
    # print(c.clause_list)
    vars_values = cdcl.VarValues(vars_num)
    # print(vars_values.change_var_value(1,2))
    # print(vars_values)
    impl_graph = cdcl.Graph()

    # print(impl_graph)

    print('--------')
    if cdcl.cdcl_based_solver(c, vars_values, impl_graph):
        print("SAT")
        print([int(value) for value in vars_values.list])
    else:
        print("UNSAT")