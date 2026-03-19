# CdnAnalyticsTimeline


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**days** | **int** |  |
**data** | [**List[CdnAnalyticsTimelineDay]**](CdnAnalyticsTimelineDay.md) |  |

## Example

```python
from encypher.models.cdn_analytics_timeline import CdnAnalyticsTimeline

# TODO update the JSON string below
json = "{}"
# create an instance of CdnAnalyticsTimeline from a JSON string
cdn_analytics_timeline_instance = CdnAnalyticsTimeline.from_json(json)
# print the JSON string representation of the object
print(CdnAnalyticsTimeline.to_json())

# convert the object into a dict
cdn_analytics_timeline_dict = cdn_analytics_timeline_instance.to_dict()
# create an instance of CdnAnalyticsTimeline from a dict
cdn_analytics_timeline_from_dict = CdnAnalyticsTimeline.from_dict(cdn_analytics_timeline_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
