# Human Microbiome Project (HMP) Portal API

* [Overview](https://github.com/jmatsumura/ihmp_portal_api#overview)
  * [Setup](https://github.com/jmatsumura/ihmp_portal_api#setup)
  * [Dependencies](https://github.com/jmatsumura/ihmp_portal_api#dependencies)
* [Searching](https://github.com/jmatsumura/ihmp_portal_api#searching)
  * [Facet Search](https://github.com/jmatsumura/ihmp_portal_api#facet-search)
  * [Advanced Search](https://github.com/jmatsumura/ihmp_portal_api#advanced-search)
  * [Available Properties](https://github.com/jmatsumura/ihmp_portal_api#available-properties)
  * [Controlled Vocabulary](https://github.com/jmatsumura/ihmp_portal_api#controlled-vocabulary)
* [Cart Metadata](https://github.com/jmatsumura/ihmp_portal_api#cart-metadata)

## Overview

* This API is built to work in conjunction with the [HMP data portal UI]( https://github.com/jmatsumura/portal-ui). 
* [Short walkthrough](https://www.youtube.com/watch?v=hbSUBr8yWNY) of how to navigate the UI once linked to the API.
* The API is a Flask app which uses [GraphQL](http://graphql.org/) to communicate with a [Neo4j](https://neo4j.com/) database in order to efficiently retrieve and transfer the data in a RESTful manner. 

### Setup
1. First, make sure all dependencies are installed and start Neo4j
2. Request an account to access [OSDF](http://osdf.igs.umaryland.edu/)
3. Use the [loader](https://github.com/jmatsumura/iHMPDCC_new_fxns/blob/master/OSDF_to_Neo4j/couchdb2neo4j_with_tags.py) to move the data from CouchDB to Neo4j
 * Make sure your Neo4j server is started and available
 * `python couchdb2neo4j_with_tags.py --db <OSDF_URL> --neo4j_password <NEO4J_PASS>`
4. Start your Flask app (must create a `conf.py` before doing this):
 * `conf.py` requires:
   * app_root - the path to the location of this repository
   * access_origin - a list of origins to accept requests from
   * be_port - the port to run this API on
   * be_loc - the IP:PORT that the API is accessible on 
   * secret_key - a complex and private string for Flask to sign sessions/cookies with
   * neo4j_ip - IP of where Neo4j is running
   * neo4j_bolt - port for Neo4j bolt connection
   * neo4j_http - port for Neo4j http connection
   * neo4j_un - username to access Neo4j database
   * neo4j_pw - password to access Neo4j database
     * An additional MySQL conf is needed under the `./lib/` directory if logins are to be supported, fill with dummy values if logging in is not required
   * mysql_h - host of the MySQL **authentication database**
   * mysql_db - name of the DB that houses the username+password rows
   * mysql_un - username to access this MySQL database
   * mysql_pw - password to access this MySQL database
     * An additional set of the same parameters but for a database which will store session/query history information
   * mysql_h_2 - host of the MySQL **session/query database**
   * mysql_db_2 - name of the DB that houses the session/query information
   * mysql_un_2 - username to access this MySQL database
   * mysql_pw_2 - password to access this MySQL database
 * Once `conf.py` is made, use the command `python app.py`
5. Can now interact with the GQL at any of the following endpoints or setup your own [portal UI]( https://github.com/jmatsumura/portal-ui)
 * `/sum_schema`
 * `/ac_schema`
 * `/files_schema`
 * `/table_schema`
 * `/indiv_files_schema`
 * `/indiv_sample_schema`

### Dependencies
* [Neo4j 3.0.0](https://neo4j.com/release-notes/neo4j-3-0-0/)
* [Python 2.7.10](https://www.python.org/downloads/release/python-2710/)
  * [Flask](http://flask.pocoo.org/docs/0.12/installation/)
  * [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/)
  * [graphene](http://docs.graphene-python.org/en/latest/quickstart/)
  * [py2neo](http://py2neo.org/v3/)
  * [MySQL connector](https://dev.mysql.com/doc/connector-python/en/connector-python-installation.html)

## Searching

The HMP portal offers two methods for searching the data: [facet search](https://github.com/jmatsumura/ihmp_portal_api#facet-search) and [advanced search](https://github.com/jmatsumura/ihmp_portal_api#advanced-search).

### Facet Search

`Facet Search` enables one to search for data entirely through clicking. Clicking a slice of a pie chart or a checkbox within the panel on the left will subset the data by the selected property+value combination. Additional properties can be added to subset by via the "Add a filter" option towards the top-right of the panel on the left. Selecting a new property here will add a new set of values to the panel on the left that one can interact with to filter the data by. Facet search builds by inclusion of a particular property+value combination, in order to efficiently perform an exclusive search (e.g. looking for all data **not** associated with a particular property+value combination) it is recommended to use `Advanced Search`.

### Advanced Search

`Advanced Search` is meant to be similar to how one would query a database directly. Each query requires the following general format:
```
(property) (comparison operator) (value)
```
The `property` is what you want to search on. The `comparison operator` is how you want to relate your `value` to your `property`. Your `value` is what you want to subset your `property` by. 

For example:
```
project.name = "Human Microbiome Project (HMP)"
```
The results of this query will be only those samples and files that are associated with the project name "Human Microbiome Project (HMP)". 

Try type this query in the interface and observe how auto-complete helps along the way. Auto-complete should be used for every query as it pulls directly from the database and makes sure you are searching by a valid `property`, `comparison operator`, and `value`. Thus, if you use auto-complete and find no results in your query, you know you have entered combinations of `property`+`comparison operator`+`value` which do not exist. It is also helpful to navigate through the `value`s found as this consists of all the values that currently exist in the database for that particular `property`. 

### Available Properties

The list of properties available to search on is actively growing. Below you can find the name+description for those which will eventually be searchable.

* **file_annotation_pipeline** - The annotation pipeline used to generate the file
* **file_format** - The format of the file
* **file_id** - The iHMP ID of the file
* **file_matrix_type** - The type of data used to generate the abundance matrix
* **file_type** - The node type of the file
* **project_name** - The name of the project within which the sequencing was organized
* **project_subtype** - The subtype of the project
* **sample_biome** - Biomes are defined based on factors such as plant structures, leaf types, plant spacing, and other factors like climate
* **sample_body_product** - Substance produced by the body, e.g. stool, mucus, where the sample was obtained from
* **sample_body_site** - Body site from which the sample was obtained using the FMA ontology
* **sample_collection_date** - The time of sampling, either as an instance (single point in time) or interval
* **sample_env_package** - Controlled vocabulary of MIGS/MIMS environmental packages
* **sample_feature** - Environmental feature level includes geographic environmental features
* **sample_fecalcal** - FecalCal result, exists if measured for the sample
* **sample_geo_loc_name** - The geographical origin of the sample as defined by the country or sea name followed by specific region name
* **sample_id** - The iHMP ID of the sample
* **sample_lat_lon** - Latitude/longitude in WGS 84 coordinates
* **sample_material** - Matter that was displaced by the sample, before the sampling event
* **sample_rel_to_oxygen** - Whether the organism is an aerobe or anaerobe
* **sample_samp_collect_device** - The method or device employed for collecting the sample
* **sample_samp_mat_process** - Any processing applied to the sample during or after retrieving the sample from environment
* **sample_samp_size** - Amount or size of sample (volume, mass or area) that was collected
* **sample_subtype** - The subtype of the sample
* **sample_supersite** - Body supersite from which the sample was obtained
* **study_center** - The study's sequencing center
* **study_contact** - The study's primary contact at the sequencing center
* **study_description** - A longer description of the study
* **study_name** - The name of the study
* **study_srp_id** - NCBI Sequence Read Archive (SRA) project ID
* **study_subtype** - The subtype of the study
* **subject_aerobics** - What is patient's baseline aerobic exercise level; type, minutes/week
* **subject_alcohol** - What is patient's baseline alcohol consumption; type, drinks/week
* **subject_allergies** - Does patient have allergies?
* **subject_asthma** - Does patient have asthma? Yes/No, duration
* **subject_cad** - Does patient have coronary artery disease/myocardial infarction? Yes/No, duration
* **subject_chf** - Does patient have chronic heart failure? Yes/No, duration
* **subject_comment** - Free-text comment
* **subject_contact** - Does patient agree to be contacted in the future?
* **subject_diabetes** - Does patient have diabetes (including gestational)? Yes/No, duration
* **subject_education** - Subject's highest level of education
* **subject_family_history** - Family history of hereditary diseases or physiological conditions
* **subject_father** - Any heritable diseases that the father had
* **subject_gallbladder** - Does patient have gallbladder disease? Yes/No, duration, clarification
* **subject_gender** - The subject's sex
* **subject_hyperlipidemia** - Does patient have hyperlipidemia? Yes/No, duration
* **subject_hypertension** - Does patient have hypertension? Yes/No, duration
* **subject_id** - The subject's per-study ID (can view in individual sample page)
* **subject_illicit_drug** - What is patient's baseline illicit drug history?
* **subject_kidney** - Does patient have kidney disease? Yes/No, duration
* **subject_liver** - Does patient have liver disease? Yes/No, duration, clarification
* **subject_lmp** - When was patient's last menstrual period, if applicable
* **subject_mother** - Any heritable diseases that the mother had
* **subject_occupation** - Subject's occupation
* **subject_osa** - Does patient have obstructive sleep apnea? Yes/No, duration
* **subject_pancreatitis** - Does patient have pancreatitis? Yes/No, duration
* **subject_postmenopausal** - Is patient postmenopausal? Yes/No, duration
* **subject_pvd** - Does patient have peripheral vascular disease? Yes/No, duration
* **subject_race** - The subject's race/ethnicity
* **subject_rx** - List all prescriptions and over the counter medication patient is taking at start of study
* **subject_subtype** - The subtype of the subject
* **subject_survey_id** - Center specific survey identifier
* **subject_tobacco** - What is patient's baseline tobacco use, measured as number of packs per day x years smoked
* **subject_uuid** - The subject's UUID
* **tag** - Tag word attached to the file
* **visit_30m_gluc** - Glucose level 30 minutes after eating.
* **visit_60m_gluc** - Glucose level 60 minutes after eating.
* **visit_abdominal_pain** - Is patient currently suffering from abdominal pain?
* **visit_abx** - In past two weeks, has patient received antibiotics?
* **visit_activity_30d** - Activity level over the last 30 days?
* **visit_activity_3m** - Activity level over the last 3 months?
* **visit_activity_change_30d** - If activity level has changed over the last 30 days, please specify what is different?
* **visit_activity_change_3m** - If activity level has changed over the last 3 months, please specify what is different?
* **visit_acute_dis** - Has patient suffered from an acute disease? If YES, provide details (e.g. I had a cold on 01/02/2012 and recovered on 01/
07/2012; I received a heart surgery on 02/12/2012).
* **visit_age** - Patient age at time of visit
* **visit_alcohol** - Do you drink alcohol?
* **visit_anger** - In the past month, how often has patient been angered because of things that were outside of their control?
* **visit_arthralgia** - In the past 24 hours, has patient experienced arthralgia (joint pain)?
* **visit_beans** - Do you eat beans or pulses?
* **visit_biscuit** - Do you eat biscuits (including chocolate biscuits)?
* **visit_bmi** - Subject BMI at time of visit, calculated as kg/m2.
* **visit_bowel_day** - Patient's day time bowel frequency.
* **visit_bowel_night** - Patient's night time bowel frequency.
* **visit_bread** - What kind of bread do you usually eat?
* **visit_bread_spread** - What do you usually spread on bread?
* **visit_breadrolls** - Do you eat slices of bread/rolls?
* **visit_breakfast_amt** - Please enter the following information for BREAKFAST you ate: Time of day, Food, Amount (whatever unit easier to you)
.
* **visit_breakfast_food** - Please enter the following information for BREAKFAST you ate: Time of day, Food, Amount (whatever unit easier to you
).
* **visit_breakfast_tod** - Please enter the following information for BREAKFAST you ate: Time of day, Food, Amount (whatever unit easier to you)
.
* **visit_cancer** - Has patient been diagnosed with cancer? If YES, provide details (e.g. I had a cold on 01/02/2012 and recovered on 01/07/2012
; I received a heart surgery on 02/12/2012).
* **visit_cancer_mtc** - Has patient been diagnosed with Medullary Thyroid Cancer, or Multiple Endocrine Neoplasia Type 2 (Men2)?
* **visit_cereal** - Do you eat breakfast cereal?
* **visit_cereal_type** - Which type of breakfast cereal do you normally eat?
* **visit_cheese** - Do you eat cheese?
* **visit_chemo** - In past two weeks, has patient undergone chemotherapy?
* **visit_chest_pain** - Is patient currently suffering from chest pain?
* **visit_chips_crisps** - Do you eat chips, crisps, savory snacks?
* **visit_chronic_dis** - Has patient suffered from a chronic disease? If YES, provide details (e.g. I had a cold on 01/02/2012 and recovered on 
01/07/2012; I received a heart surgery on 02/12/2012).
* **visit_claudication** - Is patient currently suffering from claudication (cramping pain in leg)?
* **visit_colonoscopy** - In past two weeks, has patient undergone a colonoscopy or other procedure?
* **visit_confident** - In the past month, how often has patient felt confident about ability to handle personal problems?
* **visit_control** - In the past month, how often has patient felt  unable to control the important things in their life?
* **visit_coping** - In the past month, how often has patient found that they could not cope with all the things that they had to do?
* **visit_current** - Is the patient currently undergoing hormone replacement therapy?
* **visit_dairy** - Do you eat dairy?
* **visit_date** - Date when the visit occurred
* **visit_diag_other** - Has patient been diagnosed with some other disorder? If YES, provide details (e.g. I had a cold on 01/02/2012 and recove
red on 01/07/2012; I received a heart surgery on 02/12/2012).
* **visit_diarrhea** - In past two weeks, has patient experienced diarrhea?
* **visit_diet_drinks** - Do you drink diet soft drinks, tea or coffee with sugar?
* **visit_difficulties** - In the past month, how often has patient felt difficulties were piling up so high that they could not overcome them?
* **visit_dinner_amt** - Please enter the following information for DINNER you ate: Time of day, Food, Amount (whatever unit easier to you).
* **visit_dinner_food** - Please enter the following information for DINNER you ate: Time of day, Food, Amount (whatever unit easier to you).
* **visit_dinner_tod** - Please enter the following information for DINNER you ate: Time of day, Food, Amount (whatever unit easier to you).
* **visit_duration** - Total duration of hormone replacement therapy
* **visit_dyspnea** - Is patient currently suffering from dyspnea (difficult or labored breathing)?
* **visit_eggs** - Do you eat eggs?
* **visit_ery_nodosum** - In the past 24 hours, has patient experienced erythema nodosum (a specific type of skin inflammation)?
* **visit_fast_gluc** - Fasting glucose level.
* **visit_fever** - Has patient suffered from fever? If YES, provide details (e.g. I had a cold on 01/02/2012 and recovered on 01/07/2012; I rece
ived a heart surgery on 02/12/2012).
* **visit_fish** - Do you eat fish, fish products?
* **visit_fish_count** - How many times do you eat oil rich fish?
* **visit_fish_oil** - Do you eat oil rich fish?
* **visit_fish_white** - Do you eat white fish?
* **visit_fruit** - Do you eat fruit?
* **visit_fruit_count** - How many times do you eat fruits and vegetables or pure fruit juice?
* **visit_going_your_way** - In the past month, how often has patient felt that things were going their way?
* **visit_grains** - Do you eat whole grains?
* **visit_hbi** - Was Harvey-Bradshaw index (HBI) completed?
* **visit_hbi_total** - Harvey-Bradshaw index (HBI) total score.
* **visit_height** - Subject height at time of visit, in cm.
* **visit_hosp** - In past two weeks, has patient been hospitalized?
* **visit_ice_cream** - Do you eat ice cream?
* **visit_id** - The identifier used by the sequence center to uniquely identify the visit
* **visit_immunosupp** - In past two weeks, has patient received immunosuppressants (e.g. oral corticosteroids)?
* **visit_interval** - The amount of time since the last visit (in days)
* **visit_irritation** - In the past month, how often has patient been able to control irritations in their life?
* **visit_juice** - Do you drink fruit juice (not squash)?
* **visit_leg_edema** - Is patient currently suffering from leg edema (swelling)?
* **visit_lunch_amt** - Please enter the following information for LUNCH you ate: Time of day, Food, Amount (whatever unit easier to you).
* **visit_lunch_food** - Please enter the following information for LUNCH you ate: Time of day, Food, Amount (whatever unit easier to you).
* **visit_lunch_tod** - Please enter the following information for LUNCH you ate: Time of day, Food, Amount (whatever unit easier to you).
* **visit_meat** - Do you eat meat?
* **visit_meat_product** - Do you eat processed meats?
* **visit_meat_red** - Do you eat read meat?
* **visit_meat_white** - Do you eat white meat?
* **visit_milk** - What kind of milk do you usually use?
* **visit_mod_activity_days** - During the last 7 days, on how many days did patient do moderate physical activities like carrying light loads, b
icycling at a regular pace, or doubles tennis? Do not include walking.
* **visit_mod_activity_hours** - During the last 7 days, on how many days did patient do moderate physical activities like carrying light loads, 
bicycling at a regular pace, or doubles tennis? Do not include walking.
* **visit_mod_activity_minutes** - During the last 7 days, on how many days did patient do moderate physical activities like carrying light loads
, bicycling at a regular pace, or doubles tennis? Do not include walking.
* **visit_neurologic** - Has a neurological exam been performed?
* **visit_new_meds** - Has patient started any new medications since last visit?
* **visit_number** - A sequential number that is assigned as visits occur for a subject
* **visit_on_top** - In the past month, how often has patient felt that they were on top of things?
* **visit_oral_contrast** - In past two weeks, has patient used an oral contrast?
* **visit_other_food_intake** - Please enter any other information that you want to include about your food consumption on the day.
* **visit_pastry** - Do you eat cakes, scones, sweet pies and pastries?
* **visit_poultry** - Do you eat poultry?
* **visit_preg_plans** - Does patient plan to become pregnant?
* **visit_pregnant** - Is patient currently pregnant?
* **visit_prior** - Has the patient had hormone replacement therapy in the past?
* **visit_probiotic** - Do you take probiotics?
* **visit_psychiatric** - Has a psychiatric exam been performed?
* **visit_pyo_gangrenosum** - In the past 24 hours, has patient experienced pyoderma gangrenosum related ulcers?
* **visit_rash** - Is patient currently experiencing a rash?
* **visit_salt** - At table, how do you use salt?
* **visit_sccai** - Was patient SCCAI (simple clinical colitis activity index) performed?
* **visit_sccai_total** - Patient SCCAI (simple clinical colitis activity index) score.
* **visit_self_assess** - Does patient feel that they can be described as healthy at this time?
* **visit_self_condition** - If patient answered NO to healthy self assessment question, describe the medical conditions they are under now.
* **visit_shellfish** - Do you eat shellfish?
* **visit_snacks_amt** - Please enter the following information for SNACKS you ate: Time of day, Food, Amount (whatever unit easier to you).
* **visit_snacks_food** - Please enter the following information for SNACKS you ate: Time of day, Food, Amount (whatever unit easier to you).
* **visit_snacks_tod** - Please enter the following information for SNACKS you ate: Time of day, Food, Amount (whatever unit easier to you).
* **visit_soda** - Do you drink soft drinks/fizzy drinks?
* **visit_starch** - Do you eat starch?
* **visit_starch_type** - Do you eat potatoes, pasta or rice?
* **visit_stool_blood** - Does patient currently have blood in their stool.
* **visit_stool_soft** - Number of liquid or very soft stools in the past 24 hours
* **visit_stopped_meds** - Has patient stoped any previous medications since last visit?
* **visit_stress** - In the past month, how often has patient felt nervous and 'stressed'?
* **visit_stress_def** - In the past month, what types of stress has patient encountered?
* **visit_study_disease_comment** - Ontology data associated with iHMP disease classes. Disease nodes describe phenotypic traits of a subject.
* **visit_study_disease_description** - Ontology data associated with iHMP disease classes. Disease nodes describe phenotypic traits of a subject.
* **visit_study_disease_disease_ontology_id** - Ontology data associated with iHMP disease classes. Disease nodes describe phenotypic traits of a subject.
* **visit_study_disease_mesh_id** - Ontology data associated with iHMP disease classes. Disease nodes describe phenotypic traits of a subject.
* **visit_study_disease_name** - Ontology data associated with iHMP disease classes. Disease nodes describe phenotypic traits of a subject.
* **visit_study_disease_nci_id** - Ontology data associated with iHMP disease classes. Disease nodes describe phenotypic traits of a subject.
* **visit_study_disease_status** - Status of subject health in reference to study disease.
* **visit_study_disease_umls_concept_id** - Ontology data associated with iHMP disease classes. Disease nodes describe phenotypic traits of a subject.
* **visit_subtype** - The subtype of the visit
* **visit_sugar** - Do you usually take sugar (or sugar substitute) in tea or coffee?
* **visit_sugar_drinks** - Do you drink soft drinks, tea or coffee with sugar?
* **visit_surgery** - Has patient undergone surgery? If YES, provide details (e.g. I had a cold on 01/02/2012 and recovered on 01/07/2012; I received a heart surgery on 02/12/2012).
* **visit_sweets** - Do you eat sweets, chocolates?
* **visit_sweets_count** - How many times do you eat sweets, chocolates, cakes, scones, sweet pies, pastries or biscuits?
* **visit_upset** - In the past month, how often has patient been upset because of something that happened unexpectedly?
* **visit_urgency_def** - Patient's urgency of defecation
* **visit_uveitis** - In the past 24 hours, has patient experienced uveitis (a form of eye inflammation)?
* **visit_veg** - Do you eat vegetables?
* **visit_veg_green** - Do you eat cooked green vegetables (fresh or frozen)?
* **visit_veg_raw** - Do you eat raw vegetables or salad (including tomatoes)?
* **visit_veg_root** - Do you eat cooked root vegetables (fresh or frozen)?
* **visit_vig_activity_days** - During the last 7 days, on how many days did patient do vigorous physical activities like heavy lifting, digging, aerobics, or fast bicycling? Think about only those physical activities that done for at least 10 minutes at a time.
* **visit_vig_activity_hours** - During the last 7 days, on how many days did patient do vigorous physical activities like heavy lifting, digging, aerobics, or fast bicycling? Think about only those physical activities that done for at least 10 minutes at a time.
* **visit_vig_activity_minutes** - During the last 7 days, on how many days did patient do vigorous physical activities like heavy lifting, digging, aerobics, or fast bicycling? Think about only those physical activities that done for at least 10 minutes at a time.
* **visit_walking_days** - During the last 7 days, on how many days did patient walk for at least 10 minutes at a time? This includes walking at work and at home, walking to travel from place to place, and any other walking that done solely for recreation, sport, exercise or leisure.
* **visit_walking_hours** - During the last 7 days, on how many days did patient walk for at least 10 minutes at a time? This includes walking at work and at home, walking to travel from place to place, and any other walking that done solely for recreation, sport, exercise or leisure.
* **visit_walking_minutes** - During the last 7 days, on how many days did patient walk for at least 10 minutes at a time? This includes walking at work and at home, walking to travel from place to place, and any other walking that done solely for recreation, sport, exercise or leisure.
* **visit_water** - Do you drink water?
* **visit_weight** - Subject weight at time of visit, in kg.
* **visit_weight_change** - Has patient suffered from weight gain or loss? If YES, provide details (e.g. I had a cold on 01/02/2012 and recovered on 01/07/2012; I received a heart surgery on 02/12/2012).
* **visit_weight_diff** - Weight gain/loss since last visit.
* **visit_work_missed** - If patient has been physically ill, how many days of work were missed?
* **visit_yogurt** - Do you eat yogurt or other foods containing active bacterial cultures?

### Controlled Vocabulary

The HMP portal converts the [OSDF](https://github.com/ihmpdcc/osdf-schemas) document data store of the HMP data into a graph representation. During this process certain data values are harmonized to facilitate searching. Thus, multiple OSDF values may map to a single HMP representation (e.g. both body sites 'FMA:64183' and 'stool' in OSDF become solely 'feces' in the HMP portal). Below is a table which maps the HMP portal representation of a data point to the data point(s) it originates from in OSDF. 

| HMP representation | OSDF representation |
| ------------------ | ------------------- |
| **study name** | |
| 16S-GM-AO | The Thrifty Microbiome: The Role of the Gut Microbiota in Obesity in the Amish. |
| 16S-GM-CD | Effect of Crohn's Disease Risk Alleles on Enteric Microbiota. |
| 16S-GM-CD2 | Diet, Genetic Factors, and the Gut Microbiome in Crohn's Disease. |
| 16S-GM-CGD | The Human Microbiome in Pediatric Abdominal Pain and Intestinal Inflammation. |
| 16S-GM-EA | Foregut Microbiome in Development of Esophageal Adenocarcinoma. |
| 16S-GM-NE | The Neonatal Microbiome and Necrotizing Enterocolitis. |
| 16S-GM-UC | The Role of the Gut Microbiota in Ulcerative Colitis, Targeted Gene Survey. |
| 16S-PP1 | Human microbiome project 16S production phase I. |
| 16S-PP2 | Human microbiome project 16S production phase II. |
| 16S-SM-ADI | Skin Microbiome in Disease States: Atopic Dermatitis and Immunodeficiency. |
| 16S-SM-P | Evaluation of the Cutaneous Microbiome in Psoriasis. |
| 16S-UM-AD | Urethral Microbiome of Adolescent Males. |
| 16S-VM-BV | The Microbial Ecology of Bacterial Vaginosis: A Fine Scale Resolution Metagenomic Study. |
| 16S-VM-DGE | The Vaginal Microbiome: Disease, Genetics and the Environment, 16S Gene Survey. |
| IBDMDB | ibdmdb,Inflammatory Bowel Disease Multi-omics Database (IBDMDB) |
| MOMS-PI | momspi |
| T2D | prediabetes |
| WGS-GM-CD | Metagenomic Analysis of the Structure and Function of the Human Gut Microbiota in Crohn's Disease. |
| WGS-GM-UC | The Role of the Gut Microbiota in Ulcerative Colitis, Whole Metagenome Sequencing Project. |
| WGS-PP1 | Human microbiome project WGS production phase I. |
| WGS-PP2 | Human microbiome project WGS production phase II. |
| WGS-VIR-FE | The Human Virome in Children And Its Relationship to Febrile Illness. |
| | |
| **body site** | |
| abdomen | abdomen |
| angle of seventh rib | FMA:7842 |
| anterior part of leg | shin |
| ascending colon | ascending_colon |
| back | back |
| blood cell | blood |
| buccal mucosa | Buccal mucosa [FMA:59785],buccal_mucosa |
| cerebrospinal fluid | cerebrospinal_fluid |
| cervix of uterus | cervix |
| cubital fossa | antecubital_fossa |
| descending colon | descending_colon |
| dorsum of tongue | Dorsum of tongue [FMA:54651],tongue_dorsum |
| elbow | elbow |
| external naris | anterior_nares,External naris [FMA:59645],nare |
| feces | stool,FMA:64183 |
| foot | foot |
| forearm | volar_forearm,forearm |
| gall bladder | gall_bladder |
| gastric antrum | gastric_antrum |
| gastrointestinal tract | gut,Gastrointestinal tract [FMA:71132] |
| gingiva | gingival_crevices,subgingival_plaque,supragingival_plaque,attached_keratinized_gingiva,gingiva [FMA:59762],Gingiva [FMA:59762] |
| hand | hand |
| hard palate | Hard palate [FMA:55023],hard_palate |
| head | head |
| ileal-anal pouch | ileal-anal_pouch |
| ileum | ileal_pouch,ileum |
| knee | knee |
| left arm | left_arm |
| left cubital fossa | left_antecubital_fossa |
| left retroauricular crease | left_retroauricular_crease,Skin of left auriculotemporal part of head [FMA:70332] |
| leg | leg |
| lung aspirate | lung_aspirate |
| lymph node | lymph_node |
| nasal cavity | nasal |
| nasopharynx | Nasopharynx [FMA:54878],nasopharynx |
| oral cavity | Oral cavity [FMA:20292],oral_cavity |
| orifice of vagina | Orifice of vagina [FMA:19984],vaginal_introitus |
| palatine tonsil | Palantine tonsil [FMA:9610],palatine_tonsils,Palatine tonsil [FMA:9610] |
| perianal space | perianal_region |
| peripheral blood mononuclear cell | FMA:86713 |
| plasma | Plasma [FMA:62970] |
| popliteal fossa | popliteal_fossa |
| portion of saliva | saliva |
| posterior fornix of vagina | posterior_fornix,Posterior fornix of vagina [FMA:19987] |
| rectum | rectal |
| respiratory tract | respiratory_tract |
| right cubital fossa | right_antecubital_fossa,right cubital fossa [FMA:39849] |
| right nasal cavity | FMA:276108 |
| right retroauricular crease | Skin of right auriculotemporal part of head [FMA:70331],right_retroauricular_crease |
| scalp | scalp |
| shoulder | shoulder |
| sigmoid colon | sigmoid_colon |
| spinal cord | spinal_cord |
| synovial fluid | synovial_fluid |
| terminal ileum | terminal_ileum |
| thigh | thigh |
| throat | Throat [FMA:228738],throat |
| transverse colon | transverse_colon |
| unknown | unknown |
| upper respiratory tract | upper_respiratory_tract |
| urethra | urethra |
| urinary tract | FMA:326482,urinary_tract |
| vagina | mid_vagina,Vagina [FMA:19949],vaginal |
| wall of vagina | wall_of_vagina |

## Cart Metadata

On the cart page of the UI, one can download both a manifest of their samples+files of interest as well as metadata for these same entities. The manifest is to be used in conjunction with the [HMP client](https://github.com/IGS/hmp_client) to efficiently download all the files. The metadata serves as an additional source of input for analysis. The metadata, which is tab-separated, will always consist of a minimum set of (in this order):
 * **sample_id**
 * **subject_id**
 * **sample_body_site**
 * **visit_number**
 * **subject_gender**
 * **subject_race**
 * **study_full_name**
 * **project_name**

Additional columns may be present in the metadata file if at least one of the samples present has a non-null value for the metadata. All potential metadata which will be present, if it was collected for the sample of interest, is defined in the [OSDF](https://github.com/IGS/OSDF) schemas found below:
* [subject attributes](https://github.com/ihmpdcc/osdf-schemas/blob/master/ihmp/schemas/subject_attr.json)
* [sample attributes](https://github.com/ihmpdcc/osdf-schemas/blob/master/ihmp/schemas/sample_attr.json)
* [visit attributes](https://github.com/ihmpdcc/osdf-schemas/blob/master/ihmp/schemas/visit_attr.json)
* [attribute subsets](https://github.com/ihmpdcc/osdf-schemas/tree/master/ihmp/aux)