# RichVerifyResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**valid** | **bool** |  |
**verified_at** | **str** |  |
**document_id** | **str** |  |
**content_type** | **str** |  | [optional] [default to 'rich_article']
**text_verification** | [**TextVerificationResult**](TextVerificationResult.md) |  | [optional]
**image_verifications** | [**List[ImageVerificationResult]**](ImageVerificationResult.md) |  | [optional] [default to []]
**composite_manifest_valid** | **bool** |  |
**all_ingredients_verified** | **bool** |  |
**cryptographically_verified** | **bool** |  | [optional]
**historically_signed_by_us** | **bool** |  | [optional]
**overall_status** | **str** |  | [optional]
**signer_identity** | [**SignerIdentity**](SignerIdentity.md) |  | [optional]
**error** | **str** |  | [optional]
**correlation_id** | **str** |  |

## Example

```python
from encypher.models.rich_verify_response import RichVerifyResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RichVerifyResponse from a JSON string
rich_verify_response_instance = RichVerifyResponse.from_json(json)
# print the JSON string representation of the object
print(RichVerifyResponse.to_json())

# convert the object into a dict
rich_verify_response_dict = rich_verify_response_instance.to_dict()
# create an instance of RichVerifyResponse from a dict
rich_verify_response_from_dict = RichVerifyResponse.from_dict(rich_verify_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
