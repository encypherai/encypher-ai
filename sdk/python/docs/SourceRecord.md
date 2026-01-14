# SourceRecord

A single source record in the lookup results.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **str** | Source document ID | 
**organization_id** | **str** | Source organization ID | 
**organization_name** | **str** |  | [optional] 
**segment_hash** | **str** | Hash of the matched segment | 
**leaf_index** | **int** | Index in source Merkle tree | 
**merkle_root_hash** | **str** |  | [optional] 
**created_at** | **datetime** | When content was first registered | 
**signed_at** | **datetime** |  | [optional] 
**confidence** | **float** | Match confidence (0-1) | 
**authority_score** | **float** |  | [optional] 
**is_original** | **bool** | Whether this is the original source | 
**previous_source_id** | **str** |  | [optional] 
**next_source_id** | **str** |  | [optional] 
**metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from encypher.models.source_record import SourceRecord

# TODO update the JSON string below
json = "{}"
# create an instance of SourceRecord from a JSON string
source_record_instance = SourceRecord.from_json(json)
# print the JSON string representation of the object
print(SourceRecord.to_json())

# convert the object into a dict
source_record_dict = source_record_instance.to_dict()
# create an instance of SourceRecord from a dict
source_record_from_dict = SourceRecord.from_dict(source_record_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


