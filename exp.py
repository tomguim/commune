#!/usr/bin/env python
import pymongo
from pymongo import MongoClient
cluster = MongoClient()

db = cluster["Beings"]
beings = db["Beings"]
#Beings

db = cluster["Agents"]
agents = db["Agents"]

db = cluster["Demands"]
demands = db["Demands"]

db = cluster["Objects"]
objects = db["Objects"]

#Temporary part of code
beings.delete_many({})
agents.delete_many({})
demands.delete_many({})
#things r broken down into agent demands and commune demands (commune demamds will let us do token exchane value based on planning euro cost list)
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
# ***************** beings *****************
# *********************************************

# ********* DEALING WITH BEING_TYPE ***********

def new_being(being_type, aquantity, owner, holder):
    #aquantity will be later determined post-init by adding a list of all objects.
    beinginit = {"_id": being_type}
    beings.insert_one(beinginit)
    #the way we mean aquantity as it applies to beings is different from how we mean it as we apply it so objects?
    
    i = 0
    while i < aquantity:
        objects.insert_one({"being_type": being_type, "owner": owner, "holder": holder})
        i += 1

def refresh(being_type):
    #remember that availablesupply is a large category and doesnt mean available for the agent
    #fix the program so that the true availability is agent centric and based on whether they demanded or not.
    x = beings.find_one({"_id": being_type})
    aquantity = objects.find({"being_type": being_type, "owner": "commune"}).count()
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
    beings.update_one({"_id": being_type}, {"$set":{"usupply": usupply}})
    if float(usupply) >= float(demand):
        price = 0
    else:
        price = float(usupply) / float(demand)
    beings.update_one({"_id": being_type}, {"$set":{"price": price}})

def inc_object(being_type, amount, owner, holder):
    i = 0
    while i < amount:
        objects.insert_one({"being_type": being_type, "owner": owner, "holder": holder})
        i += 1
    refresh(being_type)
    print "Added ", amount, " ", being_type

def set_pquantity(being_type, amount):
    #maybe pquantity should be based on the number of objects in the being_type.
    beings.update_one({"_id": being_type}, {"$set":{"pquantity": amount}})
    print "Set Physical Quantity to ", amount

def inc_pquantity(being_type, amount):
    if amount == 0:
        print "Invalid amount"
    else:
        beings.update_one({"_id": being_type}, {"$inc":{"pquantity": amount}})
        if amount > 0:
            print "Add ", amount, " Physical Quantity"
        else:
            print "Remove", amount, " Physical Quantity"

def set_drate(being_type, amount):
    beings.update_one({"_id": being_type}, {"$set":{"drate": amount}})
    try:
        refresh(being_type)
    except:
        print "error with refresh"
    print "Average Deterioration Rate Changed to ", amount

def set_demand(being_type, amount):
    #this will be tied to being_type
    beings.update_one({"_id": being_type}, {"$set":{"demand": amount}})
    try:
        refresh(being_type)
    except:
        print "error with refresh"
    print "Set Demand to ", amount

def take(agent_id, being_type, quantity):
    #this will take x quantity of being_type and will transfer holding of x quantity resource_ids of being_type
    refresh(being_type)
    result = beings.find_one({"_id": being_type})
    price = result["price"]
    y = agents.find_one({"_id": agent_id})
    balance = y["balance"]
    if balance >= (price * quantity):
        agents.update_one({"_id": agent_id}, {"$inc":{"balance": (price * quantity)}})
        #fix this
        beings.update_one({"_id": being_type}, {"$inc":{"uses": quantity}})
        i = 0
        while i < quantity:
            objects.update_one({"being_type": being_type, "holder": "commune"}, {"$set":{"holder": agent_id}})
            i += 1
        refresh(being_type)
        print agent_id, " took ", quantity, " of ", being_type, " at ", price, "each"
    else:
        print "Insufficient funds for purchase"
        #figure out what do with set holder thing. Is this implied?
        #make sure quantity can not exceed usupply

def give_to_commune(agent_id, receiver, being_type, quantity):
    #make sure he can only give a quantity which he himself has
      # y = agents.find_one({"_id": (agent_id)})
       #balance = y["balance"]
     #  agents.update_one({"_id": (agent_id)}, {"$inc":{"balance": (price * quantity)}})
    i = 0
    while i < quantity:
        objects.update_one({"being_type": being_type, "holder": agent_id}, {"$set":{"holder": receiver}})
        i += 1
    #change quantity amount of objects with being_type and holder: "agent_id" to holder: "commune".
    print agent_id, " gave ", quantity, " of ", being_type
        #figure out what do with set holder thing. Is this implied?

def demand(being_type, amount):
    #add support for the demands of agent_id
    #this will be tied to being_type
    beings.update_one({"_id": being_type}, {"$inc":{"demand": amount}})
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
    objects.delete_one({"_id": resource_id})
    #resource_id is the specific object.

def set_owner(resource_id, owner):
        beings.update_one({"_id": resource_id}, {"$set":{"owner": owner}})
        refresh(being_type)
        print "New owner of ", resource_id, " is ", newowner
    #problem with this logic

def set_holder(resource_id, holder):
    beings.update_one({"_id": resource_id}, {"$set":{"holder": holder}})
    refresh(being_type)
    print "New holder of ", resource_id, " is ", holder


init_agent("tom")
set_balance("tom", 100)

new_being("apple", 5, "commune", "commune")

set_drate("apple", 0.5)
set_demand("apple", 1000)

take("tom", "apple", 2)


agentsresults = agents.find({})
for x in agentsresults:
    print(x)

beingsresults = beings.find({})
for x in beingsresults:
    print(x)

objectsresults = objects.find({})
for x in objectsresults:
    print(x)