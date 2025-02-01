import os
import csv
from dotenv import load_dotenv
from telethon import TelegramClient
from logger import Logger  # Import the logger class

# Load environment variables
load_dotenv()

class TelegramChannelScraper:

    def __init__(self, api_id, api_hash, session_name, media_dir='E:/Git_repo/EthioMedical_Business_DataWarehouse/data/photos', 
                 csv_file='E:/Git_repo/EthioMedical_Business_DataWarehouse/data/telegram_data.csv', channels=None, log_file='E:/Git_repo/EthioMedical_Business_DataWarehouse/data/scraper.log'):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.media_dir = media_dir 
        self.csv_file = csv_file
        self.channels = channels or [] 
        
        # Initialize the logger with a dynamic log file path
        self.logger = Logger(log_file=log_file)

        # Create media directory
        os.makedirs(self.media_dir, exist_ok=True)

    async def scrape_channel(self, client, channel_username, writer):
        
        entity = await client.get_entity(channel_username)
        channel_title = entity.title  # Extract the channel's title
        channel_id = entity.id  # Extract the channel's ID

        self.logger.info(f"Scraping all history from {channel_username}...")  # Log the start of scraping

        try:
            # Scraping all messages from the channel (set limit=None)
            async for message in client.iter_messages(entity, limit=None):
                media_path = await self.download_media(client, message, channel_username)
                
                # Write the data to the CSV file, including channel_id
                writer.writerow([channel_title, channel_username, channel_id, message.id, message.message, message.date, media_path])

            self.logger.info(f"Successfully scraped all history from {channel_username}")  # Log success message
        except Exception as e:
            self.logger.error(f"Error while scraping {channel_username}: {e}")  # Log any error

    async def download_media(self, client, message, channel_username):
        """
        Downloads media from the message if available.

        """
        if message.media and hasattr(message.media, 'photo'):
            filename = f"{channel_username}_{message.id}.jpg"
            media_path = os.path.join(self.media_dir, filename)
            await client.download_media(message.media, media_path)
            return media_path
        return None

    async def run(self):
        """
        Runs the scraping process, initializing the Telegram client and processing each channel.
        """
        self.logger.info("Starting the full history scraping process...")  # Log the start of scraping
        async with TelegramClient(self.session_name, self.api_id, self.api_hash) as client:
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['channel_title', 'channel_username', 'channel_id', 'message_id', 'message', 'date', 'media_path'])

                for channel in self.channels:
                    await self.scrape_channel(client, channel, writer)

if __name__ == "__main__":
    # Get credentials from .env
    api_id = os.getenv('api_id')
    api_hash = os.getenv('api_hash')

    # Validate API credentials
    if not api_id or not api_hash:
        raise ValueError("Your API ID or Hash cannot be empty or None. Please check your .env file.")

    # List of channels to scrape
    channels_to_scrape = [
        '@lobelia4cosmetics',
        # @DoctorsET, 
        # @YetenaWeg, 
        # @EAHCI
    ]

    # Specify the log file path dynamically
    log_file_path = 'E:/Git_repo/EthioMedical_Business_DataWarehouse/data/scraper.log'  # You can change this path as needed

    # Initialize the scraper
    scraper = TelegramChannelScraper(api_id=api_id, api_hash=api_hash, 
                                      session_name='E:/Git_repo/EthioMedical_Business_DataWarehouse/data/scraping_session', 
                                      channels=channels_to_scrape, log_file=log_file_path)

    # Start the scraping process 
    import asyncio
    asyncio.run(scraper.run())
