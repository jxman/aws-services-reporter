"""Tests for RSS client functionality."""

import unittest
import xml.etree.ElementTree as ET
from unittest.mock import mock_open, patch

from aws_services_reporter.aws_client.rss_client import (
    extract_region_code_from_description,
    get_rss_region_launch_dates,
    merge_launch_date_sources,
    parse_rss_launch_dates,
)
from aws_services_reporter.core.config import Config


class TestRSSClient(unittest.TestCase):
    """Test cases for RSS client functionality."""

    def test_extract_region_code_from_description(self):
        """Test region code extraction from RSS descriptions."""
        # Test standard region format
        self.assertEqual(
            extract_region_code_from_description(
                "AWS region us-east-1 is now available"
            ),
            "us-east-1",
        )

        # Test extended region format
        self.assertEqual(
            extract_region_code_from_description("New region ap-southeast-2 launched"),
            "ap-southeast-2",
        )

        # Test case insensitive matching
        self.assertEqual(
            extract_region_code_from_description("Region EU-WEST-1 announcement"),
            "eu-west-1",
        )

        # Test no match
        self.assertIsNone(
            extract_region_code_from_description("General AWS announcement")
        )

        # Test multiple matches (should return first)
        self.assertEqual(
            extract_region_code_from_description(
                "Migration from us-east-1 to us-west-2"
            ),
            "us-east-1",
        )

    def test_parse_rss_launch_dates(self):
        """Test RSS XML parsing for launch dates."""
        sample_rss = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <title>AWS Regions</title>
                <item>
                    <title>US East (N. Virginia)</title>
                    <description>AWS region us-east-1 launch announcement</description>
                    <link>https://aws.amazon.com/blogs/aws/us-east-1</link>
                    <pubDate>Fri, 25 Aug 2006 12:00:00 GMT</pubDate>
                </item>
                <item>
                    <title>EU West (Ireland)</title>
                    <description>AWS region eu-west-1 is now available</description>
                    <link>https://aws.amazon.com/blogs/aws/eu-west-1</link>
                    <pubDate>Mon, 10 Dec 2007 15:30:00 GMT</pubDate>
                </item>
                <item>
                    <title>General Update</title>
                    <description>No region code here</description>
                    <link>https://aws.amazon.com/blogs/aws/general</link>
                    <pubDate>Wed, 01 Jan 2020 00:00:00 GMT</pubDate>
                </item>
            </channel>
        </rss>"""

        result = parse_rss_launch_dates(sample_rss)

        # Should extract 2 regions (third has no region code)
        self.assertEqual(len(result), 2)

        # Check us-east-1 data
        self.assertIn("us-east-1", result)
        us_east = result["us-east-1"]
        self.assertEqual(us_east["launch_date"], "2006-08-25")
        self.assertEqual(us_east["formatted_date"], "Fri, 25 Aug 2006 12:00:00 GMT")
        self.assertEqual(us_east["announcement_title"], "US East (N. Virginia)")
        self.assertEqual(
            us_east["announcement_url"], "https://aws.amazon.com/blogs/aws/us-east-1"
        )

        # Check eu-west-1 data
        self.assertIn("eu-west-1", result)
        eu_west = result["eu-west-1"]
        self.assertEqual(eu_west["launch_date"], "2007-12-10")
        self.assertEqual(eu_west["formatted_date"], "Mon, 10 Dec 2007 15:30:00 GMT")

    def test_parse_rss_launch_dates_invalid_xml(self):
        """Test RSS parsing with invalid XML."""
        invalid_xml = "This is not XML at all"

        with self.assertRaises(ET.ParseError):
            parse_rss_launch_dates(invalid_xml)

    def test_parse_rss_launch_dates_invalid_date(self):
        """Test RSS parsing with unparseable dates."""
        sample_rss = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <item>
                    <title>US East (N. Virginia)</title>
                    <description>AWS region us-east-1 launch</description>
                    <link>https://aws.amazon.com/blogs/aws/us-east-1</link>
                    <pubDate>Invalid Date Format</pubDate>
                </item>
            </channel>
        </rss>"""

        result = parse_rss_launch_dates(sample_rss)

        self.assertEqual(len(result), 1)
        self.assertIn("us-east-1", result)
        self.assertEqual(result["us-east-1"]["launch_date"], "Unknown")

    def test_merge_launch_date_sources_rss_priority(self):
        """Test that RSS data takes priority when merging sources."""
        ssm_date = "2006-08-20"
        rss_data = {
            "launch_date": "2006-08-25",
            "formatted_date": "Fri, 25 Aug 2006 12:00:00 GMT",
            "announcement_url": "https://example.com",
        }

        result = merge_launch_date_sources(ssm_date, rss_data)

        self.assertEqual(result["launch_date"], "2006-08-25")
        self.assertEqual(result["source"], "RSS")
        self.assertEqual(result["formatted_date"], "Fri, 25 Aug 2006 12:00:00 GMT")
        self.assertEqual(result["announcement_url"], "https://example.com")

    def test_merge_launch_date_sources_ssm_fallback(self):
        """Test SSM fallback when RSS data unavailable."""
        ssm_date = "2006-08-20"
        rss_data = None

        result = merge_launch_date_sources(ssm_date, rss_data)

        self.assertEqual(result["launch_date"], "2006-08-20")
        self.assertEqual(result["source"], "SSM")
        self.assertEqual(result["formatted_date"], "")
        self.assertEqual(result["announcement_url"], "")

    def test_merge_launch_date_sources_unknown_fallback(self):
        """Test fallback when both sources are unavailable."""
        ssm_date = "Unknown"
        rss_data = {"launch_date": "Unknown"}

        result = merge_launch_date_sources(ssm_date, rss_data)

        self.assertEqual(result["launch_date"], "Unknown")
        self.assertEqual(result["source"], "Unknown")

    def test_merge_launch_date_sources_rss_unknown(self):
        """Test SSM fallback when RSS has unknown date."""
        ssm_date = "2006-08-20"
        rss_data = {"launch_date": "Unknown", "formatted_date": ""}

        result = merge_launch_date_sources(ssm_date, rss_data)

        self.assertEqual(result["launch_date"], "2006-08-20")
        self.assertEqual(result["source"], "SSM")

    @patch("aws_services_reporter.aws_client.rss_client.fetch_rss_data")
    @patch("aws_services_reporter.aws_client.rss_client.parse_rss_launch_dates")
    def test_get_rss_region_launch_dates_success(self, mock_parse, mock_fetch):
        """Test successful RSS data retrieval."""
        mock_fetch.return_value = "<rss>mock data</rss>"
        mock_parse.return_value = {"us-east-1": {"launch_date": "2006-08-25"}}

        config = Config()
        result = get_rss_region_launch_dates(config)

        mock_fetch.assert_called_once()
        mock_parse.assert_called_once_with("<rss>mock data</rss>")
        self.assertEqual(result, {"us-east-1": {"launch_date": "2006-08-25"}})

    @patch("aws_services_reporter.aws_client.rss_client.fetch_rss_data")
    def test_get_rss_region_launch_dates_fetch_failure(self, mock_fetch):
        """Test RSS data retrieval when fetch fails."""
        mock_fetch.return_value = None

        config = Config()
        result = get_rss_region_launch_dates(config)

        self.assertEqual(result, {})

    @patch("aws_services_reporter.aws_client.rss_client.fetch_rss_data")
    @patch("aws_services_reporter.aws_client.rss_client.parse_rss_launch_dates")
    def test_get_rss_region_launch_dates_parse_failure(self, mock_parse, mock_fetch):
        """Test RSS data retrieval when parsing fails."""
        mock_fetch.return_value = "<rss>mock data</rss>"
        mock_parse.side_effect = Exception("Parse error")

        config = Config()
        result = get_rss_region_launch_dates(config)

        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()
