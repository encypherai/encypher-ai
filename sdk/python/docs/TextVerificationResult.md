# TextVerificationResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**valid** | **bool** |  |
**total_segments** | **int** |  | [optional]
**tampered_segments** | **List[int]** |  | [optional] [default to []]
**merkle_root_verified** | **bool** |  | [optional]
**error** | **str** |  | [optional]

## Example

```python
from encypher.models.text_verification_result import TextVerificationResult

# TODO update the JSON string below
json = "{}"
# create an instance of TextVerificationResult from a JSON string
text_verification_result_instance = TextVerificationResult.from_json(json)
# print the JSON string representation of the object
print(TextVerificationResult.to_json())

# convert the object into a dict
text_verification_result_dict = text_verification_result_instance.to_dict()
# create an instance of TextVerificationResult from a dict
text_verification_result_from_dict = TextVerificationResult.from_dict(text_verification_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
