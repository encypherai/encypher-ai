# PublicKeyListResponse

Response for listing organization's public keys.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**data** | **Dict[str, object]** |  | [optional] 

## Example

```python
from encypher.models.public_key_list_response import PublicKeyListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PublicKeyListResponse from a JSON string
public_key_list_response_instance = PublicKeyListResponse.from_json(json)
# print the JSON string representation of the object
print(PublicKeyListResponse.to_json())

# convert the object into a dict
public_key_list_response_dict = public_key_list_response_instance.to_dict()
# create an instance of PublicKeyListResponse from a dict
public_key_list_response_from_dict = PublicKeyListResponse.from_dict(public_key_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


