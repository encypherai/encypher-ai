# ContentMetadata

Schema for content metadata returned to AI companies.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**content_type** | **str** |  | 
**word_count** | **int** |  | 
**signed_at** | **datetime** |  | 
**content_hash** | **str** |  | 
**verification_url** | **str** |  | 

## Example

```python
from encypher.models.content_metadata import ContentMetadata

# TODO update the JSON string below
json = "{}"
# create an instance of ContentMetadata from a JSON string
content_metadata_instance = ContentMetadata.from_json(json)
# print the JSON string representation of the object
print(ContentMetadata.to_json())

# convert the object into a dict
content_metadata_dict = content_metadata_instance.to_dict()
# create an instance of ContentMetadata from a dict
content_metadata_from_dict = ContentMetadata.from_dict(content_metadata_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


