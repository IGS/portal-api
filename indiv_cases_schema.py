import graphene
from models import Project, IndivCase
from query import get_proj_data,get_case_data

class Query(graphene.ObjectType):

    caseId = graphene.Field(IndivCase, id=graphene.String(description='Sample ID to query on'))
    project = graphene.Field(Project, id=graphene.String(description='Subject ID to query on'))

    def resolve_caseId(self, args, context, info):
        return get_case_data(args['id'])

    def resolve_project(self, args, context, info):
        return get_proj_data(args['id'])

indiv_cases_schema = graphene.Schema(query=Query)
