import graphene
from models import Project 
from query import get_proj_data

class Query(graphene.ObjectType):

    caseId = graphene.String(name="case_id", id=graphene.String(description='Subject ID to query on'))
    project = graphene.Field(Project, id=graphene.String(description='Subject ID to query on'))

    def resolve_caseId(self, args, context, info):
        return args['id']

    def resolve_project(self, args, context, info):
        return get_proj_data(args['id'])

indiv_cases_schema = graphene.Schema(query=Query)
