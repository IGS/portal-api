import graphene
from models import Pagination, CaseHits, Aggregations, get_buckets, get_case_hits, get_pagination

# Can preload counts by declaring these in this next block. 
# These aggregations can remain stagnant so don't need to update
# based on filters as these are used to give a total count of the data.
# Any properties with a "###" following it mean that the property being
# grabbed isn't exactly what the user sees on the site. For instance,
# 'Project name' on the site actually searches for 'Project.project_name'.
# This is to provide a more succint search parameter. 
proN = get_buckets("project.name","no","") ###
stuS = get_buckets("study.subtype","no","")
stuC = get_buckets("study.center","no","")
stuN = get_buckets("study.name","no","")
subG = get_buckets("subject.gender","no","")
subR = get_buckets("subject.race","no","")
visVN = get_buckets("visit.visit_number","no","") ### 
visI = get_buckets("visit.interval","no","") 
visD = get_buckets("visit.date","no","")
samBP = get_buckets("sample.body_product","no","")
samFMA = get_buckets("sample.fma_body_site","no","")
samGLN = get_buckets("sample.geo_loc_name","no","")
samSCD = get_buckets("sample.samp_collect_device","no","")
samEP = get_buckets("sample.env_package","no","")
samSS = get_buckets("sample.supersite","no","")
samF = get_buckets("sample.feature","no","")
samID = get_buckets("sample.id","no","")
samM = get_buckets("sample.material","no","")
samB = get_buckets("sample.biome","no","")
fileF = get_buckets("File.format","no","")
fileID = get_buckets("File.id","no","")
fileNT = get_buckets("File.node_type","no","")

class Query(graphene.ObjectType):

    pagination = graphene.Field(Pagination, cy=graphene.String(description='Cypher WHERE parameters'), s=graphene.Int(description='size of subset to return'), f=graphene.Int(description='what position of the sort to start at'))
    hits = graphene.List(CaseHits, cy=graphene.String(description='Cypher WHERE parameters'), s=graphene.Int(description='size of subset to return'), o=graphene.String(description='what to sort by'), f=graphene.Int(description='what position of the sort to start at'))
    aggregations = graphene.Field(Aggregations)

    def resolve_pagination(self, args, context, info):
        cy = args['cy'].replace("|",'"')
        return get_pagination(cy,args['s'],args['f'],'c')

    def resolve_hits(self, args, context, info):
        cy = args['cy'].replace("|",'"') # handle quotes for GQL
        o = args['o'].replace("case_id","Sample.id") # lose the portal ordering syntax
        o = o.replace(".raw","")
        if args['cy'] == "":
            return get_case_hits(args['s'],"Sample.id:asc",args['f'],"")
        else:
            return get_case_hits(args['s'],o,args['f'],cy)

    def resolve_aggregations(self, args, context, info):
        return Aggregations(Project_name=proN,Study_subtype=stuS,Study_center=stuC,Study_name=stuN,
            Subject_gender=subG,Subject_race=subR,Visit_number=visVN,Visit_interval=visI,Visit_date=visD,
            Sample_bodyproduct=samBP,Sample_fmabodysite=samFMA,Sample_geolocname=samGLN,Sample_sampcollectdevice=samSCD,
            Sample_envpackage=samEP,Sample_supersite=samSS,Sample_feature=samF,Sample_material=samM,
            Sample_id=samID,Sample_biome=samB,File_format=fileF,File_node_type=fileNT,File_id=fileID
            )
        
ac_schema = graphene.Schema(query=Query)