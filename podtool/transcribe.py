import logging
from google.cloud import storage
import os

class Speech2Text:
    """Handles speech-to-text transcription of audio files"""
    
    def __init__(self, credentials_path=None):
        """
        Initialize the transcriber with API credentials
        
        Args:
            credentials_path (str, optional): Path to Google Cloud service account JSON
        """
        self.logger = logging.getLogger(__name__)
        if credentials_path:
            self.storage_client = storage.Client.from_service_account_json(credentials_path)
        else:
            self.storage_client = storage.Client()
        self.bucket_name = "case-audio-transcribe"  # Replace with your actual bucket name
        
    def upload_file(self, filename):
        """
        Upload the given audio file to Google Cloud Storage
        
        Args:
            filename (str): Path to the audio file to upload
            
        Returns: 
            str: The blob name in Google Cloud Storage
            
        Raises:
            Exception: If upload fails
        """
        self.logger.info(f"Uploading {filename} to transcription service")
        
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob_name = os.path.basename(filename)
            blob = bucket.blob(blob_name)
            
            blob.upload_from_filename(filename)
            self.logger.info(f"File {filename} uploaded to {blob_name}")
            
            return blob_name
            
        except Exception as e:
            self.logger.error(f"Failed to upload {filename}: {str(e)}")
            raise
    
    def process(self, filename):
        """
        Transcribe the given audio file to text
        
        Args:
            filename (str): Path to the audio file to transcribe
            
        Returns:
            str: The transcribed text
            
        Raises:
            Exception: If transcription fails
        """
        self.logger.info(f"Starting transcription of {filename}")
        blob_name = self.upload_file(filename)
        print(blob_name)
