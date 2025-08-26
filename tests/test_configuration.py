"""Tests for configuration and CLI argument parsing."""

import pytest
import argparse
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Import functions to test
sys.path.insert(0, str(Path(__file__).parent.parent))
from main import (
    Config,
    parse_arguments,
    create_config_from_args,
    show_examples,
    show_cache_help
)


class TestConfig:
    """Test configuration class and defaults."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.output_dir == "."
        assert config.max_workers == 10
        assert config.regions_filename == "regions_services.csv"
        assert config.matrix_filename == "services_regions_matrix.csv"
        assert config.log_level == "INFO"
        assert config.aws_profile is None
        assert config.aws_region == "us-east-1"
        assert config.max_retries == 3
        assert config.cache_enabled is True
        assert config.cache_hours == 24
        assert config.cache_file == "aws_data_cache.json"
        assert config.use_rich is True
        assert config.output_formats is None
    
    def test_custom_config(self):
        """Test configuration with custom values."""
        config = Config(
            output_dir="./custom",
            max_workers=15,
            log_level="DEBUG",
            aws_profile="prod",
            cache_enabled=False,
            cache_hours=48,
            output_formats=["json", "excel"]
        )
        
        assert config.output_dir == "./custom"
        assert config.max_workers == 15
        assert config.log_level == "DEBUG"
        assert config.aws_profile == "prod"
        assert config.cache_enabled is False
        assert config.cache_hours == 48
        assert config.output_formats == ["json", "excel"]


class TestArgumentParsing:
    """Test command-line argument parsing."""
    
    def test_default_arguments(self):
        """Test parsing with default arguments."""
        with patch('sys.argv', ['main.py']):
            args = parse_arguments()
            
            assert args.output_dir == "."
            assert args.max_workers == 10
            assert args.regions_file == "regions_services.csv"
            assert args.matrix_file == "services_regions_matrix.csv"
            assert args.max_retries == 3
            assert args.no_cache is False
            assert args.cache_hours == 24
            assert args.cache_file == "aws_data_cache.json"
            assert args.format == ["csv"]
            assert args.profile is None
            assert args.region == "us-east-1"
            assert args.log_level == "INFO"
            assert args.quiet is False
    
    def test_custom_arguments(self):
        """Test parsing with custom arguments."""
        test_args = [
            'main.py',
            '--output-dir', './reports',
            '--max-workers', '15',
            '--max-retries', '5',
            '--no-cache',
            '--cache-hours', '48',
            '--format', 'json', 'excel',
            '--profile', 'production',
            '--region', 'us-west-2',
            '--log-level', 'DEBUG',
            '--quiet'
        ]
        
        with patch('sys.argv', test_args):
            args = parse_arguments()
            
            assert args.output_dir == "./reports"
            assert args.max_workers == 15
            assert args.max_retries == 5
            assert args.no_cache is True
            assert args.cache_hours == 48
            assert args.format == ["json", "excel"]
            assert args.profile == "production"
            assert args.region == "us-west-2"
            assert args.log_level == "DEBUG"
            assert args.quiet is True
    
    def test_help_arguments(self):
        """Test help and information arguments."""
        # Test version argument
        with patch('sys.argv', ['main.py', '--version']):
            with pytest.raises(SystemExit):
                parse_arguments()
        
        # Test examples argument
        with patch('sys.argv', ['main.py', '--examples']):
            args = parse_arguments()
            assert hasattr(args, 'examples')
            assert args.examples is True
        
        # Test cache help argument
        with patch('sys.argv', ['main.py', '--cache-help']):
            args = parse_arguments()
            assert hasattr(args, 'cache_help')
            assert args.cache_help is True
    
    def test_cache_arguments(self):
        """Test cache-related arguments."""
        # Test cache stats
        with patch('sys.argv', ['main.py', '--cache-stats']):
            args = parse_arguments()
            assert args.cache_stats is True
        
        # Test clear cache
        with patch('sys.argv', ['main.py', '--clear-cache']):
            args = parse_arguments()
            assert args.clear_cache is True
        
        # Test custom cache file
        with patch('sys.argv', ['main.py', '--cache-file', './custom_cache.json']):
            args = parse_arguments()
            assert args.cache_file == "./custom_cache.json"
    
    def test_format_validation(self):
        """Test output format validation."""
        # Valid formats
        with patch('sys.argv', ['main.py', '--format', 'csv', 'json', 'excel']):
            args = parse_arguments()
            assert args.format == ['csv', 'json', 'excel']
        
        # Invalid format should cause argument parser error
        with patch('sys.argv', ['main.py', '--format', 'invalid']):
            with pytest.raises(SystemExit):
                parse_arguments()
    
    def test_numeric_argument_validation(self):
        """Test numeric argument validation."""
        # Valid numeric arguments
        with patch('sys.argv', ['main.py', '--max-workers', '20', '--cache-hours', '72']):
            args = parse_arguments()
            assert args.max_workers == 20
            assert args.cache_hours == 72
        
        # Invalid numeric arguments should cause error
        with patch('sys.argv', ['main.py', '--max-workers', 'invalid']):
            with pytest.raises(SystemExit):
                parse_arguments()


class TestConfigCreation:
    """Test configuration creation from arguments."""
    
    def test_create_config_from_args(self):
        """Test configuration creation from parsed arguments."""
        # Mock arguments object
        mock_args = MagicMock()
        mock_args.output_dir = "./test"
        mock_args.max_workers = 15
        mock_args.regions_file = "custom_regions.csv"
        mock_args.matrix_file = "custom_matrix.csv"
        mock_args.log_level = "DEBUG"
        mock_args.profile = "prod"
        mock_args.region = "us-west-2"
        mock_args.max_retries = 5
        mock_args.no_cache = True
        mock_args.cache_hours = 48
        mock_args.cache_file = "custom_cache.json"
        mock_args.format = ["json", "excel"]
        
        config = create_config_from_args(mock_args)
        
        assert config.output_dir == "./test"
        assert config.max_workers == 15
        assert config.regions_filename == "custom_regions.csv"
        assert config.matrix_filename == "custom_matrix.csv"
        assert config.log_level == "DEBUG"
        assert config.aws_profile == "prod"
        assert config.aws_region == "us-west-2"
        assert config.max_retries == 5
        assert config.cache_enabled is False  # no_cache=True means cache_enabled=False
        assert config.cache_hours == 48
        assert config.cache_file == "custom_cache.json"
        assert config.output_formats == ["json", "excel"]
    
    def test_cache_enabled_logic(self):
        """Test cache enabled logic with no-cache flag."""
        # Cache enabled (default)
        mock_args = MagicMock()
        mock_args.no_cache = False
        mock_args.cache_hours = 24
        mock_args.cache_file = "cache.json"
        mock_args.format = ["csv"]
        
        # Set other required attributes with defaults
        for attr in ['output_dir', 'max_workers', 'regions_file', 'matrix_file', 
                     'log_level', 'profile', 'region', 'max_retries']:
            setattr(mock_args, attr, None)
        
        mock_args.output_dir = "."
        mock_args.max_workers = 10
        mock_args.regions_file = "regions.csv"
        mock_args.matrix_file = "matrix.csv"
        mock_args.log_level = "INFO"
        mock_args.region = "us-east-1"
        mock_args.max_retries = 3
        
        config = create_config_from_args(mock_args)
        assert config.cache_enabled is True
        
        # Cache disabled
        mock_args.no_cache = True
        config = create_config_from_args(mock_args)
        assert config.cache_enabled is False


class TestHelpFunctions:
    """Test help and information display functions."""
    
    def test_show_examples(self, capsys):
        """Test examples display function."""
        show_examples()
        captured = capsys.readouterr()
        
        assert "AWS Services Reporter - Usage Examples" in captured.out
        assert "BASIC USAGE:" in captured.out
        assert "CACHING EXAMPLES:" in captured.out
        assert "OUTPUT FORMAT EXAMPLES:" in captured.out
        assert "python main.py" in captured.out
    
    def test_show_cache_help(self, capsys):
        """Test cache help display function."""
        show_cache_help()
        captured = capsys.readouterr()
        
        assert "AWS Services Reporter - Caching System" in captured.out
        assert "HOW IT WORKS:" in captured.out
        assert "CACHE FILE:" in captured.out
        assert "TIME-TO-LIVE (TTL):" in captured.out
        assert "99% time savings" in captured.out
    
    def test_help_content_completeness(self, capsys):
        """Test that help functions contain all important information."""
        show_examples()
        examples_output = capsys.readouterr().out
        
        # Should contain all major CLI options
        assert "--cache-stats" in examples_output
        assert "--format" in examples_output
        assert "--max-workers" in examples_output
        assert "--profile" in examples_output
        
        show_cache_help()
        cache_help_output = capsys.readouterr().out
        
        # Should contain all cache concepts
        assert "TTL" in cache_help_output
        assert "aws_data_cache.json" in cache_help_output
        assert "--clear-cache" in cache_help_output
        assert "--no-cache" in cache_help_output


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_conflicting_arguments(self):
        """Test handling of potentially conflicting arguments."""
        # No-cache with cache-hours should work (cache-hours ignored)
        with patch('sys.argv', ['main.py', '--no-cache', '--cache-hours', '48']):
            args = parse_arguments()
            config = create_config_from_args(args)
            assert config.cache_enabled is False
            assert config.cache_hours == 48  # Still set but ignored
    
    def test_boundary_values(self):
        """Test boundary values for numeric arguments."""
        # Minimum values
        with patch('sys.argv', ['main.py', '--max-workers', '1', '--cache-hours', '1']):
            args = parse_arguments()
            assert args.max_workers == 1
            assert args.cache_hours == 1
        
        # Large values
        with patch('sys.argv', ['main.py', '--max-workers', '100', '--cache-hours', '8760']):
            args = parse_arguments()
            assert args.max_workers == 100
            assert args.cache_hours == 8760  # 1 year


if __name__ == "__main__":
    pytest.main([__file__])