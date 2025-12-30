# KeyCreateResponse

Response after creating a key (includes full key - only shown once).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**data** | **Dict[str, object]** |  | 
**warning** | **str** |  | [optional] [default to 'Store this key securely. It will not be shown again.']

## Example

```python
from encypher.models.key_create_response import KeyCreateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of KeyCreateResponse from a JSON string
key_create_response_instance = KeyCreateResponse.from_json(json)
# print the JSON string representation of the object
print(KeyCreateResponse.to_json())

# convert the object into a dict
key_create_response_dict = key_create_response_instance.to_dict()
# create an instance of KeyCreateResponse from a dict
key_create_response_from_dict = KeyCreateResponse.from_dict(key_create_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


