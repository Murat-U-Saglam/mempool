from confluent_kafka.schema_registry.json_schema import JSONDeserializer # type: ignore
from mempool.config.provider import get_schema_registry
from mempool.stream.producer.topics import get_schema   


async def get_deserializer():
    json = await get_schema()
    schema_registry = await get_schema_registry()
    return JSONDeserializer(
        schema_str=json, schema_registry_client=schema_registry
    )  # Convert schema to string
    
    
