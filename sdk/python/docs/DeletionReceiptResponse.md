# DeletionReceiptResponse

Deletion receipt for compliance documentation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**request_id** | **str** |  |
**organization_id** | **str** |  |
**scope** | **str** |  |
**requested_at** | **str** |  |
**completed_at** | **str** |  |
**status** | **str** |  |
**data_categories_deleted** | **List[str]** |  |
**data_categories_retained** | **List[str]** |  |
**retention_reasons** | **Dict[str, str]** |  |

## Example

```python
from encypher.models.deletion_receipt_response import DeletionReceiptResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DeletionReceiptResponse from a JSON string
deletion_receipt_response_instance = DeletionReceiptResponse.from_json(json)
# print the JSON string representation of the object
print(DeletionReceiptResponse.to_json())

# convert the object into a dict
deletion_receipt_response_dict = deletion_receipt_response_instance.to_dict()
# create an instance of DeletionReceiptResponse from a dict
deletion_receipt_response_from_dict = DeletionReceiptResponse.from_dict(deletion_receipt_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
