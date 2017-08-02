# HMP Portal API

## Overview

This API` is built to work in conjunction with the [HMP data portal UI]( https://github.com/jmatsumura/portal-ui). The API is a Flask app which uses GraphQL to communicate with a Neo4j database in order to efficiently retrieve and transfer the data in a RESTful manner. 

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

## Advanced Search

`Advanced Search` is meant to be similar to how one would query a database directly. Each query requires the following general format:
```
(property) (comparison operator) (value)
```
The `property` is what you want to search on. The `comparison operator` is how you want to relate your `value` to your property. Your `value` is what you want to subset your `property` by. 

For example:
```
project.name = "Human Microbiome Project (HMP)"
```
The results of this query will be only those samples and files that are associated with the project name "Human Microbiome Project (HMP)". 

Try type this query in the interface and observe how auto-complete helps along the way. Auto-complete should be used for every query as it pulls directly from the database and makes sure you are searching by a valid `property`, `comparison operator`, and `value`. Thus, if you use auto-complete and find no results in your query, you know you have entered combinations of `property`+`comparison operator`+`value` which do not exist.

### Available Properties

The list of properties available to search on is actively growing. Below you can find the name+description for those which are currently available.

* "file.format" - The format of the file
* "file.id" - The iHMP ID of the file
* "file.type" - The node type of the file
* "project.name" - The name of the project within which the sequencing was organized
* "project.subtype" - The subtype of the project
* "sample.biome" - Biomes are defined based on factors such as plant structures, leaf types, plant spacing, and other factors like climate
* "sample.body_product" - Substance produced by the body, e.g. stool, mucus, where the sample was obtained from
* "sample.body_site" - Body site from which the sample was obtained using the FMA ontology
* "sample.collection_date" - The time of sampling, either as an instance (single point in time) or interval
* "sample.env_package" - Controlled vocabulary of MIGS/MIMS environmental packages
* "sample.feature" - Environmental feature level includes geographic environmental features
* "sample.geo_loc_name" - The geographical origin of the sample as defined by the country or sea name followed by specific region name
* "sample.id" - The iHMP ID of the sample
* "sample.lat_lon" - Latitude/longitude in WGS 84 coordinates
* "sample.material" - Matter that was displaced by the sample, before the sampling event
* "sample.project_name" - Name of the project within which the sequencing was organized
* "sample.rel_to_oxygen" - Whether the organism is an aerobe or anaerobe
* "sample.samp_collect_device" - The method or device employed for collecting the sample
* "sample.samp_mat_process" - Any processing applied to the sample during or after retrieving the sample from environment
* "sample.size" - Amount or size of sample (volume, mass or area) that was collected
* "sample.subtype" - The subtype of the sample
* "sample.supersite" - Body supersite from which the sample was obtained
* "study.center" - The study's sequencing center
* "study.contact" - The study's primary contact at the sequencing center
* "study.description" - A longer description of the study
* "study.name" - The name of the study
* "study.srp_id" - NCBI Sequence Read Archive (SRA) project ID
* "study.subtype" - The subtype of the study
* "subject.gender" - The subject's sex
* "subject.id" - The subject's per-study ID (can view in individual sample page)
* "subject.race" - The subject's race/ethnicity
* "subject.subtype" - The subtype of the subject
* "subject.uuid" - The subject's UUID
* "tag" - Tag word attached to the file
* "visit.date" - Date when the visit occurred
* "visit.id" - The identifier used by the sequence center to uniquely identify the visit
* "visit.interval" - The amount of time since the last visit (in days)
* "visit.number" - A sequential number that is assigned as visits occur for a subject
* "visit.subtype" - The subtype of the visit
