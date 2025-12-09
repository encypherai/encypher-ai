# MemberRevenueDetail

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **string** |  | 
**MemberId** | **string** |  | 
**ContentCount** | **int32** |  | 
**AccessCount** | **int32** |  | 
**RevenueAmount** | **string** |  | 
**Status** | [**PayoutStatus**](PayoutStatus.md) |  | 
**PaidAt** | **NullableTime** |  | 
**PaymentReference** | **NullableString** |  | 

## Methods

### NewMemberRevenueDetail

`func NewMemberRevenueDetail(id string, memberId string, contentCount int32, accessCount int32, revenueAmount string, status PayoutStatus, paidAt NullableTime, paymentReference NullableString, ) *MemberRevenueDetail`

NewMemberRevenueDetail instantiates a new MemberRevenueDetail object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMemberRevenueDetailWithDefaults

`func NewMemberRevenueDetailWithDefaults() *MemberRevenueDetail`

NewMemberRevenueDetailWithDefaults instantiates a new MemberRevenueDetail object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *MemberRevenueDetail) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *MemberRevenueDetail) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *MemberRevenueDetail) SetId(v string)`

SetId sets Id field to given value.


### GetMemberId

`func (o *MemberRevenueDetail) GetMemberId() string`

GetMemberId returns the MemberId field if non-nil, zero value otherwise.

### GetMemberIdOk

`func (o *MemberRevenueDetail) GetMemberIdOk() (*string, bool)`

GetMemberIdOk returns a tuple with the MemberId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMemberId

`func (o *MemberRevenueDetail) SetMemberId(v string)`

SetMemberId sets MemberId field to given value.


### GetContentCount

`func (o *MemberRevenueDetail) GetContentCount() int32`

GetContentCount returns the ContentCount field if non-nil, zero value otherwise.

### GetContentCountOk

`func (o *MemberRevenueDetail) GetContentCountOk() (*int32, bool)`

GetContentCountOk returns a tuple with the ContentCount field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetContentCount

`func (o *MemberRevenueDetail) SetContentCount(v int32)`

SetContentCount sets ContentCount field to given value.


### GetAccessCount

`func (o *MemberRevenueDetail) GetAccessCount() int32`

GetAccessCount returns the AccessCount field if non-nil, zero value otherwise.

### GetAccessCountOk

`func (o *MemberRevenueDetail) GetAccessCountOk() (*int32, bool)`

GetAccessCountOk returns a tuple with the AccessCount field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAccessCount

`func (o *MemberRevenueDetail) SetAccessCount(v int32)`

SetAccessCount sets AccessCount field to given value.


### GetRevenueAmount

`func (o *MemberRevenueDetail) GetRevenueAmount() string`

GetRevenueAmount returns the RevenueAmount field if non-nil, zero value otherwise.

### GetRevenueAmountOk

`func (o *MemberRevenueDetail) GetRevenueAmountOk() (*string, bool)`

GetRevenueAmountOk returns a tuple with the RevenueAmount field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRevenueAmount

`func (o *MemberRevenueDetail) SetRevenueAmount(v string)`

SetRevenueAmount sets RevenueAmount field to given value.


### GetStatus

`func (o *MemberRevenueDetail) GetStatus() PayoutStatus`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *MemberRevenueDetail) GetStatusOk() (*PayoutStatus, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *MemberRevenueDetail) SetStatus(v PayoutStatus)`

SetStatus sets Status field to given value.


### GetPaidAt

`func (o *MemberRevenueDetail) GetPaidAt() time.Time`

GetPaidAt returns the PaidAt field if non-nil, zero value otherwise.

### GetPaidAtOk

`func (o *MemberRevenueDetail) GetPaidAtOk() (*time.Time, bool)`

GetPaidAtOk returns a tuple with the PaidAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPaidAt

`func (o *MemberRevenueDetail) SetPaidAt(v time.Time)`

SetPaidAt sets PaidAt field to given value.


### SetPaidAtNil

`func (o *MemberRevenueDetail) SetPaidAtNil(b bool)`

 SetPaidAtNil sets the value for PaidAt to be an explicit nil

### UnsetPaidAt
`func (o *MemberRevenueDetail) UnsetPaidAt()`

UnsetPaidAt ensures that no value is present for PaidAt, not even an explicit nil
### GetPaymentReference

`func (o *MemberRevenueDetail) GetPaymentReference() string`

GetPaymentReference returns the PaymentReference field if non-nil, zero value otherwise.

### GetPaymentReferenceOk

`func (o *MemberRevenueDetail) GetPaymentReferenceOk() (*string, bool)`

GetPaymentReferenceOk returns a tuple with the PaymentReference field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPaymentReference

`func (o *MemberRevenueDetail) SetPaymentReference(v string)`

SetPaymentReference sets PaymentReference field to given value.


### SetPaymentReferenceNil

`func (o *MemberRevenueDetail) SetPaymentReferenceNil(b bool)`

 SetPaymentReferenceNil sets the value for PaymentReference to be an explicit nil

### UnsetPaymentReference
`func (o *MemberRevenueDetail) UnsetPaymentReference()`

UnsetPaymentReference ensures that no value is present for PaymentReference, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


