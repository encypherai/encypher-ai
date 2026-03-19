# RichContentImage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | **str** | Base64-encoded image bytes |
**filename** | **str** | Original filename e.g. photo1.jpg |
**mime_type** | **str** | MIME type of the image |
**position** | **int** | Order of this image within the article | [optional] [default to 0]
**alt_text** | **str** |  | [optional]
**metadata** | **Dict[str, object]** |  | [optional]

## Example

```python
from encypher.models.rich_content_image import RichContentImage

# TODO update the JSON string below
json = "{}"
# create an instance of RichContentImage from a JSON string
rich_content_image_instance = RichContentImage.from_json(json)
# print the JSON string representation of the object
print(RichContentImage.to_json())

# convert the object into a dict
rich_content_image_dict = rich_content_image_instance.to_dict()
# create an instance of RichContentImage from a dict
rich_content_image_from_dict = RichContentImage.from_dict(rich_content_image_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
