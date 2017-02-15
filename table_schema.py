import graphene
from models import Pagination, FileHits, Aggregations, get_buckets, get_file_hits, get_pagination

# Can preload aggregate. Note that the get_buckets function needs to be changed 
# up a bit for files counts since it needs to pull ALL nodes that are tied to 
# some file and count those unique groups. Should be easy enough, just match by 
# the relevant edges. Simplified for now. 
dt = get_buckets("File.node_type","no","")
df = get_buckets("File.format","no","")

class Query(graphene.ObjectType):

    pagination = graphene.Field(Pagination, cy=graphene.String(description='Cypher WHERE parameters'), s=graphene.Int(description='size of subset to return'), f=graphene.Int(description='what position of the sort to start at'))
    hits = graphene.List(FileHits, cy=graphene.String(description='Cypher WHERE parameters'), s=graphene.Int(description='size of subset to return'), o=graphene.String(description='what to sort by'), f=graphene.Int(description='what position of the sort to start at'))
    aggregations = graphene.Field(Aggregations)

    def resolve_pagination(self, args, context, info):
        cy = args['cy'].replace("|",'"')
        return get_pagination(cy,args['s'],args['f'],'f')

    def resolve_hits(self, args, context, info):
        cy = args['cy'].replace("|",'"') # handle quotes for GQL
        o = args['o'].replace("file_name","Sample.id") # lose the portal ordering syntax
        o = o.replace(".raw","")
        if args['cy'] == "":
            return get_file_hits(args['s'],"Sample.id:asc",args['f'],"")
        else:
            return get_file_hits(args['s'],o,args['f'],cy)

    def resolve_aggregations(self, args, context, info):
        return Aggregations(dataType=dt, dataFormat=df)

# As noted above, going to hit Neo4j once and get everything then let GQL 
# do its magic client side to return the values that the user wants. 
table_schema = graphene.Schema(query=Query)
