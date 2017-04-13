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
    Project_name = graphene.Field(BucketCounter, name="Project_name")

    Study_subtype = graphene.Field(BucketCounter, name="Study_subtype")
    Study_center = graphene.Field(BucketCounter, name="Study_center")
    Study_name = graphene.Field(BucketCounter, name="Study_name")

    Subject_gender = graphene.Field(BucketCounter, name="Subject_gender")
    Subject_race = graphene.Field(BucketCounter, name="Subject_race")

    Visit_number = graphene.Field(BucketCounter, name="Visit_number")
    Visit_interval = graphene.Field(BucketCounter, name="Visit_interval")
    Visit_date = graphene.Field(BucketCounter, name="Visit_date")

    Sample_bodyproduct = graphene.Field(BucketCounter, name="Sample_body_product")
    Sample_fmabodysite = graphene.Field(BucketCounter, name="Sample_fma_body_site")
    Sample_geolocname = graphene.Field(BucketCounter, name="Sample_geo_loc_name")
    Sample_sampcollectdevice = graphene.Field(BucketCounter, name="Sample_samp_collect_device")
    Sample_envpackage = graphene.Field(BucketCounter, name="Sample_env_package")
    Sample_feature = graphene.Field(BucketCounter, name="Sample_feature")
    Sample_material = graphene.Field(BucketCounter, name="Sample_material")
    Sample_biome = graphene.Field(BucketCounter, name="Sample_biome")
    Sample_id = graphene.Field(BucketCounter, name="Sample_id")
    
    File_id = graphene.Field(BucketCounter, name="File_id")
    File_format = graphene.Field(BucketCounter, name="File_format")
    File_node_type = graphene.Field(BucketCounter, name="File_node_type")

    dataType = graphene.Field(BucketCounter, name="data_type")
    dataFormat = graphene.Field(BucketCounter, name="data_format")

class SBucket(graphene.ObjectType): ***REMOVED***Same idea as early bucket but used for summation (pie charts)
    key = graphene.String()
    docCount = graphene.Int(name="doc_count")
    caseCount = graphene.Int(name="case_count")
    fileSize = graphene.Float(name="file_size")

class SBucketCounter(graphene.ObjectType): ***REMOVED***List of SBuckets
    buckets = graphene.List(SBucket)

class FileSize(graphene.ObjectType): ***REMOVED***total aggregate file size of current set of chosen data
    value = graphene.Float()
