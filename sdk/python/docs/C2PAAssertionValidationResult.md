# C2PAAssertionValidationResult

Validation result for a single assertion.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**label** | **str** |  | 
**valid** | **bool** |  | 
**errors** | **List[str]** |  | [optional] 
**warnings** | **List[str]** |  | [optional] 

## Example

```python
from encypher.models.c2_pa_assertion_validation_result import C2PAAssertionValidationResult

# TODO update the JSON string below
json = "{}"
# create an instance of C2PAAssertionValidationResult from a JSON string
c2_pa_assertion_validation_result_instance = C2PAAssertionValidationResult.from_json(json)
# print the JSON string representation of the object
print(C2PAAssertionValidationResult.to_json())

# convert the object into a dict
c2_pa_assertion_validation_result_dict = c2_pa_assertion_validation_result_instance.to_dict()
# create an instance of C2PAAssertionValidationResult from a dict
c2_pa_assertion_validation_result_from_dict = C2PAAssertionValidationResult.from_dict(c2_pa_assertion_validation_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


