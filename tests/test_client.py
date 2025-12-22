"""
Tests for RemoraClient

Run with: pytest tests/test_client.py
"""

import os
import pytest
from unittest.mock import patch, Mock
from remora.client import RemoraClient


class TestRemoraClient:
    """Test suite for RemoraClient"""
    
    def test_init_with_api_key(self):
        """Test initialization with explicit API key"""
        client = RemoraClient(api_key="test-key-123")
        assert client.api_key == "test-key-123"
        assert client.url == "https://remora-ai.com/api/v1/risk"
    
    def test_init_with_env_var(self):
        """Test initialization with environment variable"""
        with patch.dict(os.environ, {"REMORA_API_KEY": "env-key-456"}):
            client = RemoraClient()
            assert client.api_key == "env-key-456"
    
    def test_init_missing_api_key(self):
        """Test that missing API key raises ValueError"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Remora API key missing"):
                RemoraClient()
    
    def test_get_context_success(self):
        """Test successful API call"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "safe_to_trade": True,
            "risk_score": 0.25,
            "regime": "bull",
            "reasoning": ["Normal market conditions"]
        }
        mock_response.raise_for_status = Mock()
        
        with patch('remora.client.requests.get', return_value=mock_response):
            client = RemoraClient(api_key="test-key")
            ctx = client.get_context("BTC/USDT")
            
            assert ctx["safe_to_trade"] is True
            assert ctx["risk_score"] == 0.25
            assert ctx["regime"] == "bull"
            assert len(ctx["reasoning"]) == 1
    
    def test_get_context_api_params(self):
        """Test that API is called with correct parameters"""
        mock_response = Mock()
        mock_response.json.return_value = {"safe_to_trade": True, "risk_score": 0.0}
        mock_response.raise_for_status = Mock()
        
        with patch('remora.client.requests.get', return_value=mock_response) as mock_get:
            client = RemoraClient(api_key="test-key")
            client.get_context("ETH/USDT")
            
            # Verify API call parameters
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            
            assert call_args[1]["params"]["pair"] == "ETH/USDT"
            assert call_args[1]["headers"]["Authorization"] == "Bearer test-key"
            assert call_args[1]["timeout"] == 3
    
    def test_get_context_http_error(self):
        """Test handling of HTTP errors"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        
        with patch('remora.client.requests.get', return_value=mock_response):
            client = RemoraClient(api_key="test-key")
            
            with pytest.raises(Exception, match="404 Not Found"):
                client.get_context("BTC/USDT")
    
    def test_get_context_timeout(self):
        """Test handling of timeout errors"""
        import requests
        
        with patch('remora.client.requests.get', side_effect=requests.exceptions.Timeout("Connection timeout")):
            client = RemoraClient(api_key="test-key")
            
            with pytest.raises(requests.exceptions.Timeout):
                client.get_context("BTC/USDT")
    
    def test_get_context_high_risk(self):
        """Test response with high risk score"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "safe_to_trade": False,
            "risk_score": 0.85,
            "regime": "bear",
            "reasoning": ["Volatility spike detected", "Extreme fear conditions"]
        }
        mock_response.raise_for_status = Mock()
        
        with patch('remora.client.requests.get', return_value=mock_response):
            client = RemoraClient(api_key="test-key")
            ctx = client.get_context("BTC/USDT")
            
            assert ctx["safe_to_trade"] is False
            assert ctx["risk_score"] == 0.85
            assert ctx["regime"] == "bear"
            assert len(ctx["reasoning"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])




