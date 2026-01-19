# FuzzyFingerprintConfig

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | Option<**bool**> | Whether to generate fuzzy fingerprints during encoding. | [optional][default to false]
**algorithm** | Option<**String**> | Fingerprint algorithm (currently simhash). | [optional][default to simhash]
**levels** | Option<**Vec<String>**> | Segmentation levels to fingerprint. | [optional]
**include_document_fingerprint** | Option<**bool**> | Whether to include a document-level fingerprint. | [optional][default to false]
**fingerprint_bits** | Option<**i32**> | Number of bits in the fingerprint. | [optional][default to 64]
**bucket_bits** | Option<**i32**> | Number of high-order bits used for bucket indexing. | [optional][default to 16]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


