#!/usr/bin/env python
import pymongo
from pymongo import MongoClient

cluster = MongoClient()

db = cluster["Beings"]
beings = db["Beings"]

db = cluster["Agents"]
agents = db["Agents"]

db = cluster["Demands"]
demands = db["Demands"]

db = cluster["Objects"]
objects = db["Objects"]

db = cluster["Transactions"]
transactions = db["Transactions"]
#this should pribably just be an ipfs log.

db = cluster["Tasks"]
tasks = db["Tasks"]
#100% consensus to make an entry? (do we add quantity for tasks?) Tasks determined by commune

db = cluster["Currencies"]
currencies = db["Currencies"]

db = cluster["Forex_Prices"]
forex = db["Forex_Prices"]
# being_id and price in various currencies. Set by commune Maybe determined by market in the same way as the drate.

#Temporary part of code
beings.delete_many({})
agents.delete_many({})
demands.delete_many({})
#things r broken down into agent demands and commune demands (commune demamds will let us do token exchane value based on planning euro cost list)
objects.delete_many({})
transactions.delete_many({})
tasks.delete_many({})
forex.delete_many({})
currencies.delete_many({})


# ******************************************
# ***************** AGENTS *****************
# ******************************************

def init_agent(agent_id):
    agentinit = {"_id": agent_id}
    #the id will later be an object id, nothing needed to init
    agents.insert_one(agentinit)

def set_balance(agent_id, amount):
    agents.update_one({"_id": agent_id}, {"$set":{"balance": amount}})
    print("Set Balance")

def inc_balance(agent_id, amount):
    if amount == 0:
        print("invalid amount")
    else:
        agents.update_one({"_id": agent_id}, {"$inc":{"balance": amount}})
        print("Add Balance")

# *********************************************
# ********* DEALING WITH BEING_TYPE ***********
# *********************************************

def new_being(being_type, aquantity, owner, holder):
    if beings.find({"_id": being_type}).count() == 0:
    #aquantity will be later determined post-init by adding a list of all objects.
        beings.insert_one({"_id": being_type})
        beings.update_one({"_id": being_type}, {"$set":{"uses": 0}})
        i = 0
        while i < aquantity:
            objects.insert_one({"being_type": being_type, "owner": owner, "holder": holder})
            i += 1
    else:
        beings.update_one({"_id": being_type}, {"$set":{"uses": 0}})
        i = 0
        while i < aquantity:
            objects.insert_one({"being_type": being_type, "owner": owner, "holder": holder})
            i += 1
    #the way we mean aquantity as it applies to beings is different from how we mean it as we apply it so objects?


def refresh(being_type):
    #remember that availablesupply is a large category and doesnt mean available for the agent
    #fix the program so that the true availability is agent centric and based on whether they demanded or not.
    x = beings.find_one({"_id": being_type})
    aquantity = objects.find({"being_type": being_type, "owner": "commune"}).count()
    try:
        drate = x["drate"]
        pipe = [{'$group': {'_id': being_type, 'total': {'$sum': '$amount'}}}]
        results = demands.aggregate(pipeline=pipe)
        for result in results:
            demand = float(result['total'])
        uses = x["uses"]
        usupply = ((float(aquantity) / float(drate)) - float(uses))
    except:
        print("error fetching requirements for refresh")
            # Used when you want to catalogue an object but declare it as not usable by the public (imagine protecting a tree), or if you have
            # Not catalogued an object but want to make it illegal to use if it is ever found (imagine evasive species which are not catalogued but interaction with them are regulated)
    try:
        if float(usupply) >= float(demand):
            price = 0
        else:
            price = float(usupply) / float(demand)
        beings.update_one({"_id": being_type}, {"$set":{"price": price}})
    except:
        print("error usupply or demand not yet set")

def inc_object(being_type, amount, owner, holder):
    i = 0
    while i < amount:
        objects.insert_one({"being_type": being_type, "owner": owner, "holder": holder})
        i += 1
    refresh(being_type)
    print("Added ", amount, " ", being_type)

def set_pquantity(being_type, amount):
    #maybe pquantity should be based on the number of objects in the being_type.
    beings.update_one({"_id": being_type}, {"$set":{"pquantity": amount}})
    print("Set Physical Quantity to ", amount)

def inc_pquantity(being_type, amount):
    if amount == 0:
        print("Invalid amount")
    else:
        beings.update_one({"_id": being_type}, {"$inc":{"pquantity": amount}})
        if amount > 0:
            print("Add ", amount, " Physical Quantity")
        else:
            print("Remove", amount, " Physical Quantity")

def set_drate(being_type, amount):
    beings.update_one({"_id": being_type}, {"$set":{"drate": amount}})
    try:
        refresh(being_type)
    except:
        print("error with refresh")
    print("Average Deterioration Rate Changed to ", amount)

