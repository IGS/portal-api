import graphene
from models import Pagination, FileHits, Aggregations
from query import get_buckets, get_file_hits, get_pagination, get_sample_count

# Can preload aggregate. Note that the get_buckets function needs to be changed 
# up a bit for files counts since it needs to pull ALL nodes that are tied to 
# some file and count those unique groups. Should be easy enough, just match by 
# the relevant edges. Simplified for now. 
ft = get_buckets("F.node_type","no","")
ff = get_buckets("F.format","no","")
fa = get_buckets("F.annotation_pipeline","no","")
fm = get_buckets("F.matrix_type","no","")

class Query(graphene.ObjectType):

    pagination = graphene.Field(Pagination, cy=graphene.String(description='Cypher WHERE parameters'), s=graphene.Int(description='size of subset to return'), f=graphene.Int(description='what position of the sort to start at'))
    hits = graphene.List(FileHits, cy=graphene.String(description='Cypher WHERE parameters'), s=graphene.Int(description='size of subset to return'), o=graphene.String(description='what to sort by'), f=graphene.Int(description='what position of the sort to start at'))
    sample_count = graphene.Int(name="sample_count", cy=graphene.String(description='Cypher to count samples by'))
    aggregations = graphene.Field(Aggregations)

    def resolve_pagination(self, args, context, info):
        cy = args['cy'].replace("|",'"')
        return get_pagination(cy,args['s'],args['f'],'f')

    def resolve_hits(self, args, context, info):
        cy = args['cy'].replace("|",'"') # handle quotes for GQL
        if not args['o']:
            if args['cy'] == "":
                return get_file_hits(args['s'],'',args['f'],"")
            else:
                return get_file_hits(args['s'],'',args['f'],cy)
        elif args['cy'] == "":
            return get_file_hits(args['s'],args['o'],args['f'],"")
        else:
            return get_file_hits(args['s'],args['o'],args['f'],cy)

    def resolve_sample_count(self, args, context, info):
        cy = args['cy'].replace("|",'"')
        return get_sample_count(cy)

    def resolve_aggregations(self, args, context, info):
        return Aggregations(file_type=ft, 
            file_format=ff,
            file_annotation_pipeline=fa,
            file_matrix_type=fm
        )

# As noted above, going to hit Neo4j once and get everything then let GQL 
# do its magic client side to return the values that the user wants. 
table_schema = graphene.Schema(query=Query)
