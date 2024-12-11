# Instagram RSS Feed Automation

This project automates the process of posting summarized content from an RSS feed to Instagram. It retrieves the latest article from an RSS feed, summarizes it, downloads the associated image, and publishes the content as an Instagram post using the Instagram Graph API.

## added new function to trigger
- New Caption Creation Method: Updated the caption creation method to handle dependencies errors in the old implementation.
- Improved Dependency Handling: Ensures all required libraries and resources are available, with error handling for `NLTK` resources.
- Enhanced Monitoring**: Added a function to continuously monitor RSS feeds for new articles using timestamps.


## Removed Features
- Removed the old caption creation method due to dependency errors.
- Removed the transformer-based summarization model to streamline dependencies.

#to setup and run code first download the code

Run pip install -r requirements.txt
python assignmentscript.py



## 

will do by open ai but dont have open ai key, free open ai key very limited 