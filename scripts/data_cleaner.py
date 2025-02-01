import pandas as pd
import re
import os
import emoji
from logger import Logger

class DataCleaner:
    
    CHANNEL_ID = 'channel_id'
    CHANNEL_TITLE = 'channel_title'
    CHANNEL_USERNAME = 'channel_username'
    MESSAGE = 'message'
    DATE = 'date'
    ID = 'message_id'
    Media_path = 'media_path'
    
    def __init__(self):
        """
        Initializes the DataCleaner with a custom logger instance and allowed character patterns.
        """
        self.logger = Logger(log_file='E:/Git_repo/EthioMedical_Business_DataWarehouse/data/cleaner_log.log')
        self.allowed_characters = re.compile(r'[^a-zA-Z0-9\s.,!?;:()[]@&]+')

    def load_data(self, file_path):
        """
        Loads data from a CSV file into a pandas DataFrame.

        Args:
            file_path (str): The path to the CSV file to be loaded.

        Returns:
            pd.DataFrame: DataFrame containing the loaded data, or an empty DataFrame if loading fails.
        """
        try:
            df = pd.read_csv(file_path)
            self.logger.info(f"Data loaded successfully. Shape: {df.shape}")
            return df
        except FileNotFoundError:
            self.logger.error("File not found. Please check the file path.")
            return pd.DataFrame()  # Return empty DataFrame for consistency
        except Exception as e:
            self.logger.error(f"An error occurred while loading data: {str(e)}")
            return pd.DataFrame()
    
    ### "Handling duplicate values"
    #================================
    def remove_duplicates(self, df, image_directory):
        
        duplicates = df[df.duplicated(subset=self.ID, keep='first')]
        df = df.drop_duplicates(subset=self.ID, keep='first')
        self.logger.info(f"Duplicates removed. New shape: {df.shape}")
        self._remove_duplicate_images(duplicates, image_directory)
        return df

    def _remove_duplicate_images(self, duplicates, image_directory):
        
        for index, row in duplicates.iterrows():
            channel_username = row[self.CHANNEL_USERNAME]
            message_id = row[self.ID]
            image_name = f"{channel_username}_{message_id}.jpg"
            image_path = os.path.join(image_directory, image_name)

            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    self.logger.info(f"Removed duplicate image: {image_path}")
                except Exception as e:
                    self.logger.error(f"Error removing image: {image_path}. Exception: {str(e)}")

    ### "Handling missing values"
    #================================
    def handle_missing_values(self, df):
       
        df.fillna({
            self.CHANNEL_USERNAME: 'Unknown',
            self.MESSAGE: 'N/A',
            self.DATE: '1970-01-01 00:00:00'
        }, inplace=True)
        self.logger.info("Missing values handled.")
        return df

    ### "Standardize data values"
    #================================
    def standardize_formats(self, df):
        
        # Convert Date column to datetime
        if self.DATE in df.columns:
            df[self.DATE] = pd.to_datetime(df[self.DATE], errors='coerce')

        # Clean and format message content
        if self.MESSAGE in df.columns:
            df[self.MESSAGE] = df[self.MESSAGE].apply(self.clean_message_content).str.lower().str.strip()

        # Clean and format channel names
        if self.CHANNEL_USERNAME in df.columns:
            df[self.CHANNEL_USERNAME] = df[self.CHANNEL_USERNAME].str.replace(r'[^a-zA-Z0-9\s]', '', regex=True).str.strip().str.title()

        self.logger.info("Formats standardized.")
        return df

    ### "Cleaning message contents - Handling unwanted characters"
    #================================
    def clean_message_content(self, text):
        
        # Remove emojis
        text = emoji.replace_emoji(text, replace='')  # Remove emojis
        # Remove unwanted characters but keep specific patterns intact
        text = re.sub(self.allowed_characters, '', text)  # Remove unwanted characters
        # Remove extra whitespace (including tabs and newlines)
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
        
        return text.strip()

    def validate_data(self, df):
        
        # Drop rows with invalid Dates
        df = df.dropna(subset=[self.DATE])

        # Validate message content length
        if self.MESSAGE in df.columns:
            df = df[df[self.MESSAGE].str.len() <= 1000]

        # Validate channel names
        df = df[df[self.CHANNEL_USERNAME].str.len() > 0]

        self.logger.info("Data validation completed.")
        return df

    ### "Saving Cleaned Data"
    #================================
    def save_cleaned_data(self, df, file_path):
        
        # Define the mapping of raw column names to SQL-friendly names
        column_mapping = {
            self.CHANNEL_ID: 'channel_id',
            self.CHANNEL_USERNAME: 'channel_username',
            self.CHANNEL_TITLE: 'channel_title',
            self.ID: 'message_id',
            self.MESSAGE: 'Message',
            self.DATE: 'date',
            self.Media_path: 'media_path' 
        }
        
        # Rename columns in the DataFrame
        df.rename(columns=column_mapping, inplace=True)

        # Create the cleaned file path
        cleaned_file_path = file_path.replace('.csv', '_cleaned.csv')
        df.to_csv(cleaned_file_path, index=False)
        self.logger.info(f"Cleaned data saved to {cleaned_file_path}.")

    def clean_telegram_data(self, file_path, image_directory):
        
        try:
            # Load the data
            df = self.load_data(file_path)
            if df.empty:
                self.logger.error("No data loaded, cleaning process aborted.")
                return df
            
            # Run cleaning steps
            df = self.remove_duplicates(df, image_directory)
            df = self.handle_missing_values(df)
            df = self.standardize_formats(df)
            df = self.validate_data(df)
            
            # Save cleaned data
            self.save_cleaned_data(df, file_path)
            
            self.logger.info("Data cleaning completed successfully.")
            return df

        except Exception as e:
            self.logger.error(f"An error occurred during the cleaning process: {str(e)}")
            return pd.DataFrame()

# Run the function
if __name__ == '__main__':
    # Class instance
    cleaner = DataCleaner()
    # Call the main telegram cleaner function
    cleaner.clean_telegram_data('E:/Git_repo/EthioMedical_Business_DataWarehouse/data/telegram_data.csv', 'E:/Git_repo/EthioMedical_Business_DataWarehouse/data/photos/')
