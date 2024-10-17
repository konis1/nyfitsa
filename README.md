# Nyfitsa

`Nyfitsa` is a Python-based command-line tool designed to fetch header data from a list of URLs and calculate statistics based on specific HTTP headers such as server information, XSS protection, X-Frame options, content type options, and referrer policy. The tool supports fetching URLs both from a list provided via the command line and from a text file.

## Features

- **Fetch HTTP Header Information**: Fetches header information from a list of URLs.
- **Server Statistics**: Optionally calculate server statistics based on the `Server` header.
- **XSS Protection Statistics**: Optionally calculate statistics based on the `X-XSS-Protection` header.
- **X-Frame Options Statistics**: Optionally calculate statistics based on the `X-Frame-Options` header.
- **Content-Type Options Statistics**: Optionally calculate statistics based on the `X-Content-Type-Options` header.
- **Referrer Policy Statistics**: Optionally calculate statistics based on the `Referrer-Policy` header.
- **Parallelized URL Fetching**: The tool fetches data from URLs in parallel to speed up the process.
- **Support for Input from Text Files**: Provide URLs directly or via a text file (one URL per line).

## Installation

To install the package with the required dependencies, use the following commands:

```bash
pip install nyfitsa
```

## Usage

### Command-line Interface (CLI)

The tool accepts multiple options through the command line. These options are defined in the `NyfitsaConfig` class.

### Basic Usage

```bash
python -m nyfitsa --urls http://example.com http://google.com
```

### Options

- `--urls`: Provide a list of URLs to fetch header data from.
- `--stats-server`: Enable server statistics calculation from the list of URLs.
- `--stats-xss-protection`: Enable XSS protection statistics calculation.
- `--stats-x-frame-options`: Enable X-Frame options statistics calculation.
- `--stats-x-content-type-options`: Enable content-type options statistics calculation.
- `--stats-referrer-policy`: Enable referrer policy statistics calculation.
- `--file`: Provide a text file containing URLs (one per line).

### Example: Fetching URLs from a File and Printing Server Statistics

```bash
python -m nyfitsa --file urls.txt --stats-server
```

### Example: Fetching URLs and Printing Multiple Stats

```bash
python -m nyfitsa --urls http://example.com http://test.com --stats-server --stats-xss-protection
```

## Configuration Options

The following configuration options are defined in the `NyfitsaConfig` class:

- `urls`: A list of URLs to fetch the headers data. Each URL must follow the format `http://www.example.com` or `https://www.example.com`.
- `stats_server`: A boolean flag to activate server statistics calculation.
- `stats_xss_protection`: A boolean flag to activate XSS protection statistics calculation.
- `stats_x_frame_options`: A boolean flag to activate X-Frame options statistics calculation.
- `stats_x_content_type_options`: A boolean flag to activate content-type options statistics calculation.
- `stats_referrer_policy`: A boolean flag to activate referrer policy statistics calculation.
- `file`: Path to a text file containing a list of URLs (one per line).

## How It Works

1. **Configuration Parsing**: The `NyfitsaConfig` class defines all the possible input options that can be passed via the command line.
2. **URL Fetching**: The list of URLs is fetched either from the command line directly or from a text file if provided.
3. **Parallel Fetching**: The function `parralelize_fetching` is used to fetch the headers of the URLs in parallel for better performance.
4. **Statistics Calculation**: Based on the selected options, statistics for different headers are calculated and printed.