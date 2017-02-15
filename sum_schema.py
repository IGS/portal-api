import graphene
from models import SBucketCounter, FileSize, get_buckets, get_total_file_size

# Can preload default counts for fast loading, user interaction with facets or
# queries will then refine these counts.
proName = get_buckets("Project.name","yes","")
samFMA = get_buckets("Sample.fma_body_site","yes","")
subGender = get_buckets("Subject.gender","yes","")
fileFormat = get_buckets("File.format","yes","")
fileSubtype = get_buckets("File.subtype","yes","")
studyName = get_buckets("Study.name","yes","")
fs = FileSize(value=get_total_file_size(""))

class Query(graphene.ObjectType):

    SampleFmabodysite = graphene.Field(SBucketCounter, cy=graphene.String(description='Cypher WHERE parameters'))
    ProjectName = graphene.Field(SBucketCounter, cy=graphene.String(description='Cypher WHERE parameters'))
    SubjectGender = graphene.Field(SBucketCounter, cy=graphene.String(description='Cypher WHERE parameters'))
    FileFormat = graphene.Field(SBucketCounter, cy=graphene.String(description='Cypher WHERE parameters'))
    FileSubtype = graphene.Field(SBucketCounter, cy=graphene.String(description='Cypher WHERE parameters'))
    StudyName = graphene.Field(SBucketCounter, cy=graphene.String(description='Cypher WHERE parameters'))
    fs = graphene.Field(FileSize, cy=graphene.String(description='Cypher WHERE parameters'))

    def resolve_SampleFmabodysite(self, args, context, info):
        # accept the pipes and convert to quotes again now that it's been passed across the URL
        cy = args['cy'].replace("|",'"') 
        if cy == "":
            return samFMA
        else:
            return get_buckets("Sample.fma_body_site","yes",cy)

    def resolve_ProjectName(self, args, context, info):
        cy = args['cy'].replace("|",'"') 
        if cy == "":
            return proName
        else:
            return get_buckets("Project.name","yes",cy)

    def resolve_SubjectGender(self, args, context, info):
        cy = args['cy'].replace("|",'"') 
        if cy == "":
            return subGender
        else:
            return get_buckets("Subject.gender","yes",cy)

    def resolve_FileFormat(self, args, context, info):
        cy = args['cy'].replace("|",'"') 
        if cy == "":
            return fileFormat
        else:
            return get_buckets("File.format","yes",cy)

    def resolve_FileSubtype(self, args, context, info):
        cy = args['cy'].replace("|",'"') 
        if cy == "":
            return fileSubtype
        else:
            return get_buckets("File.subtype","yes",cy)

    def resolve_StudyName(self, args, context, info):
        cy = args['cy'].replace("|",'"') 
        if cy == "":
            return studyName
        else:
            return get_buckets("Study.name","yes",cy)

    def resolve_fs(self, args, context, info):
        cy = args['cy'].replace("|",'"') 
        if cy == "":
            return fs
        else:
            return FileSize(value=get_total_file_size(cy))

# As noted above, going to hit Neo4j once and get everything then let GQL 
# do its magic client side to return the values that the user wants. 
sum_schema = graphene.Schema(query=Query)
