# C2PAAssertionValidateResponse

Response schema for assertion validation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**valid** | **bool** |  | 
**assertions** | [**List[C2PAAssertionValidationResult]**](C2PAAssertionValidationResult.md) |  | 

## Example

```python
from encypher.models.c2_pa_assertion_validate_response import C2PAAssertionValidateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of C2PAAssertionValidateResponse from a JSON string
c2_pa_assertion_validate_response_instance = C2PAAssertionValidateResponse.from_json(json)
# print the JSON string representation of the object
print(C2PAAssertionValidateResponse.to_json())

# convert the object into a dict
c2_pa_assertion_validate_response_dict = c2_pa_assertion_validate_response_instance.to_dict()
# create an instance of C2PAAssertionValidateResponse from a dict
c2_pa_assertion_validate_response_from_dict = C2PAAssertionValidateResponse.from_dict(c2_pa_assertion_validate_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


