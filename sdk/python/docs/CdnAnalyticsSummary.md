# CdnAnalyticsSummary


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**organization_id** | **str** |  |
**assets_protected** | **int** |  |
**variants_registered** | **int** |  |
**image_requests_tracked** | **int** |  |
**recoverable_percent** | **float** |  |

## Example

```python
from encypher.models.cdn_analytics_summary import CdnAnalyticsSummary

# TODO update the JSON string below
json = "{}"
# create an instance of CdnAnalyticsSummary from a JSON string
cdn_analytics_summary_instance = CdnAnalyticsSummary.from_json(json)
# print the JSON string representation of the object
print(CdnAnalyticsSummary.to_json())

# convert the object into a dict
cdn_analytics_summary_dict = cdn_analytics_summary_instance.to_dict()
# create an instance of CdnAnalyticsSummary from a dict
cdn_analytics_summary_from_dict = CdnAnalyticsSummary.from_dict(cdn_analytics_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
