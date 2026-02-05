# VerifyRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **str** |  | 
**options** | [**VerifyOptions**](VerifyOptions.md) |  | [optional] 

## Example

```python
from encypher.models.verify_request import VerifyRequest

# TODO update the JSON string below
json = "{}"
# create an instance of VerifyRequest from a JSON string
verify_request_instance = VerifyRequest.from_json(json)
# print the JSON string representation of the object
print(VerifyRequest.to_json())

# convert the object into a dict
verify_request_dict = verify_request_instance.to_dict()
# create an instance of VerifyRequest from a dict
verify_request_from_dict = VerifyRequest.from_dict(verify_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


