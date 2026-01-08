# QuotaResponse

Response for quota endpoint.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**data** | [**QuotaInfo**](QuotaInfo.md) |  | 

## Example

```python
from encypher.models.quota_response import QuotaResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QuotaResponse from a JSON string
quota_response_instance = QuotaResponse.from_json(json)
# print the JSON string representation of the object
print(QuotaResponse.to_json())

# convert the object into a dict
quota_response_dict = quota_response_instance.to_dict()
# create an instance of QuotaResponse from a dict
quota_response_from_dict = QuotaResponse.from_dict(quota_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


