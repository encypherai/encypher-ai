# FingerprintDetectResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether detection succeeded | 
**fingerprint_detected** | **bool** | Whether a fingerprint was detected | 
**matches** | Option<[**Vec<models::FingerprintMatch>**](FingerprintMatch.md)> | List of fingerprint matches | [optional]
**best_match** | Option<[**models::FingerprintMatch**](FingerprintMatch.md)> |  | [optional]
**processing_time_ms** | **f64** | Processing time in milliseconds | 
**message** | **String** | Status message | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


