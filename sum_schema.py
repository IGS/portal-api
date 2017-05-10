import graphene
from models import SBucketCounter, FileSize
from query import get_buckets, get_total_file_size

***REMOVED***Can preload default counts for fast loading, user interaction with facets or
***REMOVED***queries will then refine these counts.
proN = get_buckets("PSS.project_name","yes","")
samBS = get_buckets("VS.body_site","yes","")
subG = get_buckets("PSS.gender","yes","")
fileF = get_buckets("F.format","yes","")
fileS = get_buckets("F.subtype","yes","")
stuN = get_buckets("PSS.study_name","yes","")
fs = FileSize(value=get_total_file_size(""))

class Query(graphene.ObjectType):

    sample_body_site = graphene.Field(SBucketCounter, cy=graphene.String(description='Cypher WHERE parameters'), name="sample_body_site")
    project_name = graphene.Field(SBucketCounter, cy=graphene.String(description='Cypher WHERE parameters'), name="project_name")
    subject_gender = graphene.Field(SBucketCounter, cy=graphene.String(description='Cypher WHERE parameters'), name="subject_gender")
    file_format = graphene.Field(SBucketCounter, cy=graphene.String(description='Cypher WHERE parameters'), name="file_format")
    file_subtype = graphene.Field(SBucketCounter, cy=graphene.String(description='Cypher WHERE parameters'), name="file_subtype")
    study_name = graphene.Field(SBucketCounter, cy=graphene.String(description='Cypher WHERE parameters'), name="study_name")
    fs = graphene.Field(FileSize, cy=graphene.String(description='Cypher WHERE parameters'))

    def resolve_sample_body_site(self, args, context, info):
        ***REMOVED***accept the pipes and convert to quotes again now that it's been passed across the URL
        cy = args['cy'].replace("|",'"') 
        if cy == "":
            return samBS
        else:
            return get_buckets("VS.body_site","yes",cy)

    def resolve_project_name(self, args, context, info):
        cy = args['cy'].replace("|",'"') 
        if cy == "":
            return proN
        else:
            return get_buckets("PSS.project_name","yes",cy)

    def resolve_subject_gender(self, args, context, info):
        cy = args['cy'].replace("|",'"') 
        if cy == "":
            return subG
        else:
            return get_buckets("PSS.gender","yes",cy)

    def resolve_file_format(self, args, context, info):
        cy = args['cy'].replace("|",'"') 
        if cy == "":
            return fileF
        else:
            return get_buckets("F.format","yes",cy)

    def resolve_file_subtype(self, args, context, info):
        cy = args['cy'].replace("|",'"') 
        if cy == "":
            return fileS
        else:
            return get_buckets("F.subtype","yes",cy)

    def resolve_study_name(self, args, context, info):
        cy = args['cy'].replace("|",'"') 
        if cy == "":
            return stuN
        else:
            return get_buckets("PSS.study_name","yes",cy)

    def resolve_fs(self, args, context, info):
        cy = args['cy'].replace("|",'"') 
        if cy == "":
            return fs
        else:
            return FileSize(value=get_total_file_size(cy))

***REMOVED***As noted above, going to hit Neo4j once and get everything then let GQL 
***REMOVED***do its magic client side to return the values that the user wants. 
sum_schema = graphene.Schema(query=Query)
