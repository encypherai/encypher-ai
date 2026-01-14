# FingerprintMatch

Details of a detected fingerprint match.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**fingerprint_id** | **str** | Matched fingerprint ID | 
**document_id** | **str** | Source document ID | 
**organization_id** | **str** | Source organization ID | 
**confidence** | **float** | Detection confidence (0-1) | 
**markers_found** | **int** | Number of markers detected | 
**markers_expected** | **int** | Number of markers expected | 
**marker_positions** | **List[int]** |  | [optional] 
**created_at** | **datetime** | When fingerprint was created | 

## Example

```python
from encypher.models.fingerprint_match import FingerprintMatch

# TODO update the JSON string below
json = "{}"
# create an instance of FingerprintMatch from a JSON string
fingerprint_match_instance = FingerprintMatch.from_json(json)
# print the JSON string representation of the object
print(FingerprintMatch.to_json())

# convert the object into a dict
fingerprint_match_dict = fingerprint_match_instance.to_dict()
# create an instance of FingerprintMatch from a dict
fingerprint_match_from_dict = FingerprintMatch.from_dict(fingerprint_match_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


