# CdnVerifyResponse

Response for POST /cdn/verify and POST /cdn/verify/url.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**verdict** | **str** |  |
**verification_path** | **str** |  |
**record_id** | **str** |  | [optional]
**manifest** | **Dict[str, object]** |  | [optional]
**hamming_distance** | **int** |  | [optional]
**confidence** | **float** |  | [optional]

## Example

```python
from encypher.models.cdn_verify_response import CdnVerifyResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CdnVerifyResponse from a JSON string
cdn_verify_response_instance = CdnVerifyResponse.from_json(json)
# print the JSON string representation of the object
print(CdnVerifyResponse.to_json())

# convert the object into a dict
cdn_verify_response_dict = cdn_verify_response_instance.to_dict()
# create an instance of CdnVerifyResponse from a dict
cdn_verify_response_from_dict = CdnVerifyResponse.from_dict(cdn_verify_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
