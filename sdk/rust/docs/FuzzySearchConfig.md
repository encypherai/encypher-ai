# FuzzySearchConfig

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | Option<**bool**> | Whether to run fuzzy fingerprint search. | [optional][default to false]
**algorithm** | Option<**String**> | Fingerprint algorithm (currently simhash). | [optional][default to simhash]
**levels** | Option<**Vec<String>**> | Segmentation levels to search. | [optional]
**similarity_threshold** | Option<**f64**> | Similarity threshold for matches (0-1). | [optional][default to 0.82]
**max_candidates** | Option<**i32**> | Maximum number of candidate matches to return. | [optional][default to 20]
**include_merkle_proof** | Option<**bool**> | Whether to include Merkle proofs for matches. | [optional][default to true]
**fallback_when_no_binding** | Option<**bool**> | Only run fuzzy search when no embeddings are found. | [optional][default to true]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


