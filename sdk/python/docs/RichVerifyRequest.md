# RichVerifyRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **str** |  |

## Example

```python
from encypher.models.rich_verify_request import RichVerifyRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RichVerifyRequest from a JSON string
rich_verify_request_instance = RichVerifyRequest.from_json(json)
# print the JSON string representation of the object
print(RichVerifyRequest.to_json())

# convert the object into a dict
rich_verify_request_dict = rich_verify_request_instance.to_dict()
# create an instance of RichVerifyRequest from a dict
rich_verify_request_from_dict = RichVerifyRequest.from_dict(rich_verify_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
