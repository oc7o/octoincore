import datetime
import typing
from decimal import Decimal
from typing import List, Optional

import strawberry
import strawberry_django_jwt.mutations as jwt_mutations
from django.db.models import Count

from .models import ExtendUser

# from octoincore.inventory.schema import ProductType


if typing.TYPE_CHECKING:
    from octoincore.inventory.schema import ProductType


@strawberry.type
class MeType:
    username: str
    email: str
    isStaff: bool
    isActive: bool
    isSuperuser: bool
    lastName: str
    firstName: str
    dateJoined: datetime.datetime | None
    lastLogin: datetime.datetime | None
    profileImage: str
    balance: Decimal


@strawberry.django.type(model=ExtendUser)
class UserType:
    username: str
    isStaff: bool
    isActive: bool
    isSuperuser: bool
    dateJoined: datetime.datetime
    profileImage: str
    products: typing.List[
        typing.Annotated["ProductType", strawberry.lazy("octoincore.inventory.schema")]
    ]


@strawberry.type
class UserQuery:
    @strawberry.field
    def me(self, info) -> Optional[MeType]:
        if info.context.request.user.is_authenticated:
            return MeType(
                username=info.context.request.user.username,
                email=info.context.request.user.email,
                isStaff=info.context.request.user.is_staff,
                isActive=info.context.request.user.is_active,
                isSuperuser=info.context.request.user.is_superuser,
                lastName=info.context.request.user.last_name,
                firstName=info.context.request.user.first_name,
                dateJoined=info.context.request.user.date_joined,
                lastLogin=info.context.request.user.last_login,
                profileImage=info.context.request.build_absolute_uri(
                    info.context.request.user.profile_image.url
                ),
                balance=info.context.request.user.balance,
            )
        return None

    @strawberry.field
    def top_20_users(self, info) -> List[UserType]:
        top_users = sorted(
            ExtendUser.objects.all(),
            key=lambda x: x.products_sold_this_month_count(),
            reverse=True,
        )[:20]

        top_user_types = []
        for user in top_users:
            top_user_types.append(
                UserType(
                    username=user.username,
                    isStaff=user.is_staff,
                    isActive=user.is_active,
                    isSuperuser=user.is_superuser,
                    dateJoined=user.date_joined,
                    profileImage=info.context.request.build_absolute_uri(
                        user.profile_image.url
                    ),
                    products=user.products.all(),
                )
            )
        return top_user_types

    @strawberry.field
    def user(self, info, username: str) -> UserType:
        user = ExtendUser.objects.get(username=username)
        return UserType(
            username=user.username,
            isStaff=user.is_staff,
            isActive=user.is_active,
            isSuperuser=user.is_superuser,
            dateJoined=user.date_joined,
            profileImage=info.context.request.build_absolute_uri(
                user.profile_image.url
            ),
            products=user.products.all(),
        )


@strawberry.type
class UserMutations:
    token_auth = jwt_mutations.ObtainJSONWebToken.obtain
    verify_token = jwt_mutations.Verify.verify
    refresh_token = jwt_mutations.Refresh.refresh
    delete_token_cookie = jwt_mutations.DeleteJSONWebTokenCookie.delete_cookie
