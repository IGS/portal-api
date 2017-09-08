import graphene
from models import Pagination, CaseHits, Aggregations
from query import get_buckets, get_case_hits, get_pagination

# Can preload counts by declaring these in this next block. 
# These aggregations can remain stagnant so don't need to update
# based on filters as these are used to give a total count of the data.
pro_name = get_buckets("PS.project_name","no","")
pro_subtype = get_buckets("PS.project_subtype","no","")

stu_center = get_buckets("VSS.study_center","no","")
stu_contact = get_buckets("VSS.study_contact","no","")
stu_description = get_buckets("VSS.study_description","no","")
stu_name = get_buckets("VSS.study_name","no","")
stu_srp_id = get_buckets("VSS.study_srp_id","no","")
stu_subtype = get_buckets("VSS.study_subtype","no","")

sub_gender = get_buckets("PS.gender","no","")
sub_id = get_buckets("PS.id","no","")
sub_race = get_buckets("PS.race","no","")
sub_rand_subject_id = get_buckets("PS.rand_subject_id","no","")
sub_subtype = get_buckets("PS.subtype","no","")

vis_date = get_buckets("VSS.visit_date","no","")
vis_hbi = get_buckets("VSS.visit_hbi","no","") 
vis_id = get_buckets("VSS.visit_id","no","") 
vis_interval = get_buckets("VSS.visit_interval","no","")
vis_subtype = get_buckets("VSS.visit_subtype","no","") 
vis_visit_number = get_buckets("VSS.visit_visit_number","no","")  

sam_biome = get_buckets("VSS.biome","no","")
sam_body_product = get_buckets("VSS.body_product","no","")
sam_body_site = get_buckets("VSS.body_site","no","")
sam_collection_date = get_buckets("VSS.collection_date","no","")
sam_env_package = get_buckets("VSS.env_package","no","")
sam_feature = get_buckets("VSS.feature","no","")
sam_fecalcal = get_buckets("VSS.fecalcal","no","")
sam_geo_loc_name = get_buckets("VSS.geo_loc_name","no","")
sam_id = get_buckets("VSS.id","no","")
sam_lat_lon = get_buckets("VSS.lat_lon","no","")
sam_material = get_buckets("VSS.material","no","")
sam_rel_to_oxygen = get_buckets("VSS.rel_to_oxygen","no","")
sam_samp_collect_device = get_buckets("VSS.samp_collect_device","no","")
sam_samp_mat_process = get_buckets("VSS.samp_mat_process","no","")
sam_samp_size = get_buckets("VSS.samp_size","no","")
sam_subtype = get_buckets("VSS.subtype","no","")
sam_supersite = get_buckets("VSS.supersite","no","")

file_format = get_buckets("F.format","no","")
file_id = get_buckets("F.id","no","")
file_matrix_type = get_buckets("F.matrix_type","no","")
file_node_type = get_buckets("F.node_type","no","")

tag_term = get_buckets("T.term","no","")

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
            project_name=pro_name,
            project_subtype=pro_subtype,
            
            study_center=stu_center,
            study_contact=stu_contact,
            study_description=stu_description,
            study_name=stu_name,
            study_srpid=stu_srp_id,
            study_subtype=stu_subtype,

            subject_gender=sub_gender,
            subject_id=sub_rand_subject_id,
            subject_race=sub_race,
            subject_subtype=sub_subtype,
            subject_uuid=sub_id,
            
            visit_date=vis_date,
            visit_hbi=vis_hbi,
            visit_id=vis_id,
            visit_interval=vis_interval,
            visit_number=vis_visit_number,
            visit_subtype=vis_subtype,

            sample_biome=sam_biome,
            sample_bodyproduct=sam_body_product,
            sample_bodysite=sam_body_site,
            sample_collectiondate=sam_collection_date,
            sample_envpackage=sam_env_package,
            sample_feature=sam_feature,
            sample_fecalcal=sam_fecalcal,
            sample_geolocname=sam_geo_loc_name,
            sample_id=sam_id,
            sample_latlon=sam_lat_lon,
            sample_material=sam_material,
            sample_reltooxygen=sam_rel_to_oxygen,
            sample_sampcollectdevice=sam_samp_collect_device,
            sample_sampmatprocess=sam_samp_mat_process,
            sample_sampsize=sam_samp_size,
            sample_subtype=sam_subtype,
            sample_supersite=sam_supersite,
            
            file_format=file_format,
            file_id=file_id,
            file_matrix_type=file_matrix_type,
            file_type=file_node_type,

            tag_term=tag_term
            )
        
ac_schema = graphene.Schema(query=Query)