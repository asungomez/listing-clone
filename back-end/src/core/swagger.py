from typing import Any, Callable, List, Optional, cast

from app import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, unset


def swagger_authenticated_schema(
    method: Optional[str] = None,
    methods: Optional[List[str]] = None,
    auto_schema: Any = unset,
    request_body: Optional[Any] = None,
    query_serializer: Optional[Any] = None,
    manual_parameters: Optional[List[openapi.Parameter]] = None,
    operation_id: Optional[str] = None,
    operation_description: Optional[str] = None,
    operation_summary: Optional[str] = None,
    security: Optional[Any] = None,
    deprecated: Optional[bool] = None,
    responses: Optional[Any] = None,
    field_inspectors: Optional[Any] = None,
    filter_inspectors: Optional[Any] = None,
    paginator_inspectors: Optional[Any] = None,
    tags: Optional[Any] = None,
    produces: Optional[Any] = None,
    consumes: Optional[Any] = None,
    **extra_overrides: Any,
) -> Callable[[Any], Any]:
    """
    Decorator for swagger_auto_schema with authentication headers
    """

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

    decorator = cast(Callable[[Any], Any], swagger_auto_schema(
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
    ))

    return decorator


def swagger_typed_schema(
    method: Optional[str] = None,
    methods: Optional[List[str]] = None,
    auto_schema: Any = unset,
    request_body: Optional[Any] = None,
    query_serializer: Optional[Any] = None,
    manual_parameters: Optional[List[openapi.Parameter]] = None,
    operation_id: Optional[str] = None,
    operation_description: Optional[str] = None,
    operation_summary: Optional[str] = None,
    security: Optional[Any] = None,
    deprecated: Optional[bool] = None,
    responses: Optional[Any] = None,
    field_inspectors: Optional[Any] = None,
    filter_inspectors: Optional[Any] = None,
    paginator_inspectors: Optional[Any] = None,
    tags: Optional[Any] = None,
    produces: Optional[Any] = None,
    consumes: Optional[Any] = None,
    **extra_overrides: Any,
) -> Callable[[Any], Any]:
    """
    Decorator for swagger_auto_schema with type hints
    """

    decorator = cast(Callable[[Any], Any], swagger_auto_schema(
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
    ))

    return decorator
