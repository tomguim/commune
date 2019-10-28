#!/usr/bin/env python
import pymongo
from pymongo import MongoClient
cluster = MongoClient()

db = cluster["Resources"]
resources = db["Resources"]

db = cluster["Agents"]
agents = db["Agents"]

#Temporary part of code
resources.delete_many({})
agents.delete_many({})

class Agent():
    def __init__(self, agent_id):
        self._id = agent_id
        # Has permission to set, burn, add and remove balance of Agent.
        resourceinit = {"_id": self._id}
        agents.insert_one(resourceinit)

    def set_balance(self, amount):
        agents.update_one({"_id":self._id}, {"$set":{"balance": (amount)}})
        print "Set Balance"

    def inc_balance(self, amount):
        if amount == 0:
            print "invalid amount"
        else:
            agents.update_one({"_id":self._id}, {"$inc":{"balance": (amount)}})
            print "Add Balance"

def new_resource(resource_id, aquantity):
    #add another category of being_type_id
    resourceinit = {"_id": resourceid, "aquantity": aquantity}
        resources.insert_one(resourceinit)

def set_owner(resource_id, owner):
        resources.update_one({"_id":resource_id}, {"$set":{"owner": (owner)}})
        refresh(resource_id)
        print "New owner of ", resource_id, " is ", newowner
    #problem with this logic

def set_holder(resource_id, holder):
    resources.update_one({"_id":resource_id}, {"$set":{"holder": (holder)}})
    refresh(resource_id)
    print "New holder of ", resource_id, " is ", holder


def refresh(resource_id):
    #this will be tied to being_type_id
    #remember that availablesupply is a large category and doesnt mean available for the agent
    #fix the program so that the true availability is agent centric and based on whether they demanded or not.
    x = resources.find_one({"_id": resource_id})
    aquantity = x["aquantity"]
    try:
        drate = x["drate"]
        demand = x["demand"]    
        uses = x["uses"]
        usupply = (float(aquantity) / float(drate)) - float(uses)
    except:
        print "error fetching requirements for refresh"
    if aquantity == 0:
        usupply = 0
            # Used when you want to catalogue an object but declare it as not usable by the public (imagine protecting a tree), or if you have
            # Not catalogued an object but want to make it illegal to use if it is ever found (imagine evasive species which are not catalogued but interaction with them are regulated)
    else:
        usupply = (float(aquantity) / float(drate))
    resources.update_one({"_id": (resource_id)}, {"$set":{"usupply": (usupply)}})
    if float(usupply) >= float(demand):
        price = 0
    else:
        price = float(usupply) / float(demand)
    resources.update_one({"_id": (resource_id)}, {"$set":{"price": (price)}})

def set_aquantity(resource_id, amount):
    #this will be tied to being_type_id, aquantity will be determined by adding all the object_IDs of a being type.
    resources.update_one({"_id":(resource_id)}, {"$set":{"aquantity": (amount)}})
    try:
        refresh(resource_id)
    except:
        print "error with refresh"
    print "Set Available Supply to ", amount

def inc_aquantity(resource_id, amount):
    #this will be tied to being_type_id
    if amount == 0:
        print "Invalid amount"
    else:
        resources.update_one({"_id": (resource_id)}, {"$inc":{"aquantity": (amount)}})
        refresh(resource_id)
        print "Inc Available Supply by ", amount

def set_pquantity(resource_id, amount):
    resources.update_one({"_id": (resource_id)}, {"$set":{"pquantity": (amount)}})
    print "Set Physical Quantity to ", amount

def inc_pquantity(resource_id, amount):
    if amount == 0:
        print "Invalid amount"
    else:
        resources.update_one({"_id":(resource_id)}, {"$inc":{"pquantity": (amount)}})
        if amount > 0:
            print "Add ", amount, " Physical Quantity"
        else:
            print "Remove", amount, " Physical Quantity"

def set_drate(resource_id, amount):
    resources.update_one({"_id": (resource_id)}, {"$set":{"drate": (amount)}})
    try:
        refresh(resource_id)
    except:
        print "error with refresh"
    print "Average Deterioration Rate Changed to ", amount

def set_demand(resource_id, amount):
    #this will be tied to being_type_id
    resources.update_one({"_id":(resource_id)}, {"$set":{"demand": (amount)}})
    try:
        refresh(resource_id)
    except:
        print "error with refresh"
    print "Set Demand to ", amount

def take(agent_id, resource_id, quantity):
    #this will take x quantity of being_type_id and will transfer holding of x quantity resource_ids of being_type_id
    refresh(resource_id)
    result = resources.find_one({"_id": (resource_id)})
    price = result["price"]
    y = agents.find_one({"_id": (agent_id)})
    balance = y["balance"]
    if balance >= (price * quantity):
        agents.update_one({"_id": (agent_id)}, {"$inc":{"balance": (price * quantity)}})
        resources.update_one({"_id": (resource_id)}, {"$inc":{"aquantity": (-1)}})
        resources.update_one({"_id": (resource_id)}, {"$inc":{"uses": (quantity)}})
        refresh(resource_id)
        print agent_id, " took ", quantity, " of ", resource_id, " at ", price, "each"
    else:
        print "Insufficient funds for purchase"
        #figure out what do with set holder thing. Is this implied?
        #make sure quantity can not exceed usupply

def give(agent_id, resource_id, quantity):
    #make sure he can only give a quantity which he himself has
      # y = agents.find_one({"_id": (agent_id)})
       #balance = y["balance"]
     #  agents.update_one({"_id": (agent_id)}, {"$inc":{"balance": (price * quantity)}})
    resources.update_one({"_id": (resource_id)}, {"$inc":{"aquantity": (+1)}})
    print agent_id, " gave ", quantity, " of ", resource_id, " at ", price, "each"
        #figure out what do with set holder thing. Is this implied? 

def demand(resource_id, amount):
    #add support for the demands of agent_id
    #this will be tied to being_type_id
    resources.update_one({"_id": (resource_id)}, {"$inc":{"demand": (amount)}})
    if amount > 0:
        print "Add ", amount, " Demand"
    else:
        print "Remove", amount, "Demand"
    try:
        refresh(resource_id)
    except:
        print "error"
        #not yet included that the demand is also attributed to the self agent (for priority access)    

def delete_resource(resource_id):
    resources.delete_one({"_id": (resource_id)})
    #resource_id is the category

tom = Agent("tom")
tom.set_balance(100)

new_resource("apple", 50)

set_drate("apple", 0.5)
set_demand("apple", 1000)

take("tom", "apple", 10)

agentsresults = agents.find({})
for x in agentsresults:
    print(x)

resourcesresults = resources.find({})
for x in resourcesresults:
    print(x)
