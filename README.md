## Prerequisites

- Python 3.8+
- Google Cloud Platform project with Gmail, Drive, and Sheets APIs enabled
- OAuth 2.0 credentials downloaded as `credentials.json`
- Required Python packages (see Installation)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd viable_assignment
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Also install poppler for pdf to image conversion
   https://poppler.freedesktop.org/
   and mention install location into POPPLER_PATH in config file
   
4. Set up Google Cloud Project:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Gmail, Drive, and Sheets APIs
   - Create OAuth 2.0 credentials (Desktop app)
   - Download credentials as `credentials.json` to the project root

5. Configure environment variables:
   Create a `.env` file in the project root with the following variables:
   ```
   DRIVE_FOLDER_ID=your_folder_id
   SPREADSHEET_ID=your_spreadsheet_id
   GROQ_API_KEY=your_groq_api_key
   ```
   you can find your drive folder id and spreadsheet id in the google drive and google sheets url
   
   change target subject and label name in config.py

## Usage

### First-Time Setup

1. Create and activate virtual environment:
   ```
   python -m venv env
   ./env/Scripts/activate
   ```

2. Run the following to generate token.json:
   ```
   python generate_token.py
   ```

3. Authorize the application when prompted in your browser

### Running the Application

Run the following to process emails:
   ```
   python app.py
```

The script will run every 6 hours by default (configurable in `config.py`).

## Configuration

Edit `config.py` to adjust:
- `SUPPORTED_MIME_TYPES`: File types to process
- `SCHEDULE_HOURS`: Hours between scheduled runs