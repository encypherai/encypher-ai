# VerificationServiceVerifyVerdict

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Valid** | **bool** |  | 
**Tampered** | **bool** |  | 
**ReasonCode** | **string** |  | 
**SignerId** | Pointer to **NullableString** |  | [optional] 
**SignerName** | Pointer to **NullableString** |  | [optional] 
**Timestamp** | Pointer to **NullableTime** |  | [optional] 
**Details** | Pointer to **map[string]interface{}** |  | [optional] 

## Methods

### NewVerificationServiceVerifyVerdict

`func NewVerificationServiceVerifyVerdict(valid bool, tampered bool, reasonCode string, ) *VerificationServiceVerifyVerdict`

NewVerificationServiceVerifyVerdict instantiates a new VerificationServiceVerifyVerdict object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewVerificationServiceVerifyVerdictWithDefaults

`func NewVerificationServiceVerifyVerdictWithDefaults() *VerificationServiceVerifyVerdict`

NewVerificationServiceVerifyVerdictWithDefaults instantiates a new VerificationServiceVerifyVerdict object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetValid

`func (o *VerificationServiceVerifyVerdict) GetValid() bool`

GetValid returns the Valid field if non-nil, zero value otherwise.

### GetValidOk

`func (o *VerificationServiceVerifyVerdict) GetValidOk() (*bool, bool)`

GetValidOk returns a tuple with the Valid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetValid

`func (o *VerificationServiceVerifyVerdict) SetValid(v bool)`

SetValid sets Valid field to given value.


### GetTampered

`func (o *VerificationServiceVerifyVerdict) GetTampered() bool`

GetTampered returns the Tampered field if non-nil, zero value otherwise.

### GetTamperedOk

`func (o *VerificationServiceVerifyVerdict) GetTamperedOk() (*bool, bool)`

GetTamperedOk returns a tuple with the Tampered field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTampered

`func (o *VerificationServiceVerifyVerdict) SetTampered(v bool)`

SetTampered sets Tampered field to given value.


### GetReasonCode

`func (o *VerificationServiceVerifyVerdict) GetReasonCode() string`

GetReasonCode returns the ReasonCode field if non-nil, zero value otherwise.

### GetReasonCodeOk

`func (o *VerificationServiceVerifyVerdict) GetReasonCodeOk() (*string, bool)`

GetReasonCodeOk returns a tuple with the ReasonCode field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetReasonCode

`func (o *VerificationServiceVerifyVerdict) SetReasonCode(v string)`

SetReasonCode sets ReasonCode field to given value.


### GetSignerId

`func (o *VerificationServiceVerifyVerdict) GetSignerId() string`

GetSignerId returns the SignerId field if non-nil, zero value otherwise.

### GetSignerIdOk

`func (o *VerificationServiceVerifyVerdict) GetSignerIdOk() (*string, bool)`

GetSignerIdOk returns a tuple with the SignerId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignerId

`func (o *VerificationServiceVerifyVerdict) SetSignerId(v string)`

SetSignerId sets SignerId field to given value.

### HasSignerId

`func (o *VerificationServiceVerifyVerdict) HasSignerId() bool`

HasSignerId returns a boolean if a field has been set.

### SetSignerIdNil

`func (o *VerificationServiceVerifyVerdict) SetSignerIdNil(b bool)`

 SetSignerIdNil sets the value for SignerId to be an explicit nil

### UnsetSignerId
`func (o *VerificationServiceVerifyVerdict) UnsetSignerId()`

UnsetSignerId ensures that no value is present for SignerId, not even an explicit nil
### GetSignerName

`func (o *VerificationServiceVerifyVerdict) GetSignerName() string`

GetSignerName returns the SignerName field if non-nil, zero value otherwise.

### GetSignerNameOk

`func (o *VerificationServiceVerifyVerdict) GetSignerNameOk() (*string, bool)`

GetSignerNameOk returns a tuple with the SignerName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignerName

`func (o *VerificationServiceVerifyVerdict) SetSignerName(v string)`

SetSignerName sets SignerName field to given value.

### HasSignerName

`func (o *VerificationServiceVerifyVerdict) HasSignerName() bool`

HasSignerName returns a boolean if a field has been set.

### SetSignerNameNil

`func (o *VerificationServiceVerifyVerdict) SetSignerNameNil(b bool)`

 SetSignerNameNil sets the value for SignerName to be an explicit nil

### UnsetSignerName
`func (o *VerificationServiceVerifyVerdict) UnsetSignerName()`

UnsetSignerName ensures that no value is present for SignerName, not even an explicit nil
### GetTimestamp

`func (o *VerificationServiceVerifyVerdict) GetTimestamp() time.Time`

GetTimestamp returns the Timestamp field if non-nil, zero value otherwise.

### GetTimestampOk

`func (o *VerificationServiceVerifyVerdict) GetTimestampOk() (*time.Time, bool)`

GetTimestampOk returns a tuple with the Timestamp field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTimestamp

`func (o *VerificationServiceVerifyVerdict) SetTimestamp(v time.Time)`

SetTimestamp sets Timestamp field to given value.

### HasTimestamp

`func (o *VerificationServiceVerifyVerdict) HasTimestamp() bool`

HasTimestamp returns a boolean if a field has been set.

### SetTimestampNil

`func (o *VerificationServiceVerifyVerdict) SetTimestampNil(b bool)`

 SetTimestampNil sets the value for Timestamp to be an explicit nil

### UnsetTimestamp
`func (o *VerificationServiceVerifyVerdict) UnsetTimestamp()`

UnsetTimestamp ensures that no value is present for Timestamp, not even an explicit nil
### GetDetails

`func (o *VerificationServiceVerifyVerdict) GetDetails() map[string]interface{}`

GetDetails returns the Details field if non-nil, zero value otherwise.

### GetDetailsOk

`func (o *VerificationServiceVerifyVerdict) GetDetailsOk() (*map[string]interface{}, bool)`

GetDetailsOk returns a tuple with the Details field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDetails

`func (o *VerificationServiceVerifyVerdict) SetDetails(v map[string]interface{})`

SetDetails sets Details field to given value.

### HasDetails

`func (o *VerificationServiceVerifyVerdict) HasDetails() bool`

HasDetails returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


