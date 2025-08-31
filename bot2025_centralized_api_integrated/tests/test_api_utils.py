"""
🧪 API Utils Test Suite - The Cosmic API Testing Framework
=======================================================

📁 File: /bot2025_centralized_api_integrated/tests/test_api_utils.py
🎯 Purpose: Comprehensive testing for API utilities and exchange interactions
🔧 Function: Tests API authentication, requests, and error handling

🌟 Test Coverage:
- API authentication and signature generation
- Request/response handling
- Error handling and retry logic
- Rate limiting compliance
- WebSocket connections
- Exchange-specific functionality

📋 Test Categories:
- Unit tests for individual functions
- Integration tests for API interactions
- Mock tests for external dependencies
- Error scenario testing
- Performance testing

🔗 Related Files:
- Bot/tools/api/api_utils.py (main API utilities)
- Bot/tools/api/wrapper.py (API wrapper)
- config/config_manager.py (configuration)

⚠️  Note: These tests require API permissions to run fully
"""

import pytest
import unittest.mock as mock
from unittest.mock import Mock, patch, MagicMock
import time
import hmac
import hashlib
from urllib.parse import urlencode
import json

# Import the modules to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Bot.tools.api.api_utils import *
from Bot.tools.config.config_manager import ConfigManager

class TestAPIAuthentication:
    """Test API authentication and signature generation"""
    
    def setup_method(self):
        """Set up test environment"""
        self.config = ConfigManager()
        self.api_key = "test_api_key_12345"
        self.secret_key = "test_secret_key_67890"
        
    def test_hmac_signature_generation(self):
        """Test HMAC-SHA256 signature generation"""
        # Test data
        query_string = "symbol=BTCUSDT&side=BUY&type=MARKET&quantity=1.0&timestamp=1234567890"
        expected_signature = hmac.new(
            self.secret_key.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Generate signature using our function
        actual_signature = generate_signature(query_string, self.secret_key)
        
        assert actual_signature == expected_signature
        assert len(actual_signature) == 64  # SHA256 hex length
    
    def test_timestamp_generation(self):
        """Test timestamp generation for API requests"""
        timestamp = generate_timestamp()
        
        assert isinstance(timestamp, int)
        assert timestamp > 0
        assert len(str(timestamp)) == 13  # Millisecond timestamp
    
    def test_request_parameter_building(self):
        """Test building request parameters with authentication"""
        params = {
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'type': 'MARKET',
            'quantity': '1.0'
        }
        
        authenticated_params = build_authenticated_params(
            params, self.api_key, self.secret_key
        )
        
        assert 'timestamp' in authenticated_params
        assert 'signature' in authenticated_params
        assert authenticated_params['apiKey'] == self.api_key
        assert len(authenticated_params['signature']) == 64

class TestAPIRequests:
    """Test API request handling and responses"""
    
    def setup_method(self):
        """Set up test environment"""
        self.base_url = "https://api.binance.com"
        self.endpoint = "/api/v3/account"
        
    @patch('requests.get')
    def test_successful_api_request(self, mock_get):
        """Test successful API request"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'makerCommission': 15,
            'takerCommission': 15,
            'buyerCommission': 0,
            'sellerCommission': 0,
            'canTrade': True,
            'canWithdraw': True,
            'canDeposit': True
        }
        mock_get.return_value = mock_response
        
        # Make request
        response = make_api_request(
            self.base_url + self.endpoint,
            method='GET',
            params={'timestamp': int(time.time() * 1000)}
        )
        
        assert response.status_code == 200
        assert 'makerCommission' in response.json()
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_api_request_with_retry(self, mock_get):
        """Test API request with retry logic"""
        # Mock failed response then success
        mock_response_fail = Mock()
        mock_response_fail.status_code = 429  # Rate limit
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {'success': True}
        
        mock_get.side_effect = [mock_response_fail, mock_response_success]
        
        # Make request with retry
        response = make_api_request(
            self.base_url + self.endpoint,
            method='GET',
            params={'timestamp': int(time.time() * 1000)},
            max_retries=3
        )
        
        assert response.status_code == 200
        assert mock_get.call_count == 2
    
    @patch('requests.get')
    def test_api_request_timeout(self, mock_get):
        """Test API request timeout handling"""
        # Mock timeout
        mock_get.side_effect = Exception("Request timeout")
        
        with pytest.raises(Exception):
            make_api_request(
                self.base_url + self.endpoint,
                method='GET',
                timeout=1
            )

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_api_key(self):
        """Test handling of invalid API key"""
        with pytest.raises(ValueError):
            generate_signature("test", "")
    
    def test_invalid_timestamp(self):
        """Test handling of invalid timestamp"""
        with pytest.raises(ValueError):
            build_authenticated_params({}, "key", "secret", timestamp=-1)
    
    def test_malformed_query_string(self):
        """Test handling of malformed query string"""
        # This should not raise an exception
        signature = generate_signature("", "secret")
        assert isinstance(signature, str)

class TestRateLimiting:
    """Test rate limiting compliance"""
    
    def test_rate_limit_detection(self):
        """Test detection of rate limit responses"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '60'}
        
        is_rate_limited = check_rate_limit(mock_response)
        assert is_rate_limited == True
    
    def test_rate_limit_wait_time(self):
        """Test calculation of rate limit wait time"""
        mock_response = Mock()
        mock_response.headers = {'Retry-After': '30'}
        
        wait_time = get_rate_limit_wait_time(mock_response)
        assert wait_time == 30
    
    def test_rate_limit_headers(self):
        """Test rate limit header parsing"""
        mock_response = Mock()
        mock_response.headers = {
            'X-MBX-USED-WEIGHT-1M': '100',
            'X-MBX-ORDER-COUNT-1M': '5'
        }
        
        limits = parse_rate_limit_headers(mock_response)
        assert limits['used_weight_1m'] == 100
        assert limits['order_count_1m'] == 5

class TestWebSocketConnections:
    """Test WebSocket connection handling"""
    
    @patch('websockets.connect')
    def test_websocket_connection(self, mock_connect):
        """Test WebSocket connection establishment"""
        mock_websocket = Mock()
        mock_connect.return_value.__aenter__.return_value = mock_websocket
        
        # Test connection
        websocket = create_websocket_connection("wss://stream.binance.com:9443/ws/btcusdt@trade")
        
        assert websocket is not None
        mock_connect.assert_called_once()
    
    def test_websocket_url_validation(self):
        """Test WebSocket URL validation"""
        valid_url = "wss://stream.binance.com:9443/ws/btcusdt@trade"
        invalid_url = "http://invalid-url"
        
        assert is_valid_websocket_url(valid_url) == True
        assert is_valid_websocket_url(invalid_url) == False

class TestExchangeSpecific:
    """Test exchange-specific functionality"""
    
    def test_binance_order_validation(self):
        """Test Binance order parameter validation"""
        valid_order = {
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'type': 'MARKET',
            'quantity': '1.0'
        }
        
        invalid_order = {
            'symbol': 'BTCUSDT',
            'side': 'INVALID',
            'type': 'MARKET',
            'quantity': '1.0'
        }
        
        assert validate_binance_order(valid_order) == True
        assert validate_binance_order(invalid_order) == False
    
    def test_bybit_order_validation(self):
        """Test Bybit order parameter validation"""
        valid_order = {
            'symbol': 'BTCUSDT',
            'side': 'Buy',
            'orderType': 'Market',
            'qty': '1.0'
        }
        
        invalid_order = {
            'symbol': 'BTCUSDT',
            'side': 'Invalid',
            'orderType': 'Market',
            'qty': '1.0'
        }
        
        assert validate_bybit_order(valid_order) == True
        assert validate_bybit_order(invalid_order) == False

class TestPerformance:
    """Test performance and optimization"""
    
    def test_request_caching(self):
        """Test API request caching"""
        cache_key = "test_cache_key"
        cache_data = {"test": "data"}
        
        # Set cache
        set_cache(cache_key, cache_data, ttl=60)
        
        # Get cache
        cached_data = get_cache(cache_key)
        assert cached_data == cache_data
    
    def test_batch_requests(self):
        """Test batch request processing"""
        requests = [
            {'url': '/api/v3/ticker/price', 'params': {'symbol': 'BTCUSDT'}},
            {'url': '/api/v3/ticker/price', 'params': {'symbol': 'ETHUSDT'}},
            {'url': '/api/v3/ticker/price', 'params': {'symbol': 'ADAUSDT'}}
        ]
        
        # Process batch requests
        batch_results = process_batch_requests(requests)
        
        assert len(batch_results) == 3
        assert all(isinstance(result, dict) for result in batch_results)

# Fixtures for common test data
@pytest.fixture
def sample_api_response():
    """Sample API response for testing"""
    return {
        'symbol': 'BTCUSDT',
        'price': '45000.00',
        'timestamp': int(time.time() * 1000)
    }

@pytest.fixture
def sample_order_data():
    """Sample order data for testing"""
    return {
        'symbol': 'BTCUSDT',
        'side': 'BUY',
        'type': 'MARKET',
        'quantity': '1.0',
        'timestamp': int(time.time() * 1000)
    }

@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    config = Mock()
    config.get_api_key.return_value = "test_api_key"
    config.get_secret_key.return_value = "test_secret_key"
    config.get_base_url.return_value = "https://api.binance.com"
    return config

# Integration tests (require API permissions)
@pytest.mark.integration
class TestIntegration:
    """Integration tests that require actual API access"""
    
    @pytest.mark.skip(reason="Requires API permissions")
    def test_live_api_connection(self):
        """Test live API connection (requires API key)"""
        # This test would require actual API credentials
        pass
    
    @pytest.mark.skip(reason="Requires API permissions")
    def test_live_order_placement(self):
        """Test live order placement (requires API key)"""
        # This test would require actual API credentials
        pass
    
    @pytest.mark.skip(reason="Requires API permissions")
    def test_live_websocket_stream(self):
        """Test live WebSocket stream (requires API key)"""
        # This test would require actual API credentials
        pass

if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "--verbose",
        "--cov=Bot.ver_1.tools.api",
        "--cov-report=html:tests/coverage/api_utils",
        "--cov-report=term-missing"
    ])
