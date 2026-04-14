import os
from neo4j import GraphDatabase

URI = os.getenv("neo4j://127.0.0.1:7687")
USERNAME = os.getenv("neo4j")
PASSWORD = os.getenv("P@$$w0rd")


class Neo4jDB:
    def __init__(self):
        self.driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

    def close(self):
        self.driver.close()

    def run_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]


db = Neo4jDB()