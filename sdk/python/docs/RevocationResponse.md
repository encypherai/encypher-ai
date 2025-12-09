# RevocationResponse

Response for revocation/reinstatement actions.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | 
**document_id** | **str** |  | 
**action** | **str** |  | 
**timestamp** | **str** |  | 
**message** | **str** |  | 

## Example

```python
from encypher.models.revocation_response import RevocationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RevocationResponse from a JSON string
revocation_response_instance = RevocationResponse.from_json(json)
# print the JSON string representation of the object
print(RevocationResponse.to_json())

# convert the object into a dict
revocation_response_dict = revocation_response_instance.to_dict()
# create an instance of RevocationResponse from a dict
revocation_response_from_dict = RevocationResponse.from_dict(revocation_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


