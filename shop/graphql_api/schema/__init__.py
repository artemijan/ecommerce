import graphene
from .catalogue import Query

schema = graphene.Schema(query=Query)
