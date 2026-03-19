# PolicyRule


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_field** | **str** | Field to check: model_provider, confidence_score, reviewer_role, human_reviewed |
**operator** | **str** | Comparison: eq, gte, lte, in, contains |
**value** | **object** |  |
**action** | **str** | Action: warn, block, require_review |

## Example

```python
from encypher.models.policy_rule import PolicyRule

# TODO update the JSON string below
json = "{}"
# create an instance of PolicyRule from a JSON string
policy_rule_instance = PolicyRule.from_json(json)
# print the JSON string representation of the object
print(PolicyRule.to_json())

# convert the object into a dict
policy_rule_dict = policy_rule_instance.to_dict()
# create an instance of PolicyRule from a dict
policy_rule_from_dict = PolicyRule.from_dict(policy_rule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
