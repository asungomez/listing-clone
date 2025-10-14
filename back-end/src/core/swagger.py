from typing import Callable

from app import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, unset


def swagger_authenticated_schema(
    method=None,
    methods=None,
    auto_schema=unset,
    request_body=None,
    query_serializer=None,
    manual_parameters=None,
    operation_id=None,
    operation_description=None,
    operation_summary=None,
    security=None,
    deprecated=None,
    responses=None,
    field_inspectors=None,
    filter_inspectors=None,
    paginator_inspectors=None,
    tags=None,
    produces=None,
    consumes=None,
    **extra_overrides,
) -> Callable:

    if manual_parameters is None:
        manual_parameters = []
    manual_parameters.append(
        openapi.Parameter(
            "Authorization",
            openapi.IN_HEADER,
            description="Authorization",
            type=openapi.TYPE_STRING,
            required=False,
        )
    )
    manual_parameters.append(
        openapi.Parameter(
            settings.CUSTOM_HEADER_MOCK_SESSION_USER_ID,
            openapi.IN_HEADER,
            description="Mock Session User Id",
            type=openapi.TYPE_STRING,
            required=False,
        )
    )

    return swagger_auto_schema(
      method=method,
      methods=methods,
      auto_schema=auto_schema,
      request_body=request_body,
      query_serializer=query_serializer,
      manual_parameters=manual_parameters,
      operation_id=operation_id,
      operation_description=operation_description,
      operation_summary=operation_summary,
      security=security,
      deprecated=deprecated,
      responses=responses,
      field_inspectors=field_inspectors,
      filter_inspectors=filter_inspectors,
      paginator_inspectors=paginator_inspectors,
      tags=tags,
      produces=produces,
      consumes=consumes,
      **extra_overrides,
    )
