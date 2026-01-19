# FuzzySearchConfig

Configuration for fuzzy fingerprint search during verification.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** | Whether to run fuzzy fingerprint search. | [optional] [default to False]
**algorithm** | **str** | Fingerprint algorithm (currently simhash). | [optional] [default to 'simhash']
**levels** | **List[str]** | Segmentation levels to search. | [optional] 
**similarity_threshold** | **float** | Similarity threshold for matches (0-1). | [optional] [default to 0.82]
**max_candidates** | **int** | Maximum number of candidate matches to return. | [optional] [default to 20]
**include_merkle_proof** | **bool** | Whether to include Merkle proofs for matches. | [optional] [default to True]
**fallback_when_no_binding** | **bool** | Only run fuzzy search when no embeddings are found. | [optional] [default to True]

## Example

```python
from encypher.models.fuzzy_search_config import FuzzySearchConfig

# TODO update the JSON string below
json = "{}"
# create an instance of FuzzySearchConfig from a JSON string
fuzzy_search_config_instance = FuzzySearchConfig.from_json(json)
# print the JSON string representation of the object
print(FuzzySearchConfig.to_json())

# convert the object into a dict
fuzzy_search_config_dict = fuzzy_search_config_instance.to_dict()
# create an instance of FuzzySearchConfig from a dict
fuzzy_search_config_from_dict = FuzzySearchConfig.from_dict(fuzzy_search_config_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


