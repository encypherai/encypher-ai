# DecodeToolResponse

Response model for decoding.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metadata** | **Dict[str, object]** |  | [optional] 
**verification_status** | **str** |  | [optional] [default to 'Not Attempted']
**error** | **str** |  | [optional] 
**raw_hidden_data** | [**AppRoutersToolsVerifyVerdict**](AppRoutersToolsVerifyVerdict.md) |  | [optional] 

## Example

```python
from encypher.models.decode_tool_response import DecodeToolResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DecodeToolResponse from a JSON string
decode_tool_response_instance = DecodeToolResponse.from_json(json)
# print the JSON string representation of the object
print(DecodeToolResponse.to_json())

# convert the object into a dict
decode_tool_response_dict = decode_tool_response_instance.to_dict()
# create an instance of DecodeToolResponse from a dict
decode_tool_response_from_dict = DecodeToolResponse.from_dict(decode_tool_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


