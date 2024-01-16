from datetime import datetime
import numpy as np
import hashlib
import json
from time import time
from Crypto.Hash import SHA3_256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Signature import *

class blueCoin:

    def __init__(self,transactions,time,index):
        self.index = index
        self.transactions = transactions #pass a list of transactions
        self.time = time
        self.prev = ''
        self.nonce = 0
        #self.difficulty = 4
        
        #self.hash=self.calculateHash()? lmao make sure this comes after you have defined all the attributes...

    def calculateHash(self):
        hashTransactions = ''
        for i in self.transactions:
            hashTransactions += i.hash

        #maybe an issue with what i'm passing into bluecoin, list of lists?
        #AttributeError: 'list' object has no attribute 'hash'

        currNonce = str(self.nonce)
        currTime = str(self.time)
        prevHash = self.prev

        hashString = currTime + hashTransactions + prevHash + currNonce

        hashEncoded = json.dumps(hashString, sort_keys=True).encode()
        return hashlib.sha3_256(hashEncoded).hexdigest()


    def mineBlock(self,difficulty): #iterate nonce to find correct value for hash puzzle difficulty string
        #with proof-of-work, hashing the entire block header
        difficultyString = ''
        for i in range(1,difficulty+1):
            difficultyString += '0' #pattern = 000...difficulty

        while self.calculateHash()[0:difficulty] != difficultyString:
            print('nonce: ' + str(self.nonce))
            print('hash attempt: ' + self.calculateHash())
            print('hash puzzle: ' + difficultyString)
            self.nonce += 1
            self.hash = self.calculateHash() #defining the block's correct hash w/ matching pattern

        print('final hash: ' + self.calculateHash())
        print('Nonce needed to solve Proof of Work: ' + str(self.nonce))

        return True

        
class BlockChain:
    def __init__(self):
        self.chain = [self.genesis()] #list of block objects
        self.pendingTransactions = [] #queue of transactions to be verified 
        self.difficulty  = 3
        self.maxBlock = 3 #the number of transactions to be mined (at a time) per block...
        self.reward = 10
    
    def addBlock(self,block):
        if(len(self.chain)>0):
            block.prev=self.getLastBlock().hash
        else:
            block.prev="none"

        self.chain.append(block)

    #method untested.
    def addTransaction(self, receiverPubKey, amount, keyString, senderKey): #need to sign transaction w/ senderkey,
        keyByte = keyString.encode('ASCII')
        senderKeyByte = senderKey.encode('ASCII')
        #A public key is exported into a binary format, but often we require to send it in an ASCII way.
        key = RSA.import_key(keyByte)
        senderKey = RSA.import_key(senderKeyByte)
        #converting the keystrings into bytes.

        newTransaction = Transaction(senderKey,receiverPubKey, amount)
        newTransaction.signTransaction()
        self.pendingTransactions.append(newTransaction)

        return 


    def minePending(self,miner):
        lenPT = len(self.pendingTransactions)
        if(lenPT < 1):
            print("not enough transactions.")
            return False
        else:
            for block in range(0,lenPT, self.maxBlock):

                endIndex = block + self.maxBlock
                if(endIndex >= lenPT):
                    end = lenPT #numpy excludes the end index when slicing...
                transactionSlice = self.pendingTransactions[block:end] 

                #the above code defines a slice of transactions to be included in a new block before calculating their hash
                #the loop processes all transactions placing their increments into blocks, adjusting if the final chunk of transactions is less than blocksize.
                #recall range(start,stop,step)
                
                addBlock = blueCoin(transactionSlice, datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),len(self.chain)) #(list,string date, integer index)
                prevHash = self.getLastBlock().hash
                addBlock.prev = prevHash
                addBlock.mineBlock(self.difficulty)
                self.chain.append(addBlock)
            print("Finished Mining Transactions")
            
            #self.chain[0].nonce = 0 test the verifyBlockchain here

            rewardTransaction = Transaction("miner Rewards", miner, self.reward)
            self.pendingTransactions = [rewardTransaction]

        return True
        
    def genesis(self):

        tArr = [] #the transactions which block 0 has undergone
        genesis_date = datetime(2004, 6, 13, 0, 0, 0).strftime("%m/%d/%Y, %H:%M:%S")
        genesis_block = blueCoin(tArr, genesis_date, 0)
        genesis_block.prev = 'none, (this is block0)'


        # why am i unable to access self.difficulty

        genesis_block.mineBlock(3)

        return genesis_block

    def getLastBlock(self):
        return self.chain[-1]


    def chainJSONencode(self):
        blockArrJSON = []

        for block in self.chain:
            blockJSON = {}
            blockJSON['index'] = block.index
            blockJSON['time'] = block.time
            blockJSON['prev'] = block.prev
            blockJSON['nonce'] = block.nonce
            blockJSON['hash'] = block.hash

            transactionsJSON = []
            tJSON = {}
            for transaction in block.transactions:
                tJSON['sender'] = transaction.sender
                tJSON['receiver'] = transaction.receiver
                tJSON['time'] = transaction.time
                tJSON['amount'] = transaction.amount
                tJSON['hash'] = transaction.hash
                #technically list transaction.data here...
            blockJSON['transactions'] = transactionsJSON
            
            blockArrJSON.append(blockJSON)

        return blockArrJSON

    def chainJSONdecode(self, chainJSON):
        chain=[]
        for blockJSON in chainJSON:

            tArr = []
            for tJSON in blockJSON['transactions']:
                transaction = Transaction(tJSON['sender'], tJSON['reciever'], tJSON['amt'])
                transaction.time = tJSON['time']
                transaction.hash = tJSON['hash']
                tArr.append(transaction)
                    
            block = blueCoin(tArr, blockJSON['time'], blockJSON['index'])
            block.hash = blockJSON['hash']
            block.prev =blockJSON['prev']
            block.nonse = blockJSON['nonse']
            block.gym = blockJSON['gym']

            chain.append(block)
        return chain
    
    def verifyBlockchain(self):

        for i in range(1,len(self.chain)):
            givenPrevious = self.chain[i].prev
            compare = self.chain[i-1].calculateHash()

            if self.difficulty * '0' != compare[0:self.difficulty] and compare != givenPrevious:
                return False
            
            return True

    def generateKeys(self):

        key = RSA.generate(2048)
        private_key = key.export_key()
        file_out = open("private.pem", "wb")
        file_out.write(private_key)

        public_key = key.publickey().export_key()
        file_out = open("receiver.pem", "wb")
        file_out.write(public_key)
        
        print(public_key.decode('ASCII'))
        return key.publickey().export_key().decode('ASCII')

        

class Transaction():
    #each transaction needs to be signed 
    def __init__(self, senderKey, receiverKey, amount, time): 
        self.sender = senderKey
        self.receiver = receiverKey
        self.time = time #how do i set the time so that it can only be initialized once?
        self.amount = amount
        #self.data = data a string to summarize the transaction

        self.hash = self.hashTransaction()

    def hashTransaction(self):
        stringToHash = self.sender + self.receiver + str(self.time) + str(self.amount)
        encodedStr = json.dumps(stringToHash, sort_keys=True).encode()
        return hashlib.md5(encodedStr).hexdigest()

    def signTransaction(self, key, senderKey):
        if(self.hash != self.hashTransaction()):
            print('error: transaction tampered')
            return False
        if(str(key.publickey().export_key()) != str(senderKey.publickey().export_key())):
            print('error: attempt to sign transaction from incorrect wallet')
            return False

        pkcs1_15.new(key)
        self.signature = 'made'
        print('Transaction successfully signed.')
        return True


        
