# FingerprintEncodeRequest

Request to encode a robust fingerprint into text.  Fingerprints use secret-seeded placement of invisible markers that survive text modifications like paraphrasing or truncation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **str** | Unique document identifier | 
**text** | **str** | Text to fingerprint | 
**fingerprint_density** | **float** | Density of fingerprint markers (0.01-0.5) | [optional] [default to 0.1]
**fingerprint_key** | **str** |  | [optional] 
**metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from encypher.models.fingerprint_encode_request import FingerprintEncodeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of FingerprintEncodeRequest from a JSON string
fingerprint_encode_request_instance = FingerprintEncodeRequest.from_json(json)
# print the JSON string representation of the object
print(FingerprintEncodeRequest.to_json())

# convert the object into a dict
fingerprint_encode_request_dict = fingerprint_encode_request_instance.to_dict()
# create an instance of FingerprintEncodeRequest from a dict
fingerprint_encode_request_from_dict = FingerprintEncodeRequest.from_dict(fingerprint_encode_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


