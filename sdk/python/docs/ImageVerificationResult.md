# ImageVerificationResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**image_id** | **str** |  | [optional]
**filename** | **str** |  | [optional]
**valid** | **bool** |  |
**c2pa_manifest_valid** | **bool** |  |
**hash_matches** | **bool** |  |
**trustmark_valid** | **bool** |  | [optional]
**c2pa_instance_id** | **str** |  | [optional]
**signer** | **str** |  | [optional]
**signed_at** | **str** |  | [optional]
**cryptographically_verified** | **bool** |  | [optional]
**historically_signed_by_us** | **bool** |  | [optional]
**overall_status** | **str** |  | [optional]
**error** | **str** |  | [optional]

## Example

```python
from encypher.models.image_verification_result import ImageVerificationResult

# TODO update the JSON string below
json = "{}"
# create an instance of ImageVerificationResult from a JSON string
image_verification_result_instance = ImageVerificationResult.from_json(json)
# print the JSON string representation of the object
print(ImageVerificationResult.to_json())

# convert the object into a dict
image_verification_result_dict = image_verification_result_instance.to_dict()
# create an instance of ImageVerificationResult from a dict
image_verification_result_from_dict = ImageVerificationResult.from_dict(image_verification_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
