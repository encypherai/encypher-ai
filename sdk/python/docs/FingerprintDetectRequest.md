# FingerprintDetectRequest

Request to detect a fingerprint in text.  Detection uses score-based matching with confidence threshold to identify fingerprinted content even after modifications.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **str** | Text to scan for fingerprint | 
**fingerprint_key** | **str** |  | [optional] 
**confidence_threshold** | **float** | Minimum confidence threshold for detection (0.0-1.0) | [optional] [default to 0.6]
**return_positions** | **bool** | Return positions of detected markers | [optional] [default to False]

## Example

```python
from encypher.models.fingerprint_detect_request import FingerprintDetectRequest

# TODO update the JSON string below
json = "{}"
# create an instance of FingerprintDetectRequest from a JSON string
fingerprint_detect_request_instance = FingerprintDetectRequest.from_json(json)
# print the JSON string representation of the object
print(FingerprintDetectRequest.to_json())

# convert the object into a dict
fingerprint_detect_request_dict = fingerprint_detect_request_instance.to_dict()
# create an instance of FingerprintDetectRequest from a dict
fingerprint_detect_request_from_dict = FingerprintDetectRequest.from_dict(fingerprint_detect_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


