# RichArticleSignRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | **str** | Article text/HTML/Markdown |
**content_format** | **str** |  | [optional] [default to 'html']
**document_id** | **str** |  | [optional]
**document_title** | **str** |  | [optional]
**document_url** | **str** |  | [optional]
**metadata** | **Dict[str, object]** |  | [optional]
**images** | [**List[RichContentImage]**](RichContentImage.md) |  |
**options** | [**RichSignOptions**](RichSignOptions.md) |  | [optional]
**publisher_org_id** | **str** |  | [optional]

## Example

```python
from encypher.models.rich_article_sign_request import RichArticleSignRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RichArticleSignRequest from a JSON string
rich_article_sign_request_instance = RichArticleSignRequest.from_json(json)
# print the JSON string representation of the object
print(RichArticleSignRequest.to_json())

# convert the object into a dict
rich_article_sign_request_dict = rich_article_sign_request_instance.to_dict()
# create an instance of RichArticleSignRequest from a dict
rich_article_sign_request_from_dict = RichArticleSignRequest.from_dict(rich_article_sign_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
