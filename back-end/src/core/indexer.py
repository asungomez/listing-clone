from abc import ABC
from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar

import requests
from app import settings
from django.db.models import Model
from rest_framework.serializers import ModelSerializer

GenericModel = TypeVar("GenericModel", bound=Model)


class Indexer:
    """
    Indexer class for managing the Solr index.
    """

    url: str
    override_types: Optional[Dict[str, str]]

    def __init__(self) -> None:
        self.url = f"{settings.SOLR_URL}/{settings.SOLR_CORE}"

    def build_query(self, query: Dict[str, Any]) -> str:
        """
        Build a query string from a dictionary of parameters.

        :param query: The query to build.
        :return: The built query.
        """
        transformed_query = self.transform_data(query)

        def escape_value(value: Any) -> str:
            if isinstance(value, str):
                return value.replace(":", r"\:")
            return str(value)

        return "&".join([
            f"{key}:{
                escape_value(value)
                }" for key, value in transformed_query.items()
            ])

    def update(self, data: Dict[str, Any]) -> None:
        """
        Index a new document into the Solr index.

        :param data: The data to index.
        """
        transformed_data = self.transform_data(data)
        response = requests.post(
            f"{self.url}/update?commit=true",
            json=[transformed_data],
            headers={"Content-Type": "application/json"}
            )
        response.raise_for_status()

    def select(
        self,
        query: str,
        start: Optional[int] = None,
        rows: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Search the Solr index for a given query.

        :param query: The query to search for.
        :return: The response from the Solr index.
        """
        try:
            url = f"{self.url}/select?q={query}&wt=json"
            if rows is not None:
                url = f"{url}&rows={rows}"
            if start is not None:
                url = f"{url}&start={start}"
            response = requests.get(url)
            response.raise_for_status()
            response_body: Dict[str, Any] = response.json()
            return response_body
        except Exception as e:
            raise e

    def reverse_transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reverse transform the data to be indexed. Remove type suffix from the
        fields.

        :param data: The data to reverse transform.
        :return: The reverse transformed data.
        """
        reverse_transformed_data: Dict[str, Any] = {}
        for key, value in data.items():
            if key == "id":
                reverse_transformed_data[key] = value
            elif key.endswith("_s") or key.endswith("_t"):
                reverse_transformed_data[key[:-2]] = value
            elif key.endswith("_i"):
                reverse_transformed_data[key[:-2]] = int(value)
            elif key.endswith("_f"):
                reverse_transformed_data[key[:-2]] = float(value)
            elif key.endswith("_b"):
                reverse_transformed_data[key[:-2]] = bool(value)
        return reverse_transformed_data

    def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform the data to be indexed. Add type suffix to the fields.

        :param data: The data to transform.
        :return: The transformed data.
        """
        transformed_data: Dict[str, Any] = {}
        for key, value in data.items():
            if value is None:
                continue
            if key == "id":
                transformed_data[key] = value
            elif key == "_childDocuments_":
                transformed_data[key] = [
                    self.transform_data(child)
                    for child in value
                ]
            elif self.override_types and key in self.override_types:
                transformed_data[f"{key}_{self.override_types[key]}"] = value
            elif isinstance(value, str):
                transformed_data[f"{key}_s"] = value
            elif isinstance(value, bool):
                transformed_data[f"{key}_b"] = value
            elif isinstance(value, int):
                transformed_data[f"{key}_i"] = value
            elif isinstance(value, float):
                transformed_data[f"{key}_f"] = value
            else:
                transformed_data[f"{key}_s"] = str(value)
        return transformed_data


class ModelIndexer(Indexer, ABC, Generic[GenericModel]):
    """
    Indexer class for managing the Solr index for a Django model.
    """

    serializer_class: Type[ModelSerializer[GenericModel]]

    def __init__(self, serializer_class: Type[ModelSerializer[GenericModel]]):
        self.serializer_class = serializer_class
        super().__init__()

    def add(self, instance: GenericModel) -> None:
        """
        Index a new document into the Solr index.

        :param instance: The instance to index.
        """
        serializer = self.serializer_class(instance)
        data = serializer.data
        self.update(data)

    def all(self, offset: int, page_size: int) -> Tuple[
        List[GenericModel],
        int
    ]:
        """
        Get all instances from the Solr index.
        """
        return self.search({}, offset, page_size)

    def search(
        self,
        query: Dict[str, Any],
        offset: int,
        page_size: int,
    ) -> tuple[List[GenericModel], int]:
        """
        Search the Solr index for a given query with pagination.

        :param query: The query to search for.
        :param offset: The starting offset of the results.
        :param page_size: The number of results to return.
        :return: A tuple of (results, total_count).
        """
        if "id" not in query:
            query["id"] = "*"
        query_str = self.build_query(query)
        response = self.select(query_str, start=offset, rows=page_size)
        resp_obj = response.get("response", {})
        docs = resp_obj.get("docs", [])
        total_count: int = int(resp_obj.get("numFound", 0))
        model_cls: Type[GenericModel] = self.serializer_class.Meta.model
        results: List[GenericModel] = []
        for doc in docs:
            transformed_doc = self.reverse_transform_data(doc)
            serializer = self.serializer_class(data=transformed_doc)
            if serializer.is_valid():
                instance = model_cls(**transformed_doc)
                results.append(instance)
        return results, total_count

    def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        transformed_data = super().transform_data(data)
        if "id" in transformed_data:
            id_value = transformed_data["id"]
            class_name = self.serializer_class.Meta.model.__name__.lower()
            transformed_data["id"] = f"{class_name}:{id_value}"
        return transformed_data

    def reverse_transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        reverse_transformed_data = super().reverse_transform_data(data)
        if "id" in reverse_transformed_data:
            id_value = reverse_transformed_data["id"]
            reverse_transformed_data["id"] = int(id_value.split(":")[1])
        return reverse_transformed_data
