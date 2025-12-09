# EncodeToolRequest

Request model for encoding text with metadata.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**original_text** | **str** | The original text to embed metadata into. | 
**target** | **str** |  | [optional] 
**metadata_format** | **str** |  | [optional] 
**ai_info** | **Dict[str, object]** |  | [optional] 
**custom_metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from encypher.models.encode_tool_request import EncodeToolRequest

# TODO update the JSON string below
json = "{}"
# create an instance of EncodeToolRequest from a JSON string
encode_tool_request_instance = EncodeToolRequest.from_json(json)
# print the JSON string representation of the object
print(EncodeToolRequest.to_json())

# convert the object into a dict
encode_tool_request_dict = encode_tool_request_instance.to_dict()
# create an instance of EncodeToolRequest from a dict
encode_tool_request_from_dict = EncodeToolRequest.from_dict(encode_tool_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


