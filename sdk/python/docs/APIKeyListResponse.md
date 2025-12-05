# APIKeyListResponse

Response schema for listing API keys.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**keys** | **List[Dict[str, object]]** | List of API keys | 
**total** | **int** | Total number of keys | 

## Example

```python
from encypher.models.api_key_list_response import APIKeyListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of APIKeyListResponse from a JSON string
api_key_list_response_instance = APIKeyListResponse.from_json(json)
# print the JSON string representation of the object
print(APIKeyListResponse.to_json())

# convert the object into a dict
api_key_list_response_dict = api_key_list_response_instance.to_dict()
# create an instance of APIKeyListResponse from a dict
api_key_list_response_from_dict = APIKeyListResponse.from_dict(api_key_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


