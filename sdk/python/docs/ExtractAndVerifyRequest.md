# ExtractAndVerifyRequest

Request to extract and verify invisible embedding from text.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **str** | Text with invisible embedding | 

## Example

```python
from encypher.models.extract_and_verify_request import ExtractAndVerifyRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ExtractAndVerifyRequest from a JSON string
extract_and_verify_request_instance = ExtractAndVerifyRequest.from_json(json)
# print the JSON string representation of the object
print(ExtractAndVerifyRequest.to_json())

# convert the object into a dict
extract_and_verify_request_dict = extract_and_verify_request_instance.to_dict()
# create an instance of ExtractAndVerifyRequest from a dict
extract_and_verify_request_from_dict = ExtractAndVerifyRequest.from_dict(extract_and_verify_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


