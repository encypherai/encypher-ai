# ProgressionStage

Single stage in the publisher value journey.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**stage** | **int** |  |
**label** | **str** |  |
**description** | **str** |  |
**status** | **str** |  |
**metric_value** | **int** |  | [optional]
**metric_label** | **str** |  | [optional]
**metric_target** | **int** |  | [optional]
**cta_label** | **str** |  | [optional]
**cta_url** | **str** |  | [optional]

## Example

```python
from encypher.models.progression_stage import ProgressionStage

# TODO update the JSON string below
json = "{}"
# create an instance of ProgressionStage from a JSON string
progression_stage_instance = ProgressionStage.from_json(json)
# print the JSON string representation of the object
print(ProgressionStage.to_json())

# convert the object into a dict
progression_stage_dict = progression_stage_instance.to_dict()
# create an instance of ProgressionStage from a dict
progression_stage_from_dict = ProgressionStage.from_dict(progression_stage_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
