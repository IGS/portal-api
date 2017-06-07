import graphene
from models import Pagination, CaseHits, Aggregations
from query import get_buckets, get_case_hits, get_pagination

# Can preload counts by declaring these in this next block. 
# These aggregations can remain stagnant so don't need to update
# based on filters as these are used to give a total count of the data.
proN = get_buckets("PS.project_name","no","")
proS = get_buckets("PS.project_subtype","no","")
subUUID = get_buckets("PS.id","no","")
subID = get_buckets("PS.rand_subject_id","no","")
subG = get_buckets("PS.gender","no","")
subR = get_buckets("PS.race","no","")
visVN = get_buckets("VSS.visit_visit_number","no","") 
visI = get_buckets("VSS.visit_interval","no","") 
visD = get_buckets("VSS.visit_date","no","")
samBP = get_buckets("VSS.body_product","no","")
samFMA = get_buckets("VSS.body_site","no","")
samGLN = get_buckets("VSS.geo_loc_name","no","")
samSCD = get_buckets("VSS.samp_collect_device","no","")
samEP = get_buckets("VSS.env_package","no","")
samF = get_buckets("VSS.feature","no","")
samID = get_buckets("VSS.id","no","")
samM = get_buckets("VSS.material","no","")
samB = get_buckets("VSS.biome","no","")
stuS = get_buckets("VSS.study_subtype","no","")
stuC = get_buckets("VSS.study_center","no","")
stuN = get_buckets("VSS.study_name","no","")
fileF = get_buckets("F.format","no","")
fileID = get_buckets("F.id","no","")
fileNT = get_buckets("F.node_type","no","")
tagT = get_buckets("T.term","no","")

class Query(graphene.ObjectType):

    pagination = graphene.Field(Pagination, cy=graphene.String(description='Cypher WHERE parameters'), s=graphene.Int(description='size of subset to return'), f=graphene.Int(description='what position of the sort to start at'))
    hits = graphene.List(CaseHits, cy=graphene.String(description='Cypher WHERE parameters'), s=graphene.Int(description='size of subset to return'), o=graphene.String(description='what to sort by'), f=graphene.Int(description='what position of the sort to start at'))
    aggregations = graphene.Field(Aggregations)

    def resolve_pagination(self, args, context, info):
        cy = args['cy'].replace("|",'"')
        return get_pagination(cy,args['s'],args['f'],'c')

    def resolve_hits(self, args, context, info):
        cy = args['cy'].replace("|",'"') # handle quotes for GQL
        if args['cy'] == "":
            return get_case_hits(args['s'],args['o'],args['f'],"")
        else:
            return get_case_hits(args['s'],args['o'],args['f'],cy)

    def resolve_aggregations(self, args, context, info):
        return Aggregations(
            project_name=proN,
            project_subtype=proS,
            study_subtype=stuS,
            study_center=stuC,
            study_name=stuN,
            subject_uuid=subUUID,
            subject_id=subID,
            subject_gender=subG,
            subject_race=subR,
            visit_number=visVN,
            visit_interval=visI,
            visit_date=visD,
            sample_bodyproduct=samBP,
            sample_bodysite=samFMA,
            sample_geolocname=samGLN,
            sample_sampcollectdevice=samSCD,
            sample_envpackage=samEP,
            sample_feature=samF,
            sample_material=samM,
            sample_id=samID,
            sample_biome=samB,
            file_format=fileF,
            file_type=fileNT,
            file_id=fileID,
            tag_term=tagT
            )
        
ac_schema = graphene.Schema(query=Query)