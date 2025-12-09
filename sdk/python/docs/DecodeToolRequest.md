# DecodeToolRequest

Request model for decoding text.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**encoded_text** | **str** | The text containing embedded metadata. | 

## Example

```python
from encypher.models.decode_tool_request import DecodeToolRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DecodeToolRequest from a JSON string
decode_tool_request_instance = DecodeToolRequest.from_json(json)
# print the JSON string representation of the object
print(DecodeToolRequest.to_json())

# convert the object into a dict
decode_tool_request_dict = decode_tool_request_instance.to_dict()
# create an instance of DecodeToolRequest from a dict
decode_tool_request_from_dict = DecodeToolRequest.from_dict(decode_tool_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


