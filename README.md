# ihmp_portal_api

The `ihmp_porta_api` is built to work in conjunction with the [iHMP data portal UI]( https://github.com/jmatsumura/portal-ui). It is a Flask app that uses GraphQL to communicate with a Neo4j database in order to efficiently retrieve and transfer the data in a RESTful manner. 

Setup:
1. First, make sure all dependencies are installed and start Neo4j
2. Request an account to access [OSDF](http://osdf.igs.umaryland.edu/)
3. Use the [loader](https://github.com/jmatsumura/iHMPDCC_new_fxns/blob/master/OSDF_to_Neo4j/couchdb2neo4j_with_tags.py) to move the data from CouchDB to Neo4j
 * Make sure your Neo4j server is started and open on the default ports (7474)
 * `python couchdb2neo4j_with_tags.py --db <OSDF_URL> --neo4j_password <NEO4J_PASS>`
4. Start your Flask app (may want to modify `conf.py` before doing this):
 * `python app.py`
5. Can now interact with the GQL at any of end the endpoints noted at the bottom of `app.py` or install your own [local portal UI]( https://github.com/jmatsumura/portal-ui)

Dependencies:
* [Neo4j 3.0.0](https://neo4j.com/release-notes/neo4j-3-0-0/)
* [Python 2.7.10](https://www.python.org/downloads/release/python-2710/)
  * [Flask](http://flask.pocoo.org/docs/0.12/installation/)
  * [graphene](http://docs.graphene-python.org/en/latest/quickstart/)
  * [py2neo](http://py2neo.org/v3/)
