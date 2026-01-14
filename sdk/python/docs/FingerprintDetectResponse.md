# FingerprintDetectResponse

Response after fingerprint detection.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether detection succeeded | 
**fingerprint_detected** | **bool** | Whether a fingerprint was detected | 
**matches** | [**List[FingerprintMatch]**](FingerprintMatch.md) | List of fingerprint matches | [optional] 
**best_match** | [**FingerprintMatch**](FingerprintMatch.md) |  | [optional] 
**processing_time_ms** | **float** | Processing time in milliseconds | 
**message** | **str** | Status message | 

## Example

```python
from encypher.models.fingerprint_detect_response import FingerprintDetectResponse

# TODO update the JSON string below
json = "{}"
# create an instance of FingerprintDetectResponse from a JSON string
fingerprint_detect_response_instance = FingerprintDetectResponse.from_json(json)
# print the JSON string representation of the object
print(FingerprintDetectResponse.to_json())

# convert the object into a dict
fingerprint_detect_response_dict = fingerprint_detect_response_instance.to_dict()
# create an instance of FingerprintDetectResponse from a dict
fingerprint_detect_response_from_dict = FingerprintDetectResponse.from_dict(fingerprint_detect_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


