# ContentAccessLogResponse

Schema for content access log response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**agreement_id** | **str** |  | 
**content_id** | **str** |  | 
**member_id** | **str** |  | 
**accessed_at** | **datetime** |  | 
**access_type** | **str** |  | 
**ai_company_name** | **str** |  | 

## Example

```python
from encypher.models.content_access_log_response import ContentAccessLogResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ContentAccessLogResponse from a JSON string
content_access_log_response_instance = ContentAccessLogResponse.from_json(json)
# print the JSON string representation of the object
print(ContentAccessLogResponse.to_json())

# convert the object into a dict
content_access_log_response_dict = content_access_log_response_instance.to_dict()
# create an instance of ContentAccessLogResponse from a dict
content_access_log_response_from_dict = ContentAccessLogResponse.from_dict(content_access_log_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


