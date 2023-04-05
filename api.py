from flask import Flask, request, jsonify, redirect, render_template
from flask_restful import Api, Resource, reqparse
import watchdog
from neo4j import GraphDatabase
import csv
import json

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if self.driver is not None:
            self.driver.close()

# Метод, который передает запрос в БД и возвращает данные в виде json
    def query_json(self, query_json, parametrs, db=None):
        assert self.driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.driver.session(database=db) if db is not None else self.driver.session()
            response = session.run(query_json, parametrs)
            data = response.data()
            data = json.dumps(data, ensure_ascii=False)
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return data

with open('entrance.txt','r') as ent:
    data = ent.read().split(',')

uri_my = eval(data[0].split('=')[1])
user_my = eval(data[1].split('=')[1])
password_my = eval(data[2].split('=')[1])


conn = Neo4jConnection(uri=uri_my, user=user_my, password=password_my)


api=Flask(__name__)


@api.route("/info_part/<name>", methods=['GET'])
def infor_node_partisipate(name):
    query ='''
    MATCH (member1:Member{fullname:$name})-->(event:Event)<--(member2:Member)
    RETURN member1.fullname AS Member1, member2.fullname AS Member2, event.idEvent AS idEvent;
    '''
    parametrs = {"name":name}
    data_info_part = conn.query_json(query, parametrs, db='graphdb')
    return data_info_part



@api.route("/info/<name>", methods=['GET'])
def info_node(name):
    query ='''
    MATCH (member:Member{fullname:$name})-[:PARTICIPATE]->(event:Event)
    WITH member,collect(event.idEvent) as idEvent,count(*) as total
    RETURN member.fullname AS Member, idEvent, total;
    '''
    parametrs = {"name":name}
    data_info = conn.query_json(query, parametrs, db='graphdb')
    return data_info

if __name__=="__main__":
    api.run(port=5050, host="127.0.0.1")