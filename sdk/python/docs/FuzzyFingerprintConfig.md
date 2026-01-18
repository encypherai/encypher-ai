# FuzzyFingerprintConfig

Configuration for fuzzy fingerprint indexing at encode time.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** | Whether to generate fuzzy fingerprints during encoding. | [optional] [default to False]
**algorithm** | **str** | Fingerprint algorithm (currently simhash). | [optional] [default to 'simhash']
**levels** | **List[str]** | Segmentation levels to fingerprint. | [optional] 
**include_document_fingerprint** | **bool** | Whether to include a document-level fingerprint. | [optional] [default to False]
**fingerprint_bits** | **int** | Number of bits in the fingerprint. | [optional] [default to 64]
**bucket_bits** | **int** | Number of high-order bits used for bucket indexing. | [optional] [default to 16]

## Example

```python
from encypher.models.fuzzy_fingerprint_config import FuzzyFingerprintConfig

# TODO update the JSON string below
json = "{}"
# create an instance of FuzzyFingerprintConfig from a JSON string
fuzzy_fingerprint_config_instance = FuzzyFingerprintConfig.from_json(json)
# print the JSON string representation of the object
print(FuzzyFingerprintConfig.to_json())

# convert the object into a dict
fuzzy_fingerprint_config_dict = fuzzy_fingerprint_config_instance.to_dict()
# create an instance of FuzzyFingerprintConfig from a dict
fuzzy_fingerprint_config_from_dict = FuzzyFingerprintConfig.from_dict(fuzzy_fingerprint_config_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


