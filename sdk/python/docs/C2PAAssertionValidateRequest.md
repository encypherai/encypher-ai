# C2PAAssertionValidateRequest

Request schema for validating a C2PA assertion.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**label** | **str** | Assertion label to validate | 
**data** | **Dict[str, object]** | Assertion data to validate | 

## Example

```python
from encypher.models.c2_pa_assertion_validate_request import C2PAAssertionValidateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of C2PAAssertionValidateRequest from a JSON string
c2_pa_assertion_validate_request_instance = C2PAAssertionValidateRequest.from_json(json)
# print the JSON string representation of the object
print(C2PAAssertionValidateRequest.to_json())

# convert the object into a dict
c2_pa_assertion_validate_request_dict = c2_pa_assertion_validate_request_instance.to_dict()
# create an instance of C2PAAssertionValidateRequest from a dict
c2_pa_assertion_validate_request_from_dict = C2PAAssertionValidateRequest.from_dict(c2_pa_assertion_validate_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


