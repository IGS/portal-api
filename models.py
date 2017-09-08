import graphene

###################
***REMOVED***DEFINING MODELS #
###################

***REMOVED***This section will contain all the necessary models needed to populate the schema

class Project(graphene.ObjectType): ***REMOVED***Graphene object for node
    projectId = graphene.String(name="project_id")
    primarySite = graphene.String(name="primary_site")
    name = graphene.String()
    studyName = graphene.String(name="study_name")
    studyFullName = graphene.String(name="study_full_name")

class Pagination(graphene.ObjectType): ***REMOVED***GDC expects pagination data for populating table
    count = graphene.Int()
    sort = graphene.String()
    fromNum = graphene.Int(name="from")
    page = graphene.Int()
    total = graphene.Int()
    pages = graphene.Int()
    size = graphene.Int()

class CaseHits(graphene.ObjectType): ***REMOVED***GDC defines hits as matching Project node + Case ID (in our case sample ID)
    project = graphene.Field(Project)
    caseId = graphene.String(name="case_id")
    visitNumber = graphene.String(name="visit_number")
    subjectId = graphene.String(name="subject_id")

class IndivFiles(graphene.ObjectType): ***REMOVED***individual files to populate all files list
    dataType = graphene.String(name="data_type")
    fileName = graphene.String(name="file_name")
    dataFormat = graphene.String(name="data_format")
    access = graphene.String() ***REMOVED***only exists for consistency with GDC
    fileId = graphene.String(name="file_id")
    fileSize = graphene.Int(name="file_size")

class Analysis(graphene.ObjectType):
    updatedDatetime = graphene.String(name="updated_datetime")
    workflowType = graphene.String(name="workflow_type")
    analysisId = graphene.String(name="analysis_id")
    inputFiles = graphene.List(IndivFiles, name="input_files")

class AssociatedEntities(graphene.ObjectType):
    entityId = graphene.String(name="entity_id")
    caseId = graphene.String(name="case_id")
    entityType = graphene.String(name="entity_type")

class FileHits(graphene.ObjectType): ***REMOVED***GDC defined file hits for data type, file name, data format, and more
    dataType = graphene.String(name="data_type")
    fileName = graphene.String(name="file_name")
    md5sum = graphene.String()
    dataFormat = graphene.String(name="data_format")
    submitterId = graphene.String(name="submitter_id")
    state = graphene.String()
    access = graphene.String()
    fileId = graphene.String(name="file_id")
    dataCategory = graphene.String(name="data_category")
    experimentalStrategy = graphene.String(name="experimental_strategy")
    fileSize = graphene.Float(name="file_size")
    cases = graphene.List(CaseHits)
    associatedEntities = graphene.List(AssociatedEntities, name="associated_entities")
    analysis = graphene.Field(Analysis)

class Bucket(graphene.ObjectType): ***REMOVED***Each bucket is a distinct property in the node group
    key = graphene.String()
    docCount = graphene.Int(name="doc_count")

class BucketCounter(graphene.ObjectType): ***REMOVED***List of Buckets
    buckets = graphene.List(Bucket)

