#!/usr/bin/env python
import pymongo
from pymongo import MongoClient
cluster = MongoClient()

db = cluster["Resources"]
resources = db["Resources"]

db = cluster["Agents"]
agents = db["Agents"]

db = cluster["Objects"]
objects = db["Objects"]

#Temporary part of code
resources.delete_many({})
agents.delete_many({})
objects.delete_many({})

# ******************************************
# ***************** AGENTS *****************
# ******************************************

def init_agent(agent_id):
    agentinit = {"_id": agent_id}
    #the id will later be an object id, nothing needed to init
    agents.insert_one(agentinit)


def set_balance(agent_id, amount):
    agents.update_one({"_id": agent_id}, {"$set":{"balance": amount}})
    print "Set Balance"

def inc_balance(agent_id, amount):
    if amount == 0:
        print "invalid amount"
    else:
        agents.update_one({"_id": agent_id}, {"$inc":{"balance": amount}})
        print "Add Balance"

# *********************************************
# ***************** RESOURCES *****************
# *********************************************

# ********* DEALING WITH BEING_TYPE ***********

def new_resource(being_type, physical_quantity, aquantity, owner, holder):
    #aquantity will be later determined post-init by adding a list of all objects.
    resourceinit = {"_id": being_type, "aquantity": aquantity}
    resources.insert_one(resourceinit)
    
    #Do this physical_quantity times
    objects.insert_one("being_type": being_type, "owner": owner, "holder": holder)

def refresh(being_type):
    #remember that availablesupply is a large category and doesnt mean available for the agent
    #fix the program so that the true availability is agent centric and based on whether they demanded or not.
    x = resources.find_one({"_id": being_type})
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
    resources.update_one({"_id": being_type}, {"$set":{"usupply": usupply}})
    if float(usupply) >= float(demand):
        price = 0
    else:
        price = float(usupply) / float(demand)
    resources.update_one({"_id": being_type}, {"$set":{"price": price}})

def set_aquantity(being_type, amount):
    resources.update_one({"_id":being_type}, {"$set":{"aquantity": amount}})
    try:
        refresh(being_type)
    except:
        print "error with refresh"
    print "Set Available Supply to ", amount

def inc_aquantity(being_type, amount):
    #this will be tied to being_type_id
    if amount == 0:
        print "Invalid amount"
    else:
        resources.update_one({"_id": being_type}, {"$inc":{"aquantity": amount}})
        refresh(being_type)
        print "Inc Available Supply by ", amount

def set_pquantity(being_type, amount):
    #maybe pquantity should be based on the number of objects in the being_type.
    resources.update_one({"_id": being_type}, {"$set":{"pquantity": amount}})
    print "Set Physical Quantity to ", amount

def inc_pquantity(being_type, amount):
    if amount == 0:
        print "Invalid amount"
    else:
        resources.update_one({"_id": being_type)}, {"$inc":{"pquantity": amount}})
        if amount > 0:
            print "Add ", amount, " Physical Quantity"
        else:
            print "Remove", amount, " Physical Quantity"

def set_drate(being_type, amount):
    resources.update_one({"_id": being_type}, {"$set":{"drate": amount}})
    try:
        refresh(being_type)
    except:
        print "error with refresh"
    print "Average Deterioration Rate Changed to ", amount

def set_demand(being_type, amount):
    #this will be tied to being_type
    resources.update_one({"_id": being_type}, {"$set":{"demand": amount}})
    try:
        refresh(being_type)
    except:
        print "error with refresh"
    print "Set Demand to ", amount

def take(agent_id, being_type, quantity):
    #this will take x quantity of being_type and will transfer holding of x quantity resource_ids of being_type
    refresh(being_type)
    result = resources.find_one({"_id": being_type})
    price = result["price"]
    y = agents.find_one({"_id": agent_id})
    balance = y["balance"]
    if balance >= (price * quantity):
        agents.update_one({"_id": agent_id}, {"$inc":{"balance": (price * quantity)}})
        resources.update_one({"_id": being_type}, {"$inc":{"aquantity": -1}})
        resources.update_one({"_id": being_type}, {"$inc":{"uses": quantity}})
        refresh(being_type)
        print agent_id, " took ", quantity, " of ", being_type, " at ", price, "each"
    else:
        print "Insufficient funds for purchase"
        #figure out what do with set holder thing. Is this implied?
        #make sure quantity can not exceed usupply

def give(agent_id, being_type, quantity):
    #make sure he can only give a quantity which he himself has
      # y = agents.find_one({"_id": (agent_id)})
       #balance = y["balance"]
     #  agents.update_one({"_id": (agent_id)}, {"$inc":{"balance": (price * quantity)}})
    resources.update_one({"_id": being_type}, {"$inc":{"aquantity": 1}})
    print agent_id, " gave ", quantity, " of ", being_type, " at ", price, "each"
        #figure out what do with set holder thing. Is this implied? 

def demand(being_type, amount):
    #add support for the demands of agent_id
    #this will be tied to being_type
    resources.update_one({"_id": being_type}, {"$inc":{"demand": amount}})
    if amount > 0:
        print "Add ", amount, " Demand"
    else:
        print "Remove", amount, "Demand"
    try:
        refresh(being_type)
    except:
        print "error"
        #not yet included that the demand is also attributed to the self agent (for priority access)    


# ***************** DEALING WITH OBJECT_ID *****************


def delete_resource(resource_id):
    resources.delete_one({"_id": resource_id})
    #resource_id is the specific object.

def set_owner(resource_id, owner):
        resources.update_one({"_id": resource_id}, {"$set":{"owner": owner}})
        refresh(being_type)
        print "New owner of ", resource_id, " is ", newowner
    #problem with this logic

def set_holder(resource_id, holder):
    resources.update_one({"_id": resource_id}, {"$set":{"holder": holder}})
    refresh(being_type)
    print "New holder of ", resource_id, " is ", holder

init_agent("tom")
set_balance("tom", 100)

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
