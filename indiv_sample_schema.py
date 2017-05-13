import graphene
from models import Project, IndivSample
from query import get_proj_data,get_sample_data

class Query(graphene.ObjectType):

    sample = graphene.Field(IndivSample, id=graphene.String(description='Sample ID to query on'))
    project = graphene.Field(Project, id=graphene.String(description='Subject ID to query on'))

    def resolve_sample(self, args, context, info):
        return get_sample_data(args['id'])

    def resolve_project(self, args, context, info):
        return get_proj_data(args['id'])

indiv_sample_schema = graphene.Schema(query=Query)
