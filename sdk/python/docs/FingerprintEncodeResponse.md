# FingerprintEncodeResponse

Response after encoding a fingerprint.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether encoding succeeded | 
**document_id** | **str** | Document identifier | 
**fingerprint_id** | **str** | Unique fingerprint identifier | 
**fingerprinted_text** | **str** | Text with embedded fingerprint | 
**fingerprint_key_hash** | **str** | Hash of fingerprint key (for verification) | 
**markers_embedded** | **int** | Number of markers embedded | 
**processing_time_ms** | **float** | Processing time in milliseconds | 
**message** | **str** | Status message | 

## Example

```python
from encypher.models.fingerprint_encode_response import FingerprintEncodeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of FingerprintEncodeResponse from a JSON string
fingerprint_encode_response_instance = FingerprintEncodeResponse.from_json(json)
# print the JSON string representation of the object
print(FingerprintEncodeResponse.to_json())

# convert the object into a dict
fingerprint_encode_response_dict = fingerprint_encode_response_instance.to_dict()
# create an instance of FingerprintEncodeResponse from a dict
fingerprint_encode_response_from_dict = FingerprintEncodeResponse.from_dict(fingerprint_encode_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


