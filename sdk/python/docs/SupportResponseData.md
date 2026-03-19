# SupportResponseData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** |  |
**sent_at** | **str** |  |

## Example

```python
from encypher.models.support_response_data import SupportResponseData

# TODO update the JSON string below
json = "{}"
# create an instance of SupportResponseData from a JSON string
support_response_data_instance = SupportResponseData.from_json(json)
# print the JSON string representation of the object
print(SupportResponseData.to_json())

# convert the object into a dict
support_response_data_dict = support_response_data_instance.to_dict()
# create an instance of SupportResponseData from a dict
support_response_data_from_dict = SupportResponseData.from_dict(support_response_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
