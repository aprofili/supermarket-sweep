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

n= 5#len(item_list)
v=[i.price for i in item_list]
v.append(0.0)
maxtime=90
#print(v)
#print(len(d[0]),len(d),len(v))
d=[[1,2,3,4,5,6],[1,2,3,4,5,6],[1,2,3,4,5,6],[1,2,3,4,5,6],[1,2,3,4,5,6],[1,2,3,4,5,6]]

x=m.addVars(range(1,n+1), range(2,n+2), vtype=GRB.BINARY, name='x') #if path from item i to j is in the sweep
y=m.addVars(range(1,n+2), vtype=GRB.CONTINUOUS, name='y',lb=0) #seconds from start to item 1 during sweep
t=m.addVars(range(1,n+1), range(2,n+2), vtype=GRB.CONTINUOUS, name='t',lb=0) 

m.addConstr(y[1]==0)
m.addConstrs(x[i,i]==0 for i in range(2,n+1))
m.addConstrs(quicksum([x[i,j] for i in range(1,n+1)])==1 for j in range(2,n+2))
m.addConstrs(quicksum([x[i,j] for j in range(2,n+2)])==1 for i in range(1,n+1))
#m.addConstrs(0<=t[i,j] for i in range(1,n+1) for j in range(2,n+2))
m.addConstrs(t[i,j]<=maxtime*x[i,j] for i in range(1,n+1) for j in range(2,n+2))
m.addConstrs(y[j]==quicksum([t[i,j] for i in range(1,n+1)]) for j in range(2,n+2))
m.addConstrs(quicksum([t[j,k] for k in range(2,n+2)])==y[j]+quicksum([d[j-1][k-1]*x[j,k] for k in range(2,n+2) ]) for j in range(1,n+1))
#m.addConstr(y[n+1]<=90)
#m.addConstr(quicksum([t[i,n+1] for i in range(1,n+1)])==1)


m.setObjective(y[n+1],GRB.MINIMIZE)
#m.setObjective(quicksum([v[i]*quicksum([x[i,j] for j in range(i+1,n+2)]) for i in range(1,n+1)]), GRB.MAXIMIZE)

m.optimize()
#class Node:
#    def __init__(self, item, next):
#        self.item=item
#
#    def __repr__(self):
#        return 'item '+ str(self.i) + " comes before item " + str(self.next.item)

nodedict={}
for i in range(1,n+1):
    j=i+1
    while j <n+2:
        if int(x[i,j].x):
            nodedict[i]=j
            j=n+2
        j+=1
print(nodedict)

print("\nOptimal Value: %s" % (str(m.ObjVal)))
