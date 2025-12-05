# EncodeToolResponse

Response model for encoding.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**encoded_text** | **str** | Text with embedded metadata. | 
**metadata** | **Dict[str, object]** |  | [optional] 
**error** | **str** |  | [optional] 

## Example

```python
from encypher.models.encode_tool_response import EncodeToolResponse

# TODO update the JSON string below
json = "{}"
# create an instance of EncodeToolResponse from a JSON string
encode_tool_response_instance = EncodeToolResponse.from_json(json)
# print the JSON string representation of the object
print(EncodeToolResponse.to_json())

# convert the object into a dict
encode_tool_response_dict = encode_tool_response_instance.to_dict()
# create an instance of EncodeToolResponse from a dict
encode_tool_response_from_dict = EncodeToolResponse.from_dict(encode_tool_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


