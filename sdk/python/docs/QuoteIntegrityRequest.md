# QuoteIntegrityRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**quote** | **str** | The exact text the AI cited |
**attribution** | **str** | Claimed source e.g. &#39;According to Reuters...&#39; |
**org_id** | **str** |  | [optional]
**doc_id** | **str** |  | [optional]
**fuzzy_threshold** | **float** | Similarity threshold | [optional] [default to 0.85]

## Example

```python
from encypher.models.quote_integrity_request import QuoteIntegrityRequest

# TODO update the JSON string below
json = "{}"
# create an instance of QuoteIntegrityRequest from a JSON string
quote_integrity_request_instance = QuoteIntegrityRequest.from_json(json)
# print the JSON string representation of the object
print(QuoteIntegrityRequest.to_json())

# convert the object into a dict
quote_integrity_request_dict = quote_integrity_request_instance.to_dict()
# create an instance of QuoteIntegrityRequest from a dict
quote_integrity_request_from_dict = QuoteIntegrityRequest.from_dict(quote_integrity_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
