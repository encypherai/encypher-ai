# HeatMapData

Schema for heat map visualization data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**positions** | **List[Dict[str, object]]** |  | 
**total_segments** | **int** |  | 
**matched_segments** | **int** |  | 
**match_percentage** | **float** |  | 

## Example

```python
from encypher.models.heat_map_data import HeatMapData

# TODO update the JSON string below
json = "{}"
# create an instance of HeatMapData from a JSON string
heat_map_data_instance = HeatMapData.from_json(json)
# print the JSON string representation of the object
print(HeatMapData.to_json())

# convert the object into a dict
heat_map_data_dict = heat_map_data_instance.to_dict()
# create an instance of HeatMapData from a dict
heat_map_data_from_dict = HeatMapData.from_dict(heat_map_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


