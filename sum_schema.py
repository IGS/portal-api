import graphene
from models import FileSize, SBucketCounter, PieCharts
from query import get_buckets, get_total_file_size, get_pie_chart_summary

# Can preload default counts for fast loading, user interaction with facets or
# queries will then refine these counts.
pie_sum = get_pie_chart_summary("")

class Query(graphene.ObjectType):

    pie_charts = graphene.Field(PieCharts, cy=graphene.String(description='Cypher WHERE parameters'), name="pie_charts")

    def resolve_pie_charts(self, args, context, info):
        # accept the pipes and convert to quotes again now that it's been passed across the URL
        cy = args['cy'].replace("|",'"') 
        if cy == "":
            return pie_sum
        else:
            return get_pie_chart_summary(cy)

# As noted above, going to hit Neo4j once and get everything then let GQL 
# do its magic client side to return the values that the user wants. 
sum_schema = graphene.Schema(query=Query)
