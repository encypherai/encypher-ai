# KeyRotateResponse

Response after rotating a key (includes new key).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**data** | **Dict[str, object]** |  | 
**warning** | **str** |  | [optional] [default to 'Store this key securely. It will not be shown again.']

## Example

```python
from encypher.models.key_rotate_response import KeyRotateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of KeyRotateResponse from a JSON string
key_rotate_response_instance = KeyRotateResponse.from_json(json)
# print the JSON string representation of the object
print(KeyRotateResponse.to_json())

# convert the object into a dict
key_rotate_response_dict = key_rotate_response_instance.to_dict()
# create an instance of KeyRotateResponse from a dict
key_rotate_response_from_dict = KeyRotateResponse.from_dict(key_rotate_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


