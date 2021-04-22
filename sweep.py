#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 13 12:16:38 2021

@author: brynnschne
"""
import numpy as np
import csv
from pprint import pprint

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

for i in range(len(d)):
    for j in range(len(d) - 1):
        d[i][j] = d[i][j] + 2

from gurobipy import GRB, Model,quicksum

m = Model('Supermarket Sweep')

n= len(item_list)
print(n)
v=[i.price for i in item_list]
v.append(0.0)
maxtime=90
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
m.addConstrs(t[i,j]<=maxtime*x[i,j] for i in range(1,n+1) for j in range(2,n+2)) # if node i doesn't go to node j, then t[i, j] is 0
m.addConstrs(y[j]==quicksum([t[i,j] for i in range(1,n+1)]) for j in range(2,n+2)) # y[j] is equal to the only positive t[i, j]
m.addConstrs(quicksum([t[j,k] for k in range(2,n+2)])==y[j]+quicksum([d[j-1][k-1]*x[j,k] for k in range(2,n+2) ]) for j in range(1,n+1)) # defines t[i, j] to be the time up to the i plus the time from the i to j
m.addConstr(y[n+1]<=maxtime) # total time less than 90 seconds
m.addConstr(quicksum([x[i, n+1] for i in range(1, n+1)]) == 1) # node n+1 must be visited
m.addConstr(quicksum([quicksum([x[i,j] for i in range(1,n+1)]) for j in range(2,n+2)])<= 15 + 1) #at most 15 items in the cart (not including the end node)

# m.addConstr(quicksum([x[n+1, j] for i in range(1, n+1)]) == 0) # node n+1 must come last
# m.addConstrs(y[n+1] >= y[i] for i in range(1, n+1)) #node n+1 must come last


# m.setObjective(y[n+1],GRB.MINIMIZE) # minimize time to the last node
# m.setObjective(quicksum([quicksum([d[i-1][j-1] * x[i, j] for j in range(2, n+2)]) for i in range(1, n+1)]),GRB.MINIMIZE) # same as previous
m.setObjective(quicksum([v[i]*quicksum([x[i,j] for j in range(i+1,n+2)]) for i in range(1,n+1)]), GRB.MAXIMIZE) # maximize cost of items collected

m.optimize()


print(f"\n\n\nMoney Won: ${m.ObjVal}")
print("")

nodedict={}
count = 0
for i in range(1,n+1):
    for j in range(2,n+2):
        if int(x[i,j].x):
            count +=1
            nodedict[i]=j

print("Path Taken:")
i = 1
for rep in range(count):
    print(f"Node {i}: {item_list[i-1]}")
    i = nodedict[i]
print("Back to Start (0,0)\nFinished")


time = 0
for (i, j) in nodedict.items():
    time += d[i-1][j-1]
print(f"\nTime used: {time} seconds")

