from app import mysql, session
from blueCoin import BlockChain, blueCoin, Transaction

class Table():
    def __init__(self,table_name, *args):

        self.table = table_name
        self.columns =  "(%s)" %",".join(args) #(join function for any length of arguments)
        self.columnsList = args

        if isnewtable(self.table):
            create_data = ""
            for column in self.columnsList:
                create_data += "%s varchar(100)," %column

            cur = mysql.connection.cursor() #create the table
            cur.execute("CREATE TABLE %s(%s)" %(self.table, create_data[:len(create_data)-1]))
            cur.close()

    def getall(self): #returns all values from the table
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM %s" %self.table)
        data = cur.fetchall()
        cur.close(); return data


    def getone(self, search, value): #obtain a single row from a table based on column data
        data = {}; cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM %s WHERE %s = \"%s\"" %(self.table,search,value))
        if result > 0: data = cur.fetchone()
        cur.close(); return data

    def deleteone(self, search, value): #remove a single row from the table
        cur = mysql.connection.cursor()
        cur.execute("DELETE from %s WHERE %s = \"%s\"" %(self.table,search,value))
        mysql.conncetion.commit()
        cur.close() 
         
    def deleteall(self):
        self.drop()
        self.__init__(self.table, *self.columns)

    def drop(self):
        cur = mysql.connection.cursor()
        cur.execute("DROP TABLE %s" %(self.table))
        cur.close()


    def insert(self, *args):
        data = ""
        for arg in args: #convert data into string mysql format
            data += "\"%s\"," %(arg)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO %s%s VALUES(%s)" %(self.table, self.columns, data[:len(data)-1]))
        mysql.connection.commit()
        cur.close()
        
def isnewuser(username):
    #access the users table and get all values from column "username"
    users = Table("users", "name", "email", "username", "password")
    data = users.getall()
    usernames = [user.get('username') for user in data]

    return False if username in usernames else True
    

def sql_raw(execution): #a generic method for executing raw SQL queries.
    cur = mysql.connetion.cursor()
    cur.execute(execution)
    mysql.connection.commit()
    cur.close()

def isnewtable(table_name):
    cur = mysql.connection.cursor()
    try:
        cur.execute('SELECT * FROM %s' %table_name)
        cur.close()
    except:
        return True
    else:
        return False

#methods related to the blockchain itself.

def get_blockchain(): #blockchain constructor in sql 

    blockchain = BlockChain()

    #each block stores a list of transactions, which must be initialized uniquely aswell.

    blockchain_sql = Table('blockchain', 'index', 'transactions', 'time', 'prev', 'nonce')
    for block in blockchain_sql.getall():
        transactions = []
        transaction_sql = Table('transactions', 'sender', 'receiver', 'amount', 'time', 'hash')

        thisList = block.get('transactions') #this should return the table of transactions for eachblock stored in sql within the blockchain table
        for entry in thisList:
            appendTransaction = Transaction(thisList.get('sender'), thisList.get('receiver'), thisList.get('amount'))
            transactions.append(appendTransaction)



        blockchain.addBlock(int(block.get('index')), transactions, block.get('time'), block.get('prev'), block.get('nonce'))

    return blockchain


def sync_blockchain(blockchain):

    blockchain_sql = Table('blockchain', 'index', 'transactions', 'time', 'prev', 'nonce')
    blockchain_sql.deleteall()


    return



    