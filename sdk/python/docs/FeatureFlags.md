# FeatureFlags

Organization feature flags.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**merkle_enabled** | **bool** | Merkle tree features enabled | [optional] [default to False]
**byok_enabled** | **bool** | Bring Your Own Key enabled | [optional] [default to False]
**sentence_tracking** | **bool** | Sentence-level tracking enabled | [optional] [default to False]
**bulk_operations** | **bool** | Bulk/batch operations enabled | [optional] [default to False]
**custom_assertions** | **bool** | Custom C2PA assertions enabled | [optional] [default to False]
**streaming** | **bool** | Streaming API enabled | [optional] [default to True]
**team_management** | **bool** | Team management enabled | [optional] [default to False]
**audit_logs** | **bool** | Audit logs enabled | [optional] [default to False]
**sso** | **bool** | SSO/SAML enabled | [optional] [default to False]
**max_team_members** | **int** | Maximum team members allowed | [optional] [default to 1]

## Example

```python
from encypher.models.feature_flags import FeatureFlags

# TODO update the JSON string below
json = "{}"
# create an instance of FeatureFlags from a JSON string
feature_flags_instance = FeatureFlags.from_json(json)
# print the JSON string representation of the object
print(FeatureFlags.to_json())

# convert the object into a dict
feature_flags_dict = feature_flags_instance.to_dict()
# create an instance of FeatureFlags from a dict
feature_flags_from_dict = FeatureFlags.from_dict(feature_flags_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