def take(agent_id, being_type, quantity):
    refresh(being_type)
    result = beings.find_one({"_id": being_type})
    price = result["price"]
    asupply = objects.find({"being_type": being_type, "owner": "commune"}).count() - demands.find({"being_type": being_type, "demander": "commune"}).count()
    #this will change after i add the availability column to the objects database, we will filter simply for available supply
    #might create a negative number: this should trigger unavailability of the being (or objects?) to agents
    y = agents.find_one({"_id": agent_id})
    balance = y["balance"]
    if (balance >= (price * quantity)) and (asupply >= quantity):
        #I think there is a problem with the "and"
        #right now this is usupply >= than quantity but this will change when we make it agent demand specific
        agents.update_one({"_id": agent_id}, {"$inc":{"balance": (price * quantity*(-1))}})
        beings.update_one({"_id": being_type}, {"$inc":{"uses": quantity}})
        i = 0
        while i < quantity:
            objects.update_one({"being_type": being_type, "holder": "commune"}, {"$set":{"holder": agent_id}})
            i += 1
        refresh(being_type)
        print(agent_id, " took ", quantity, " of ", being_type, " at ", price, "each")
    else:
        print("Insufficient funds or asupply for taking")
        #figure out what do with set holder thing. Is this implied?
        #make it so that the take function can transfer to anyone.

def give(agent_id, receiver, being_type, quantity):
    personal_supply = objects.find({"being_type": being_type, "holder": agent_id}).count()
    if personalsupply >= quantity:
    #make sure he can only give a quantity which he himself has
      # y = agents.find_one({"_id": (agent_id)})
       #balance = y["balance"]
     #  agents.update_one({"_id": (agent_id)}, {"$inc":{"balance": (price * quantity)}})
        i = 0
        while i < quantity:
            objects.update_one({"being_type": being_type, "holder": agent_id}, {"$set":{"holder": receiver}})
            i += 1
        #change quantity amount of objects with being_type and holder: "agent_id" to holder: "commune".
        print(agent_id, " gave ", quantity, " of ", being_type, " to ", receiver)
    else:
        print("agent has insufficient supply to give.")

def demand(demander, being_type, amount):
    # demander can be either commune or agent
    if demands.count({"being_type": being_type, "demander": demander}) > 0: 
        demands.update_one({"being_type": being_type, "demander": demander}, {"$inc":{"amount": amount}})
    else:
        demands.insert_one({"being_type": being_type, "demander": demander, "amount": amount})
    if amount > 0:
        print("Add ", amount, " Demand")
    else:
        print("Remove", amount, "Demand")
    try:
        refresh(being_type)
    except:
        print("error")

# **********************************************************
# ***************** DEALING WITH OBJECT_ID *****************
# **********************************************************

def delete_object(resource_id):
    objects.delete_one({"_id": resource_id})
    #resource_id is the specific object.

def set_owner(resource_id, owner):
        beings.update_one({"_id": resource_id}, {"$set":{"owner": owner}})
        refresh(being_type)
        print("New owner of ", resource_id, " is ", newowner)
    #problem with this logic

def set_holder(resource_id, holder):
    beings.update_one({"_id": resource_id}, {"$set":{"holder": holder}})
    refresh(being_type)
    print("New holder of ", resource_id, " is ", holder)

# ***************** DEALING WITH CURRENCIES *****************

def new_currency(currency, amount):
    #this is like communes money account
    currencies.insert_one({"_id": currency, "amount": amount})

def inc_currency(currency, amount):
    currencies.update_one({"_id": currency}, {"$inc":{"amount": amount}})

def fetch_moneysupply(currency):
    x = currencies.find_one({"_id": currency})
    moneysupply = float(x["amount"])
    print(moneysupply, " ", currency)
    return moneysupply
        

# ***************** DEALING WITH FOREX *****************
def set_forex_price(being_type, currency, amount):
    if forex.find({}).count() == 0:
        forex.insert_one({"_id": being_type})
        forex.update_one({"_id": being_type}, {"$set":{"amount": amount, "currency": currency}})
    else:
        forex.update_one({"_id": being_type}, {"$set":{"amount": amount, "currency": currency}})

init_agent("tom")
init_agent("luc")
set_balance("tom", 100)
set_balance("luc", 100)

new_being("apple", 2, "commune", "commune")
new_being("apple", 2, "commune", "commune")
new_currency("euros", 50)
set_forex_price("apple", "euros", 5)

set_drate("apple", 0.5)
demand("tom", "apple", 3)
demand("luc", "apple", 3)
demand("commune", "apple", 2)
demand("commune", "bannana", 5)

take("tom", "apple", 2)
take("luc", "apple", 1)

print(" ")
print("----------- AGENTS -----------")
agentsresults = agents.find({})
for x in agentsresults:
    print(x)

print(" ")
print("----------- BEINGS -----------")
beingsresults = beings.find({})
for x in beingsresults:
    print(x)

print(" ")
print("----------- OBJECTS -----------")
objectsresults = objects.find({})
for x in objectsresults:
    print(x)

print(" ")
print("----------- DEMANDS -----------")
demandsresults = demands.find({})
for x in demandsresults:
    print(x)

print(" ")
print("--------- FOREX PRICES --------")
forexresults = forex.find({})
for x in forexresults:
    print(x)

print(" ")
print("--------- CURRENCIES --------")
forexresults = forex.find({})
for x in forexresults:
    print(x)

#def moneyconversion():

#y = demands.find({"demander": "commune"})
#def fetch_moneydemand():
 #   pipe = [{'$group': {"_id": "demander": "commune"}, 'total': {'$sum': '$amount'}}]
  #  x = demands.aggregate(pipeline=pipe)
   # for y in x:
    #    print(y["total"])
    #return y
#fetch_moneydemand()
#fetch_moneysupply("euros")

#if moneysupply > moneydemand:
 #   tokenspereuro = 0
#else:
 #   tokenspereuro = moneysupply / moneydemand