class Aggregations(graphene.ObjectType): ***REMOVED***Collecting lists of buckets (BucketCounter)
    ***REMOVED***Note that many of the "name" values are identical to the variable assigned to,
    ***REMOVED***but all are explicitly named for clarity and to match syntax of more complex names
    project_name = graphene.Field(BucketCounter, name="project_name")
    project_subtype = graphene.Field(BucketCounter, name="project_subtype")

    study_center = graphene.Field(BucketCounter, name="study_center")
    study_contact = graphene.Field(BucketCounter, name="study_contact")
    study_description = graphene.Field(BucketCounter, name="study_description")
    study_name = graphene.Field(BucketCounter, name="study_name")
    study_srpid = graphene.Field(BucketCounter, name="study_srp_id")
    study_subtype = graphene.Field(BucketCounter, name="study_subtype")

    subject_gender = graphene.Field(BucketCounter, name="subject_gender")
    subject_id = graphene.Field(BucketCounter, name="subject_id")
    subject_race = graphene.Field(BucketCounter, name="subject_race")
    subject_subtype = graphene.Field(BucketCounter, name="subject_subtype")
    subject_uuid = graphene.Field(BucketCounter, name="subject_uuid")

    visit_date = graphene.Field(BucketCounter, name="visit_date")
    visit_hbi = graphene.Field(BucketCounter, name="visit_hbi")
    visit_id = graphene.Field(BucketCounter, name="visit_id")
    visit_interval = graphene.Field(BucketCounter, name="visit_interval")
    visit_number = graphene.Field(BucketCounter, name="visit_number")
    visit_subtype = graphene.Field(BucketCounter, name="visit_subtype")

    sample_biome = graphene.Field(BucketCounter, name="sample_biome")
    sample_bodyproduct = graphene.Field(BucketCounter, name="sample_body_product")
    sample_bodysite = graphene.Field(BucketCounter, name="sample_body_site")
    sample_collectiondate = graphene.Field(BucketCounter, name="sample_collection_date")
    sample_envpackage = graphene.Field(BucketCounter, name="sample_env_package")
    sample_feature = graphene.Field(BucketCounter, name="sample_feature")
    sample_fecalcal = graphene.Field(BucketCounter, name="sample_fecalcal")
    sample_geolocname = graphene.Field(BucketCounter, name="sample_geo_loc_name")
    sample_id = graphene.Field(BucketCounter, name="sample_id")
    sample_latlon = graphene.Field(BucketCounter, name="sample_lat_lon")
    sample_material = graphene.Field(BucketCounter, name="sample_material")
    sample_reltooxygen = graphene.Field(BucketCounter, name="sample_rel_to_oxygen")
    sample_sampcollectdevice = graphene.Field(BucketCounter, name="sample_samp_collect_device")
    sample_sampmatprocess = graphene.Field(BucketCounter, name="sample_samp_mat_process")
    sample_sampsize = graphene.Field(BucketCounter, name="sample_samp_size")
    sample_subtype= graphene.Field(BucketCounter, name="sample_subtype")
    sample_supersite = graphene.Field(BucketCounter, name="sample_supersite")
    
    file_format = graphene.Field(BucketCounter, name="file_format")
    file_id = graphene.Field(BucketCounter, name="file_id")
    file_matrix_type = graphene.Field(BucketCounter, name="file_matrix_type")
    file_type = graphene.Field(BucketCounter, name="file_type")
    
    tag_term = graphene.Field(BucketCounter, name="tag_term")

class SBucket(graphene.ObjectType): ***REMOVED***Same idea as early bucket but used for summation (pie charts)
    key = graphene.String()
    docCount = graphene.Int(name="doc_count")
    caseCount = graphene.Int(name="case_count")
    fileSize = graphene.Float(name="file_size")

class SBucketCounter(graphene.ObjectType): ***REMOVED***List of SBuckets
    buckets = graphene.List(SBucket)

class FileSize(graphene.ObjectType): ***REMOVED***total aggregate file size of current set of chosen data
    value = graphene.Float()

class IndivSample(graphene.ObjectType): ***REMOVED***individual sample model for populating the particular sample page
    sample_id = graphene.String(name="sample_id")
    body_site = graphene.String(name="body_site")
    subject_id = graphene.String(name="subject_id")
    rand_subject_id = graphene.String(name="rand_subject_id")
    subject_gender = graphene.String(name="subject_gender")
    study_center = graphene.String(name="study_center")
    project_name = graphene.String(name="project_name")
    files = graphene.List(IndivFiles, name="files")

class PieCharts(graphene.ObjectType): ***REMOVED***individual sample model for populating the particular sample page
    sample_body_site = graphene.Field(SBucketCounter, name="sample_body_site")
    project_name = graphene.Field(SBucketCounter, name="project_name")
    subject_gender = graphene.Field(SBucketCounter, name="subject_gender")
    file_format = graphene.Field(SBucketCounter, name="file_format")
    file_type = graphene.Field(SBucketCounter, name="file_type")
    study_name = graphene.Field(SBucketCounter, name="study_name")
    fs = graphene.Field(FileSize)
