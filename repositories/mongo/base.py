from datetime import datetime, timezone

from typing import Type, TypeVar, Generic, List, Optional, Any, Dict

from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from bson.errors import InvalidId

from pydantic import TypeAdapter


T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, collection: AsyncIOMotorCollection, model: Type[T]):
        self.collection = collection
        self.model = model
        self.adapter = TypeAdapter(List[model])
        self.filter = FilterConverter()

    async def create(self, data: T) -> T | None:
        doc = data.model_dump()
        result = await self.collection.insert_one(doc)

        doc["_id"] = result.inserted_id

        return self.model.model_validate(doc)
    
    async def get_one(self, filter: dict, *, sort: list[tuple] | None = None, ignore_key: str | None = None) -> Optional[T]:
        new_filter = self.filter._convert_filter(filter or {}, ignore_key=ignore_key)

        if sort is not None:
            doc = await self.collection.find_one(new_filter, sort=sort)
        else:
            doc = await self.collection.find_one(new_filter)

        if not doc:
            return None
        
        return self.model.model_validate(doc)
    
    async def get_many(self, filter: dict, is_limit: bool = False, **kwargs) -> List[T] | None:
        new_filter = self.filter._convert_filter(filter or {}, ignore_key="category_path_ids")

        if is_limit:
            if not kwargs.get("limit"):
                raise ValueError("'kwargs' must have a 'limit' key with 'int' value")
            
            cursor = self.collection.find(new_filter).limit(kwargs.get("limit"))
            docs = await cursor.to_list(kwargs.get("limit"))
        else:
            cursor = self.collection.find(new_filter)
            docs = await cursor.to_list()

        return self.adapter.validate_python(docs)
    
    async def update(self, filter: dict, update_data: dict) -> Optional[T] | None:
        new_filter = self.filter._convert_filter(filter or {})
        await self.collection.update_one(
            new_filter,
            {"$set": {
                **update_data,
                "updated_at": datetime.now(timezone.utc)
                }
            }
        )

        return await self.get_one(new_filter)
    
    async def delete(self, filter: dict) -> bool:
        new_filter = self.filter._convert_filter(filter or {}, ignore_key="category_path_ids")
        result = await self.collection.delete_one(new_filter)

        return result.deleted_count > 0
    
    async def delete_many(self, filter: dict) -> bool:
        new_filter = self.filter._convert_filter(filter or {}, ignore_key="category_path_ids")
        result = await self.collection.delete_many(new_filter)

        return result.deleted_count > 0
    
    async def count(self, filter: dict) -> int:
        new_filter = self.filter._convert_filter(filter or {}, ignore_key="category_path_ids")

        return await self.collection.count_documents(new_filter)
    
    async def is_exists(self, filter: dict) -> bool:
        new_filter = self.filter._convert_filter(filter or {}, ignore_key="category-path_ids")
        doc = await self.collection.find_one(new_filter)

        return bool(doc)
    
    async def get_value(self, filter: dict, key: str) -> str | Any:
        new_filter = self.filter._convert_filter(filter or {}, ignore_key="category_path_ids")
        doc = await self.collection.find_one(new_filter)

        return doc.get(key, None)


class FilterConverter:

    FIELD_MAP = {
        "category_path_ids": "path_ids",
        "id": "_id",
    }

    def _convert_filter(self, filter: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        ignore_key = kwargs.get("ignore_key")

        new_filter = {}

        for key, value in filter.items():

            if ignore_key and key == ignore_key:
                new_filter[key] = value
                continue

            db_key = self.FIELD_MAP.get(key, key)

            if db_key == "path_ids":

                if isinstance(value, list):
                    new_filter[db_key] = {"$in": self._convert_value(value)}
                    continue

                new_filter[db_key] = self._convert_value(value)
                continue

            new_filter[db_key] = self._convert_value(value)

        return new_filter
    
    def is_object_id(self, value: Any) -> bool:
        try:
            ObjectId(value)
            return True
        except (InvalidId, TypeError):
            return False

    def _convert_value(self, value: Any) -> Any:
        if isinstance(value, str) and self.is_object_id(value):
            return ObjectId(value)

        if isinstance(value, list):
            return [self._convert_value(v) for v in value]

        if isinstance(value, dict):
            return {k: self._convert_value(v) for k, v in value.items()}

        return value