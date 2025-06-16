# Florida Statutes Scraper

This project scrapes all Florida statutes from the official state website, parses them, and loads them into a SQLite database. It is designed for robustness, configurability, resumability, and ease of use in production environments.

## Features
- Scrapes all 49 Florida statute titles
- Parses statutes and subsections
- Loads data into a normalized SQLite database
- Resumable: can restart after interruption and skip completed statutes
- Configurable via `config.ini` (URLs, DB file, rate limiting, user agent)
- Logging for progress and errors
- Rate limiting to avoid overloading the server
- Robust error handling (network, database)
- Unit and integration tests for all major features

## Usage
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Configure `config.ini` as needed (see example in repo).
3. Run the scraper:
   ```sh
   python Statutes_at_5.py
   ```

## Testing
Run all tests with:
```sh
pytest
```

## Configuration
Edit `config.ini` to set:
- `db_file`: SQLite database file path
- `rate_limit_seconds`: Delay between requests
- `user_agent`: Custom User-Agent string
- `index_url`: Statutes index page URL

## License
MIT
