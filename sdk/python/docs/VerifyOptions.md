# VerifyOptions

Optional parameters for verification request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**include_merkle_proof** | **bool** | Include Merkle proof details (requires API key) | [optional] [default to False]
**include_raw_manifest** | **bool** | Include raw C2PA manifest data | [optional] [default to False]

## Example

```python
from encypher.models.verify_options import VerifyOptions

# TODO update the JSON string below
json = "{}"
# create an instance of VerifyOptions from a JSON string
verify_options_instance = VerifyOptions.from_json(json)
# print the JSON string representation of the object
print(VerifyOptions.to_json())

# convert the object into a dict
verify_options_dict = verify_options_instance.to_dict()
# create an instance of VerifyOptions from a dict
verify_options_from_dict = VerifyOptions.from_dict(verify_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


