import graphene

###################
# DEFINING MODELS #
###################

# This section will contain all the necessary models needed to populate the schema

class Project(graphene.ObjectType): # Graphene object for node
    projectId = graphene.String(name="project_id")
    primarySite = graphene.String(name="primary_site")
    name = graphene.String()
    studyName = graphene.String(name="study_name")
    studyFullName = graphene.String(name="study_full_name")

class Pagination(graphene.ObjectType): # GDC expects pagination data for populating table
    count = graphene.Int()
    sort = graphene.String()
    fromNum = graphene.Int(name="from")
    page = graphene.Int()
    total = graphene.Int()
    pages = graphene.Int()
    size = graphene.Int()

class CaseHits(graphene.ObjectType): # GDC defines hits as matching Project node + Case ID (in our case sample ID)
    project = graphene.Field(Project)
    caseId = graphene.String(name="case_id")

class IndivFiles(graphene.ObjectType): # individual files to populate all files list
    dataType = graphene.String(name="data_type")
    fileName = graphene.String(name="file_name")
    dataFormat = graphene.String(name="data_format")
    access = graphene.String() # only exists for consistency with GDC
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

class FileHits(graphene.ObjectType): # GDC defined file hits for data type, file name, data format, and more
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

class Bucket(graphene.ObjectType): # Each bucket is a distinct property in the node group
    key = graphene.String()
    docCount = graphene.Int(name="doc_count")

class BucketCounter(graphene.ObjectType): # List of Buckets
    buckets = graphene.List(Bucket)

class Aggregations(graphene.ObjectType): # Collecting lists of buckets (BucketCounter)
    # Note that many of the "name" values are identical to the variable assigned to,
    # but all are explicitly named for clarity and to match syntax of more complex names
    project_name = graphene.Field(BucketCounter, name="project_name")
    project_subtype = graphene.Field(BucketCounter, name="project_subtype")

    study_subtype = graphene.Field(BucketCounter, name="study_subtype")
    study_center = graphene.Field(BucketCounter, name="study_center")
    study_name = graphene.Field(BucketCounter, name="study_name")

    subject_gender = graphene.Field(BucketCounter, name="subject_gender")
    subject_race = graphene.Field(BucketCounter, name="subject_race")

    visit_number = graphene.Field(BucketCounter, name="visit_number")
    visit_interval = graphene.Field(BucketCounter, name="visit_interval")
    visit_date = graphene.Field(BucketCounter, name="visit_date")

    sample_bodyproduct = graphene.Field(BucketCounter, name="sample_body_product")
    sample_fmabodysite = graphene.Field(BucketCounter, name="sample_fma_body_site")
    sample_geolocname = graphene.Field(BucketCounter, name="sample_geo_loc_name")
    sample_sampcollectdevice = graphene.Field(BucketCounter, name="sample_samp_collect_device")
    sample_envpackage = graphene.Field(BucketCounter, name="sample_env_package")
    sample_feature = graphene.Field(BucketCounter, name="sample_feature")
    sample_material = graphene.Field(BucketCounter, name="sample_material")
    sample_biome = graphene.Field(BucketCounter, name="sample_biome")
    sample_id = graphene.Field(BucketCounter, name="sample_id")
    
    file_id = graphene.Field(BucketCounter, name="file_id")
    file_format = graphene.Field(BucketCounter, name="file_format")
    file_node_type = graphene.Field(BucketCounter, name="file_node_type")

    dataType = graphene.Field(BucketCounter, name="data_type")
    dataFormat = graphene.Field(BucketCounter, name="data_format")

class SBucket(graphene.ObjectType): # Same idea as early bucket but used for summation (pie charts)
    key = graphene.String()
    docCount = graphene.Int(name="doc_count")
    caseCount = graphene.Int(name="case_count")
    fileSize = graphene.Float(name="file_size")

class SBucketCounter(graphene.ObjectType): # List of SBuckets
    buckets = graphene.List(SBucket)

class FileSize(graphene.ObjectType): # total aggregate file size of current set of chosen data
    value = graphene.Float()

class IndivSample(graphene.ObjectType): # individual sample model for populating the particular sample page
    sample_id = graphene.String(name="sample_id")
    body_site = graphene.String(name="body_site")
    subject_id = graphene.String(name="subject_id")
    subject_gender = graphene.String(name="subject_gender")
    study_center = graphene.String(name="study_center")
    project_name = graphene.String(name="project_name")
