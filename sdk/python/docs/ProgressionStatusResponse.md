# ProgressionStatusResponse

Publisher progression status across the 6-stage value journey.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**organization_id** | **str** |  |
**current_stage** | **int** |  |
**stages** | [**List[ProgressionStage]**](ProgressionStage.md) |  |
**notice_ready** | **bool** |  |
**notice_verification_threshold** | **int** |  |
**total_documents_signed** | **int** |  |
**total_external_verifications** | **int** |  |
**coalition_active** | **bool** |  |
**total_earnings_cents** | **int** |  |

## Example

```python
from encypher.models.progression_status_response import ProgressionStatusResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ProgressionStatusResponse from a JSON string
progression_status_response_instance = ProgressionStatusResponse.from_json(json)
# print the JSON string representation of the object
print(ProgressionStatusResponse.to_json())

# convert the object into a dict
progression_status_response_dict = progression_status_response_instance.to_dict()
# create an instance of ProgressionStatusResponse from a dict
progression_status_response_from_dict = ProgressionStatusResponse.from_dict(progression_status_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
