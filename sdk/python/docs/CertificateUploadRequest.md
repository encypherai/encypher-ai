# CertificateUploadRequest

Request to upload a CA-signed certificate for BYOK.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**certificate_pem** | **str** | PEM-encoded X.509 certificate (must chain to C2PA trusted CA) | 
**chain_pem** | **str** |  | [optional] 
**key_name** | **str** |  | [optional] 

## Example

```python
from encypher.models.certificate_upload_request import CertificateUploadRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CertificateUploadRequest from a JSON string
certificate_upload_request_instance = CertificateUploadRequest.from_json(json)
# print the JSON string representation of the object
print(CertificateUploadRequest.to_json())

# convert the object into a dict
certificate_upload_request_dict = certificate_upload_request_instance.to_dict()
# create an instance of CertificateUploadRequest from a dict
certificate_upload_request_from_dict = CertificateUploadRequest.from_dict(certificate_upload_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


