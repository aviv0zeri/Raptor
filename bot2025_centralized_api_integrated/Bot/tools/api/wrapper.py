import requests
import hashlib
import hmac
import time
from urllib.parse import urlencode
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BinanceTimeoutError(Exception):
    """Custom exception for Binance timeout errors."""
    pass

@retry(
    stop=stop_after_attempt(10),  # Retry up to 10 times
    wait=wait_exponential(multiplier=2, min=1, max=60),  # Exponential backoff: 1s, 2s, 4s... up to 60s
    retry=retry_if_exception_type((requests.exceptions.RequestException, BinanceTimeoutError)),
)
def make_binance_request(method, url, api_key=None, secret_key=None, **kwargs):
    """
    Centralized function for making Binance API requests with retry logic.
    Args:
        method (str): HTTP method ('GET', 'POST', etc.).
        url (str): Binance API endpoint URL.
        api_key (str): Binance API key for authentication (optional).
        secret_key (str): Binance secret key for signing requests (optional).
        **kwargs: Additional parameters for the requests library.
    Returns:
        response (Response): HTTP response object.
    Raises:
        BinanceTimeoutError: If the request times out.
    """
    try:
        # Log request details
        # logger.info(f"Making {method} request to {url}")
        # logger.info(f"Params: {kwargs.get('params')}")
        # logger.info(f"Headers: {kwargs.get('headers')}")
        # logger.info(f"Timeout: {kwargs.get('timeout', 'default')}")

        # Use a default timeout if not specified
        timeout = kwargs.pop("timeout", (5, 10))  # Connection timeout = 5s, Read timeout = 10s

        # Handle signed requests
        if api_key and secret_key:
            params = kwargs.get("params", {})
            params["timestamp"] = int(time.time() * 1000)  # Add current timestamp
            query_string = urlencode(params)
            signature = hmac.new(secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
            params["signature"] = signature
            kwargs["params"] = params
            headers = kwargs.get("headers", {})
            headers["X-MBX-APIKEY"] = api_key
            kwargs["headers"] = headers

        # Make the request
        response = requests.request(method=method, url=url, timeout=timeout, **kwargs)

        # Raise for HTTP errors (e.g., 404, 500)
        response.raise_for_status()

        # Log successful responses
        # logger.info(f"Request successful: Status code={response.status_code}, Content={response.text[:200]}")
        return response

    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout error during request to {url}: {e}")
        raise BinanceTimeoutError("Binance API request timed out") from e

    except requests.exceptions.RequestException as e:
        logger.error(f"RequestException during request to {url}: {e}")
        if e.response:
            logger.error(f"Response status: {e.response.status_code}, Content: {e.response.text}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error during request to {url}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
