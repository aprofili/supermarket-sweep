#import numpy as np
import csv
from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np

class Item:
    def __init__(self, name, price, x, y):
        self.name = name
        self.price = float(price)
        self.x = int(x)
        self.y = int(y)

    def __repr__(self):
        return f"{self.name}: ${self.price} at ({self.x},{self.y})"

item_list = []
with open("Supermarket Sweep.csv", "r") as file:
    reader = csv.reader(file)
    next(reader)
    for row in reader:
        item_list.append(Item(row[0], row[1], row[2], row[3]))

#pprint(item_list)

d = [[0 for i in range(len(item_list))] for i in range(len(item_list))]
for i in range(len(item_list)):
    for j in range(i,len(item_list)):
        item_i = item_list[i]
        item_j = item_list[j]

        if item_i.x == item_j.x:
            d[i][j] = (abs(item_i.y - item_j.y) / 10)
            d[j][i] = (abs(item_i.y - item_j.y) / 10)
        else:
            dist_x = abs(item_i.x - item_j.x)
            dist_y = min(((110 - item_i.y) + (110 - item_j.y) ), item_i.y + item_j.y)
            d[i][j] = ((dist_x + dist_y) / 10)
            d[j][i] = ((dist_x + dist_y) / 10)
        if i!=j:            #brynn
            d[j][i]+=2      #brynn
            d[i][j]+=2     #brynn

#d = [[0 for i in range(len(item_list))] for i in range(len(item_list))]
#for i in range(len(item_list)):
#    for j in range(len(item_list)):
#        item_i = item_list[i]
#        item_j = item_list[j]
#
#        if item_i.x == item_j.x:
#            d[i][j] = abs(item_i.y - item_j.y) / 10
#        else:
#            dist_x = abs(item_i.x - item_j.x)
#            dist_y = min(((110 - item_i.y) + (110 - item_j.y) ), item_i.y + item_j.y)
#            d[i][j] = (dist_x + dist_y) / 10


#for i in range(len(d[0])):         #adam
#    d[i].append(d[i][0])           #adam

d.append(d[0])
for i in range(len(d[0])):
    if i in [0, len(d[0])-1]:
        d[i].append(d[i][0])
    else:
        d[i].append(d[i][0] - 2)


#for i in range(len(d)):            #adam
#    for j in range(len(d) - 1):    #adam
#       d[i][j] = d[i][j] + 2       #adam
        
pprint(np.array(d))
#nd=len(d)
#nd0=len(d[0])
#maxd= max([d[i][j] for i in range(nd) for j in range(nd0)])
#print(maxd)

from gurobipy import GRB, Model,quicksum

