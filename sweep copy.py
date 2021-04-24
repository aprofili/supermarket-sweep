#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 13 12:16:38 2021

@author: brynnschne
"""
#import numpy as np
import csv
from pprint import pprint
import matplotlib.pyplot as plt

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
        if i!=j:
            d[j][i]+=2
            d[i][j] +=2
#
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

#.append(d[0])
for i in range(len(d[0])):
    d[i].append(max(d[i][0]-2,0))
# pprint(np.array(d))

#for i in range(len(d)):
#    for j in range(len(d) - 1):
#        d[i][j] = d[i][j] + 2
#nd=len(d)
#nd0=len(d[0])
#maxd= max([d[i][j] for i in range(nd) for j in range(nd0)])
#print(maxd)

from gurobipy import GRB, Model,quicksum

def optimize(max_time=90, cart_cap=15, mip_gap=0.0001, print_output=False):

    m = Model('Supermarket Sweep')

    n= len(item_list)
    # print(n)
    v=[i.price for i in item_list]
    v.append(0.0)
    # max_time=90
    # cart_cap=15
    # mip_gap = 0.0001

    x=m.addVars(range(1,n+1), range(2,n+2), vtype=GRB.BINARY, name='x') #if path from item i to j is in the sweep
    y=m.addVars(range(1,n+2), vtype=GRB.CONTINUOUS, name='y',lb=0) #seconds from start to item i during sweep
    t=m.addVars(range(1,n+1), range(2,n+2), vtype=GRB.CONTINUOUS, name='t',lb=0) # seconds from start to item j if node j comes after node i

    m.addConstr(y[1]==0) # starts with node 1  and time 0
    m.addConstrs(x[i,i]==0 for i in range(2,n+1)) # nodes cannot connect to themselves
    m.addConstrs(quicksum([x[i,j] for i in range(1,n+1)])<=1 for j in range(2,n+2)) # all nodes follow 0 or 1 node
    m.addConstrs(quicksum([x[i,j] for j in range(2,n+2)])<=1 for i in range(1,n+1)) # all nodes are followed by 0 or 1 node
    #m.addConstrs(t[i,j]<=max_time*x[i,j] for i in range(1,n+1) for j in range(2,n+2)) # if node i doesn't go to node j, then t[i, j] is 0
    m.addConstrs(t[i,j]<=max_time*x[i,j] for i in range(1,n+1) for j in range(2,n+2)) # if node i doesn't go to node j, then t[i, j] is 0
    m.addConstrs(y[j]==quicksum([t[i,j] for i in range(1,n+1)]) for j in range(2,n+2)) # y[j] is equal to the only positive t[i, j]
    m.addConstrs(quicksum([t[j,k] for k in range(2,n+2)])==y[j]+quicksum([(d[j-1][k-1])*x[j,k] for k in range(2,n+2) ]) for j in range(1,n+1)) # defines t[i, j] to be the time up to the ith node plus the time from the ith to jth node
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

    nodedict={}
    count = 0
    for i in range(1,n+1):
        for j in range(2,n+2):
            if int(x[i,j].x):
                count +=1
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

    return m.ObjVal



parts = "c"
max_times = range(80, 101, 5)
cart_caps = range(5, 26)
mip_gaps = range(5, 16)


for part in parts:
    if part == "c":
        optimize(print_output=True)
    if part == "d":
        d_results = []
        for max_time in max_times:
            d_results.append(optimize(max_time=max_time))
        for i in range(d_results-1):
            plt.plot((max_times[i],max_times[i+1]),(d_results[i],d_results[i+1]), marker='o')
        plt.show()
        print("d results")
        print(d_results)
    if part == "e":
        e_results = []
            e_results.append(optimize(cart_cap=cart_cap))
        print("e results")
        print(e_results)
    if part == "f":
        f_results = []
        for mip_gap in mip_gaps:
            f_results.append(optimize(mip_gap=(mip_gap/10000)))
        print("f results")
        print(f_results)



