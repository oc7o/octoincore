import logging
import typing
from inspect import isawaitable

import strawberry
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model
from graphql import GraphQLResolveInfo
from graphql.error import GraphQLError
from strawberry.tools import merge_types
from strawberry.types import ExecutionContext
from strawberry_django_jwt import exceptions
from strawberry_django_jwt.middleware import JSONWebTokenMiddleware

from octoincore.basket.schema import BasketMutation, BasketQuery
from octoincore.captcha.schema import CaptchaMutation
from octoincore.inventory.models import Product
from octoincore.inventory.schema import InventoryMutation, InventoryQuery
from octoincore.payments.schema import PaymentsMutation, PaymentsQuery
from octoincore.users.schema import UserMutations, UserQuery

logger = logging.getLogger("strawberry.execution")


class MySchema(strawberry.Schema):
    def process_errors(
        self, errors: typing.List[GraphQLError], execution_context: ExecutionContext
    ) -> None:
        for error in errors:
            # A GraphQLError wraps the underlying error so we have to access it
            # through the `original_error` property
            # https://graphql-core-3.readthedocs.io/en/latest/modules/error.html#graphql.error.GraphQLError
            actual_error = error.original_error or error
            logger.error(actual_error, exc_info=actual_error)


class MyJSONWebTokenMiddleware(JSONWebTokenMiddleware):
    # https://github.com/KundaPanda/strawberry-django-jwt/issues/348
    def resolve(self, _next, root, info: GraphQLResolveInfo, *args, **kwargs):
        try:
            return super().resolve(_next, root, info, *args, **kwargs)
        except exceptions.JSONWebTokenError:
            result = _next(root, info, **kwargs)
            return result


Query = merge_types(
    "RootQuery", (UserQuery, InventoryQuery, PaymentsQuery, BasketQuery)
)
Mutation = merge_types(
    "RootMutation",
    (
        UserMutations,
        InventoryMutation,
        PaymentsMutation,
        CaptchaMutation,
        BasketMutation,
    ),
)

schema = MySchema(
    query=Query,
    mutation=Mutation,
    extensions=[
        MyJSONWebTokenMiddleware,
    ],
)
