"""
🔧 Configuration Loader - Centralized JSON Configuration Management
================================================================

This module loads and manages all JSON configuration files for consistent
data flow throughout the Raptor trading system.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigLoader:
    """Centralized configuration loader for JSON files"""
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.data_dir = os.path.join(self.project_root, 'data')
        self._cache = {}
    
    def load_signal_format(self) -> Dict[str, Any]:
        """Load signal format configuration"""
        return self._load_json('api/signal_format.json')
    
    def load_data_transfer_classes(self) -> Dict[str, Any]:
        """Load data transfer classes configuration"""
        return self._load_json('api/data_transfer_classes.json')
    
    def load_api_routes(self) -> Dict[str, Any]:
        """Load API routes configuration"""
        return self._load_json('api/api_routes.json')
    
    def get_signal_template(self) -> Dict[str, Any]:
        """Get the standard signal template"""
        signal_config = self.load_signal_format()
        return signal_config.get('signal_format', {}).get('example', {})
    
    def validate_signal_format(self, signal_data: Dict[str, Any]) -> bool:
        """Validate if signal data matches the required format"""
        try:
            signal_config = self.load_signal_format()
            required_fields = signal_config.get('signal_format', {}).get('fields', {})
            
            # Check if all required fields are present
            for field_name, field_config in required_fields.items():
                if field_name not in signal_data:
                    print(f"❌ Missing required field: {field_name}")
                    return False
                
                # Validate field type if specified
                expected_type = field_config.get('type')
                if expected_type and not self._validate_field_type(signal_data[field_name], expected_type):
                    print(f"❌ Invalid type for field {field_name}: expected {expected_type}")
                    return False
            
            return True
        except Exception as e:
            print(f"❌ Error validating signal format: {e}")
            return False
    
    def _validate_field_type(self, value: Any, expected_type: str) -> bool:
        """Validate field type"""
        type_map = {
            'string': str,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict
        }
        
        expected_python_type = type_map.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        return True
    
    def _load_json(self, relative_path: str) -> Dict[str, Any]:
        """Load JSON file with caching"""
        cache_key = relative_path
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        file_path = os.path.join(self.data_dir, relative_path)
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                self._cache[cache_key] = data
                return data
        except FileNotFoundError:
            print(f"⚠️ Configuration file not found: {file_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {file_path}: {e}")
            return {}
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            return {}

# Global instance
config_loader = ConfigLoader()

def get_signal_template() -> Dict[str, Any]:
    """Get the standard signal template"""
    return config_loader.get_signal_template()

def validate_signal(signal_data: Dict[str, Any]) -> bool:
    """Validate signal data against the standard format"""
    return config_loader.validate_signal_format(signal_data)

def load_api_routes() -> Dict[str, Any]:
    """Load API routes configuration"""
    return config_loader.load_api_routes()
