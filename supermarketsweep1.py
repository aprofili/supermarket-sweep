#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 13 12:16:38 2021

@author: brynnschne
"""
import numpy as np
import csv
from pprint import pprint
import matplotlib as plt

class Item:
    def __init__(self, name, price, x, y):
        self.name = name
        self.price = float(price)
        self.x = int(x)
        self.y = int(y)

    def __repr__(self):
        return self.name + ": $" + str(self.price) + " at " + str(self.x) + ", " + str(self.y)

item_list = []
with open("Supermarket Sweep.csv", "r") as file:
    reader = csv.reader(file)
    next(reader)
    for row in reader:
        item_list.append(Item(row[0], row[1], row[2], row[3]))

#pprint(item_list)

d = [[0 for i in range(len(item_list))] for i in range(len(item_list))]
for i in range(len(item_list)):
    for j in range(len(item_list)):
        item_i = item_list[i]
        item_j = item_list[j]

        if item_i.x == item_j.x:
            d[i][j] = abs(item_i.y - item_j.y) / 10
        else:
            dist_x = abs(item_i.x - item_j.x)
            dist_y = min(((110 - item_i.y) + (110 - item_j.y) ), item_i.y + item_j.y)
            d[i][j] = (dist_x + dist_y) / 10

d.append(d[0])
for i in range(len(d[0])):
    d[i].append(d[i][0])
pprint(np.array(d))

from gurobipy import GRB, Model,quicksum
m = Model('Supermarket Sweep')

n= len(item_list)
# print(n)
v=[i.price for i in item_list]
v.append(0.0)
max_time=90
cart_cap=15
mip_gap = 0.0001
max_time=90
cart_cap=15
mip_gap=0.0001
print_output=True

#print(v)
#print(len(d[0]),len(d),len(v))
# d=[[1,2,3,4,5,6],[1,2,3,4,5,6],[1,2,3,4,5,6],[1,2,3,4,5,6],[1,2,3,4,5,6],[1,2,3,4,5,6]]

x=m.addVars(range(1,n+1), range(2,n+2), vtype=GRB.BINARY, name='x') #if path from item i to j is in the sweep
y=m.addVars(range(1,n+2), vtype=GRB.CONTINUOUS, name='y',lb=0) #seconds from start to item i during sweep
t=m.addVars(range(1,n+1), range(2,n+2), vtype=GRB.CONTINUOUS, name='t',lb=0) # seconds from start to item j if node j comes after node i

m.addConstr(y[1]==0) # starts with node 1  and time 0
m.addConstrs(x[i,i]==0 for i in range(2,n+1)) # nodes cannot connect to themselves
m.addConstrs(quicksum([x[i,j] for i in range(1,n+1)])<=1 for j in range(2,n+2)) # all nodes follow 0 or 1 node
m.addConstrs(quicksum([x[i,j] for j in range(2,n+2)])<=1 for i in range(1,n+1)) # all nodes are followed by 0 or 1 node
m.addConstrs(t[i,j]<=max_time*x[i,j] for i in range(1,n+1) for j in range(2,n+2)) # if node i doesn't go to node j, then t[i, j] is 0
m.addConstrs(y[j]==quicksum([t[i,j] for i in range(1,n+1)]) for j in range(2,n+2)) # y[j] is equal to the only positive t[i, j]
m.addConstrs(quicksum([t[j,k] for k in range(2,n+2)])==y[j]+quicksum([d[j-1][k-1]*x[j,k] for k in range(2,n+2) ]) for j in range(1,n+1)) # defines t[i, j] to be the time up to the i plus the time from the i to j
m.addConstr(y[n+1]<=max_time) # total time less than 90 seconds
m.addConstr(quicksum([x[i, n+1] for i in range(1, n+1)]) == 1) # node n+1 must be visited
m.addConstr(quicksum([x[1, j] for j in range(2, n+2)]) == 1) # node 1 must be visited
m.addConstr(quicksum([quicksum([x[i,j] for i in range(1,n+1)]) for j in range(2,n+2)])<= cart_cap + 1) #at most 15 items in the cart (not including the end node)

# m.addConstr(quicksum([x[n+1, j] for i in range(1, n+1)]) == 0) # node n+1 must come last
# m.addConstrs(y[n+1] >= y[i] for i in range(1, n+1)) #node n+1 must come last


# m.setObjective(y[n+1],GRB.MINIMIZE) # minimize time to the last node
# m.setObjective(quicksum([quicksum([d[i-1][j-1] * x[i, j] for j in range(2, n+2)]) for i in range(1, n+1)]),GRB.MINIMIZE) # same as previous
m.setObjective(quicksum([v[i-1]*quicksum([x[i,j] for j in range(2,n+2)]) for i in range(1,n+1)]), GRB.MAXIMIZE) # maximize cost of items collected


if not print_output:
    m.setParam("LogToConsole", 0)

m.setParam("MIPGap", mip_gap)


m.optimize()
print(m.ObjVal)
nodedict={}
count = 0
for i in range(1,n+1):
    for j in range(2,n+2):
        if int(x[i,j].x):
            count += 1
            nodedict[i]=j

pprint(nodedict)
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
    print("winnings " + str(winnings))

    time = 0
    for (i, j) in nodedict.items():
        time += d[i-1][j-1]
    print(f"\nTime used: {time} seconds\n\n\n")

#m = Model('Supermarket Sweep')
#
#n= len(item_list)
#print(n)
#v=[i.price for i in item_list]
#v.append(0.0)
#maxtime=90
#cart_cap=15
#
##v=[0,5,10,6,11,0]
##item_list=[['start',0,0,0],['a',5,10,10],['b',10,10,15],['c',6,20,10],['d',11,20,15]]
##n=len(item_list)
##print(v)
##print(len(d[0]),len(d),len(v))
## d=[[1,2,3,4,5,6],[1,2,3,4,5,6],[1,2,3,4,5,6],[1,2,3,4,5,6],[1,2,3,4,5,6],[1,2,3,4,5,6]]
#
#x=m.addVars(range(1,n+1), range(2,n+2), vtype=GRB.BINARY, name='x') #if path from item i to j is in the sweep
#y=m.addVars(range(1,n+2), vtype=GRB.CONTINUOUS, name='y',lb=0) #seconds from start to item i during sweep
#t=m.addVars(range(1,n+1), range(2,n+2), vtype=GRB.CONTINUOUS, name='t',lb=0) # seconds from start to item j if node j comes after node i
#
#m.addConstr(y[1]==0) # starts with node 1  and time 0
#m.addConstrs(x[i,i]==0 for i in range(2,n+1)) # nodes cannot connect to themselves
#m.addConstrs(quicksum([x[i,j] for i in range(1,n+1)])<=1 for j in range(2,n+2)) # all nodes follow 0 or 1 node
#m.addConstrs(quicksum([x[i,j] for j in range(2,n+2)])<=1 for i in range(1,n+1)) # all nodes are followed by 0 or 1 node
#m.addConstrs(t[i,j]<=maxtime*x[i,j] for i in range(1,n+1) for j in range(2,n+2)) # if node i doesn't go to node j, then t[i, j] is 0
#m.addConstrs(y[j]==quicksum([t[i,j] for i in range(1,n+1)]) for j in range(2,n+2)) # y[j] is equal to the only positive t[i, j]
#m.addConstrs(quicksum([t[j,k] for k in range(2,n+2)])==y[j]+quicksum([d[j-1][k-1]*x[j,k] for k in range(2,n+2) ]) for j in range(1,n+1)) # defines t[i, j] to be the time up to the i plus the time from the i to j
#m.addConstr(y[n+1]<=maxtime) # total time less than 90 seconds
#m.addConstr(quicksum([x[i, n+1] for i in range(1, n+1)]) == 1) # node n+1 must be visited
#m.addConstr(quicksum([x[1, j] for j in range(2, n+2)]) == 1) # node 1 must be visited
#m.addConstr(quicksum([quicksum([x[i,j] for i in range(1,n+1)]) for j in range(2,n+2)])<= cart_cap+1)
#
## m.addConstr(quicksum([x[n+1, j] for i in range(1, n+1)]) == 0) # node n+1 must come last
## m.addConstrs(y[n+1] >= y[i] for i in range(1, n+1)) #node n+1 must come last
#
#
##m.setObjective(y[n+1],GRB.MINIMIZE) # minimize time to the last node
##m.setObjective(,GRB.MINIMIZE) # same as previous
#m.setObjective(quicksum([v[i-1]*quicksum([x[i,j] for j in range(2,n+2)]) for i in range(1,n+1)]), GRB.MAXIMIZE) # maximize cost of items collected
##m.setObjective(quicksum([v[j-1]*quicksum([x[i,j] for i in range(1,n+1)]) for j in range(2,n+1)]), GRB.MAXIMIZE)
#
#m.optimize()
##class Node:
##    def __init__(self, item, next):
##        self.item=item
##
##    def __repr__(self):
##        return 'item '+ str(self.i) + " comes before item " + str(self.next.item)
#
#print("\nOptimal Value: %s" % (str(m.ObjVal)))
#print("\n\n")
#
#nodedict={}
#count = 0
#for i in range(1,n+1):
#    for j in range(2,n+2):
#        if int(x[i,j].x):
#            print(str(item_list[i-1])+'  ' + str(i) +'-->'+str(j))
#            count +=1
#            nodedict[i]=j
#
#i = 1
#print(i)
#for rep in range(count):
#    i = nodedict[i]
#    print(i)
#
## print(count)
#time = 0
#for (i, j) in nodedict.items():
#    time += d[i-1][j-1]
## print(time)
