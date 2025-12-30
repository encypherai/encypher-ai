# PublicKeyInfo

Information about a registered public key.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Key ID | 
**organization_id** | **str** | Organization that owns this key | 
**key_name** | **str** |  | [optional] 
**key_algorithm** | **str** | Key algorithm | 
**key_fingerprint** | **str** | SHA-256 fingerprint of the public key | 
**public_key_pem** | **str** | PEM-encoded public key | 
**is_active** | **bool** | Whether key is active for verification | [optional] [default to True]
**created_at** | **datetime** | When key was registered | 
**last_used_at** | **datetime** |  | [optional] 

## Example

```python
from encypher.models.public_key_info import PublicKeyInfo

# TODO update the JSON string below
json = "{}"
# create an instance of PublicKeyInfo from a JSON string
public_key_info_instance = PublicKeyInfo.from_json(json)
# print the JSON string representation of the object
print(PublicKeyInfo.to_json())

# convert the object into a dict
public_key_info_dict = public_key_info_instance.to_dict()
# create an instance of PublicKeyInfo from a dict
public_key_info_from_dict = PublicKeyInfo.from_dict(public_key_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


