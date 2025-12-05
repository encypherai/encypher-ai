# RevenueDistributionResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | [**uuid::Uuid**](uuid::Uuid.md) |  | 
**agreement_id** | [**uuid::Uuid**](uuid::Uuid.md) |  | 
**period_start** | [**String**](string.md) |  | 
**period_end** | [**String**](string.md) |  | 
**total_revenue** | **String** |  | 
**encypher_share** | **String** |  | 
**member_pool** | **String** |  | 
**status** | [**models::DistributionStatus**](DistributionStatus.md) |  | 
**created_at** | **String** |  | 
**processed_at** | Option<**String**> |  | 
**member_revenues** | Option<[**Vec<models::MemberRevenueDetail>**](MemberRevenueDetail.md)> |  | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


