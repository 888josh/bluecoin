from blueCoin import *
import json
from time import time
import pprint

pp = pprint.PrettyPrinter(indent=4)

testChain = BlockChain()


pp.pprint(testChain.chainJSONencode())
print("Length: " + str(len(testChain.chain)))


print(testChain.verifyBlockchain())