# CdnAnalyticsTimelineDay


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_date** | **str** |  |
**images_signed** | **int** |  |
**image_requests** | **int** |  |

## Example

```python
from encypher.models.cdn_analytics_timeline_day import CdnAnalyticsTimelineDay

# TODO update the JSON string below
json = "{}"
# create an instance of CdnAnalyticsTimelineDay from a JSON string
cdn_analytics_timeline_day_instance = CdnAnalyticsTimelineDay.from_json(json)
# print the JSON string representation of the object
print(CdnAnalyticsTimelineDay.to_json())

# convert the object into a dict
cdn_analytics_timeline_day_dict = cdn_analytics_timeline_day_instance.to_dict()
# create an instance of CdnAnalyticsTimelineDay from a dict
cdn_analytics_timeline_day_from_dict = CdnAnalyticsTimelineDay.from_dict(cdn_analytics_timeline_day_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