def optimize(part, max_time=90, cart_cap=15, mip_gap=0.0001, print_output=False):

    m = Model('Supermarket Sweep')

    n= len(item_list)
    # print(n)
    v=[i.price for i in item_list]
    v.append(0.0)
    # max_time=90
    # cart_cap=15
    # mip_gap = 0.0001

    x=m.addVars(range(1,n+1), range(2,n+2), vtype=GRB.BINARY, name='x') #if path from item i to j is in the sweep
    y=m.addVars(range(1,n+2), vtype=GRB.CONTINUOUS, name='y') #seconds from start to item i during sweep
    t=m.addVars(range(1,n+1), range(2,n+2), vtype=GRB.CONTINUOUS, name='t',lb=0) # seconds from start to item j if node j comes after node i

    m.addConstr(y[1]==0) # starts with node 1  and time 0
    m.addConstrs(x[i,i]==0 for i in range(2,n+1)) # nodes cannot connect to themselves
    m.addConstr(quicksum([x[1, j] for j in range(2, n+2)]) == 1) # node 1 must be visited
    m.addConstrs(quicksum([x[i,j] for i in range(1,n+1)])<=1 for j in range(2,n+2)) # all nodes follow 0 or 1 node
    m.addConstrs(quicksum([x[i,j] for j in range(2,n+2)])<=1 for i in range(1,n+1)) # all nodes are followed by 0 or 1 node
    m.addConstr(quicksum([x[i, n+1] for i in range(1, n+1)]) == 1) # node n+1 must be visited
    m.addConstrs(t[i,j]<=max_time*x[i,j] for i in range(1,n+1) for j in range(2,n+2)) # if node i doesn't go to node j, then t[i, j] is 0
    m.addConstrs(y[j]==quicksum([t[i,j] for i in range(1,n+1)]) for j in range(2,n+2)) # y[j] is equal to the only positive t[i, j]
    m.addConstrs(quicksum([t[j,k] for k in range(2,n+2)])==y[j]+quicksum([(d[j-1][k-1])*x[j,k] for k in range(2,n+2) ]) for j in range(1,n+1)) # defines t[i, j] to be the time up to the ith node plus the time from the ith to jth node
    #m.addConstr(y[n+1]<=max_time) # total time less than 90 seconds
    m.addConstr(quicksum([quicksum([x[i,j] for i in range(1,n+1)]) for j in range(2,n+1)])<= cart_cap) #at most 15 items in the cart (not including the end node)
    # m.addConstr(quicksum([x[n+1, j] for i in range(1, n+1)]) == 0) # node n+1 must come last
    # m.addConstrs(y[n+1] >= y[i] for i in range(1, n+1)) #node n+1 must come last
    m.addConstrs(quicksum([x[i,j] for i in range(1,n+1)])== quicksum([x[j,k] for k in range(2,n+2)]) for j in range(2,n+1)) # nodes that arent arrived at are also not departed from

    # m.setObjective(y[n+1],GRB.MINIMIZE) # minimize time to the last node
    # m.setObjective(quicksum([quicksum([d[i-1][j-1] * x[i, j] for j in range(2, n+2)]) for i in range(1, n+1)]),GRB.MINIMIZE) # same as previous
    m.setObjective(quicksum([v[i-1]*quicksum([x[i,j] for j in range(2,n+2)]) for i in range(1,n+1)]), GRB.MAXIMIZE) # maximize cost of items collected


    if not print_output:
        m.setParam("LogToConsole", 0)

    m.setParam("MIPGap", mip_gap)


    m.optimize()

    nodedict={}
    count = 0
    for i in range(1,n+1):
        for j in range(2,n+2):
            if int(x[i,j].x):
                count +=1
                nodedict[i]=j

    # pprint(nodedict)
    if print_output:
        print(f"\n\n\nMoney Won: ${m.ObjVal}")
        print("")


        print("Path Taken:")
        i = 1
        winnings = 0
        for rep in range(count):
            winnings += item_list[i-1].price
            print(f"Node {i}: {item_list[i-1]}")
            i = nodedict[i]
        print("Back to Start (0,0)\nFinished")
        # print("winnings " + str(winnings))

        time = 0
        for (i, j) in nodedict.items():
            time += d[i-1][j-1]
        print(f"\nTime used: {time} seconds\n\n\n")
    if part == "f":
        return m.Runtime
    return m.ObjVal





parts = "d"
max_times = range(50, 131, 5)
cart_caps = range(5, 26)
mip_gaps = [10**-5,10**-4,10**-3,5*10**-3,10**-2,10**-(5/3),10**-(4/3),10**-1,10**-(2/3),10**-(1/3),10**0]


for part in parts:
    if part == "c":
        optimize(print_output=True, part="c")
    if part == "d":
        d_results = []
        for max_time in max_times:
            d_results.append(optimize(max_time=max_time, part="d"))
        print("\nD GRAPH")
        plt.plot([int(i) for i in max_times],d_results, marker='o')
        plt.xlabel("Number of seconds allotted to competitors (s)")
        plt.ylabel("Optimal value ($)")
        plt.show()
        print("d results")
        print(d_results)
    if part == "e":
        e_results = []
        for cart_cap in cart_caps:
            e_results.append(optimize(cart_cap=cart_cap, part="e"))
        print("\nE GRAPH")
        plt.plot([int(i) for i in cart_caps],e_results, marker='o')
        plt.xlabel("Maximum Number of Items Allowed In Cart")
        plt.ylabel("Optimal value ($)")
        plt.show()
        print("e results")
        print(e_results)
    if part == "f":
        f_results = []
        for mip_gap in mip_gaps:
            op=optimize(mip_gap=(mip_gap), part="f")
            f_results.append(op)
            print(op)
        print("\nF GRAPH")
        plt.plot(mip_gaps,f_results, marker='o')
        plt.xlabel("MIP Parameter in Optimization Problem")
        plt.ylabel("Optimal value ($)")
        plt.show()
        print("f results")
        print(f_results)


#d_results=[120,130,150,180,220]
#plt.plot([int(i) for i in max_times],d_results, marker='o')
#plt.xlabel("Number of seconds allotted to competitors (s)")
#plt.ylabel("Optimal value ($)")
#plt.show()
