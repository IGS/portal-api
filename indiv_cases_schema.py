import graphene
from graphene import relay
from models import Project, get_proj_data

class Query(graphene.ObjectType):

    caseId = graphene.String(name="case_id", id=graphene.String(description='Subject ID to query on'))
    project = graphene.Field(Project, id=graphene.String(description='Subject ID to query on'))

    def resolve_caseId(self, args, context, info):
        return args['id']

    def resolve_project(self, args, context, info):
        return get_proj_data(args['id'])

# As noted above, going to hit Neo4j once and get everything then let GQL 
# do its magic client side to return the values that the user wants. 
indiv_cases_schema = graphene.Schema(query=Query)
