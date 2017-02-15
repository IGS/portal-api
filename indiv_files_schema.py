import graphene
from graphene import relay
from models import FileHits, get_file_data 

# Unlike the others, don't want to preload here. Load on call from each unique sample ID

class Query(graphene.ObjectType):

    fileHit = graphene.Field(FileHits, id=graphene.String(description='Sample ID to query on'))

    def resolve_fileHit(self, args, context, info):
        return get_file_data(args['id'])

# As noted above, going to hit Neo4j once and get everything then let GQL 
# do its magic client side to return the values that the user wants. 
indiv_files_schema = graphene.Schema(query=Query)
