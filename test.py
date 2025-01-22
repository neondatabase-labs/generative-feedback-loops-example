from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient

credential = ClientSecretCredential(
            tenant_id=os.environ["AZURE_AD_TENANT_ID"],
            client_id=os.environ["AZURE_AD_CLIENT_ID"],
            client_secret=os.environ["AZURE_AD_CLIENT_SECRET"],
)

blob_service_url = 

blob_service_client = BlobServiceClient(account_url=blob_service_url, credential=credential)