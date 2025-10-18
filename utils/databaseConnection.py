import neo4j
from neo4j import GraphDatabase

"""
used to connect to the database with uri,username,password @Y22CS191 Vemuri Sasi Vardhan

"""

class graphDB:
    def __init__(self,uri,username="neo4j",password="RVR#1985"):
        self.uname=username
        self.password=password
        self.uri=uri
    def connect(self):
        Auth=   (self.uname,self.password)
        try:
            with GraphDatabase.driver(self.uri,auth=Auth) as driver:
                driver.verify_connectivity()
                print("Driver is Connected")
                return driver
        except:
            print("Error while connecting to the database")

           

if(__name__ == "__main__"):
    dbO=graphDB("neo4j://127.0.0.1:7687","neo4j","RVR#1985")
    dbO.connect()