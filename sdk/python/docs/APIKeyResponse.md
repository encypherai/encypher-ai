# APIKeyResponse

Response schema for API key.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**api_key** | **str** | Generated API key | 
**key_id** | **str** | API key identifier | 
**organization_id** | **str** | Organization identifier | 
**tier** | **str** | Organization tier | 
**created_at** | **datetime** | Creation timestamp | 
**expires_at** | **datetime** |  | [optional] 

## Example

```python
from encypher.models.api_key_response import APIKeyResponse

# TODO update the JSON string below
json = "{}"
# create an instance of APIKeyResponse from a JSON string
api_key_response_instance = APIKeyResponse.from_json(json)
# print the JSON string representation of the object
print(APIKeyResponse.to_json())

# convert the object into a dict
api_key_response_dict = api_key_response_instance.to_dict()
# create an instance of APIKeyResponse from a dict
api_key_response_from_dict = APIKeyResponse.from_dict(api_key_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


