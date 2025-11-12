"""
Web Operations Tool
Provides safe web operations for AI agents including scraping, API calls, and data extraction.
"""

import requests
import json
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urljoin, urlparse
import time
import hashlib

class WebOperationsTool:
    """
    Comprehensive web operations tool for AI agents.
    Supports web scraping, API calls, and data extraction with safety features.
    """
    
    def __init__(self, timeout: int = 30, max_retries: int = 3, delay_between_requests: float = 1.0):
        """
        Initialize web operations tool.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            delay_between_requests: Delay between requests in seconds
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.delay_between_requests = delay_between_requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CBW-Agent-WebTool/1.0 (Educational Purpose)'
        })
        self.last_request_time = 0
        
        # Rate limiting
        self.rate_limit_domains = {}
        
    def fetch_url(self, url: str, method: str = "GET", data: Optional[Dict] = None, 
                  headers: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Fetch content from URL with retry logic and rate limiting.
        
        Args:
            url: URL to fetch
            method: HTTP method (GET, POST, PUT, DELETE)
            data: Request data
            headers: Additional headers
            
        Returns:
            Dictionary with response data
        """
        try:
            # Rate limiting
            self._enforce_rate_limit(url)
            
            # Prepare request
            request_headers = {}
            if headers:
                request_headers.update(headers)
                
            for attempt in range(self.max_retries):
                try:
                    response = self.session.request(
                        method=method,
                        url=url,
                        json=data if method in ["POST", "PUT"] else None,
                        headers=request_headers,
                        timeout=self.timeout
                    )
                    
                    response.raise_for_status()
                    
                    return {
                        "success": True,
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "content": response.text,
                        "url": response.url,
                        "encoding": response.encoding
                    }
                    
                except requests.exceptions.RequestException as e:
                    if attempt == self.max_retries - 1:
                        return {"success": False, "error": str(e)}
                    
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def scrape_webpage(self, url: str, extract_links: bool = True, 
                      extract_images: bool = True, extract_text: bool = True) -> Dict[str, Any]:
        """
        Scrape webpage content and extract structured data.
        
        Args:
            url: URL to scrape
            extract_links: Whether to extract links
            extract_images: Whether to extract images
            extract_text: Whether to extract text content
            
        Returns:
            Dictionary with scraped data
        """
        try:
            # Fetch the webpage
            fetch_result = self.fetch_url(url)
            if not fetch_result["success"]:
                return fetch_result
                
            html_content = fetch_result["content"]
            soup = BeautifulSoup(html_content, 'html.parser')
            
            result = {
                "success": True,
                "url": url,
                "title": soup.title.string if soup.title else "",
                "metadata": {
                    "status_code": fetch_result["status_code"],
                    "encoding": fetch_result["encoding"]
                }
            }
            
            # Extract text content
            if extract_text:
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                    
                result["text"] = soup.get_text(separator=' ', strip=True)
            
            # Extract links
            if extract_links:
                links = []
                for link in soup.find_all('a', href=True):
                    absolute_url = urljoin(url, link['href'])
                    links.append({
                        "text": link.get_text(strip=True),
                        "url": absolute_url,
                        "title": link.get('title', '')
                    })
                result["links"] = links
            
            # Extract images
            if extract_images:
                images = []
                for img in soup.find_all('img', src=True):
                    absolute_url = urljoin(url, img['src'])
                    images.append({
                        "url": absolute_url,
                        "alt": img.get('alt', ''),
                        "title": img.get('title', '')
                    })
                result["images"] = images
            
            # Extract meta tags
            meta_tags = {}
            for meta in soup.find_all('meta'):
                name = meta.get('name') or meta.get('property')
                content = meta.get('content')
                if name and content:
                    meta_tags[name] = content
            result["meta_tags"] = meta_tags
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_web(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """
        Perform web search (placeholder - would need actual search API).
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            Dictionary with search results
        """
        # This is a placeholder implementation
        # In practice, you'd integrate with a search API like Google, Bing, or DuckDuckGo
        
        return {
            "success": True,
            "query": query,
            "results": [
                {
                    "title": f"Search result for: {query}",
                    "url": "https://example.com",
                    "snippet": "This is a placeholder search result."
                }
            ],
            "note": "This is a placeholder. Implement with actual search API."
        }
    
    def download_file(self, url: str, save_path: str, chunk_size: int = 8192) -> Dict[str, Any]:
        """
        Download file from URL.
        
        Args:
            url: URL to download from
            save_path: Local path to save file
            chunk_size: Download chunk size
            
        Returns:
            Dictionary with download result
        """
        try:
            self._enforce_rate_limit(url)
            
            response = self.session.get(url, stream=True, timeout=self.timeout)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
            
            return {
                "success": True,
                "file_path": save_path,
                "size": downloaded_size,
                "total_size": total_size,
                "url": url
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def validate_url(self, url: str) -> Dict[str, Any]:
        """
        Validate URL format and accessibility.
        
        Args:
            url: URL to validate
            
        Returns:
            Dictionary with validation result
        """
        try:
            parsed = urlparse(url)
            
            if not all([parsed.scheme, parsed.netloc]):
                return {"valid": False, "error": "Invalid URL format"}
                
            if parsed.scheme not in ['http', 'https']:
                return {"valid": False, "error": "Only HTTP/HTTPS URLs allowed"}
                
            # Try to make a HEAD request to check accessibility
            response = self.session.head(url, timeout=self.timeout)
            
            return {
                "valid": True,
                "accessible": response.status_code < 400,
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type', ''),
                "content_length": response.headers.get('content-length', '')
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def extract_json_from_html(self, html_content: str) -> Dict[str, Any]:
        """
        Extract JSON data from HTML (useful for SPAs and APIs).
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            Dictionary with extracted JSON data
        """
        try:
            # Look for JSON in script tags
            json_pattern = r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>'
            matches = re.findall(json_pattern, html_content, re.DOTALL)
            
            extracted_data = []
            for match in matches:
                try:
                    json_data = json.loads(match.strip())
                    extracted_data.append(json_data)
                except json.JSONDecodeError:
                    continue
            
            # Look for JSON-LD structured data
            jsonld_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
            jsonld_matches = re.findall(jsonld_pattern, html_content, re.DOTALL)
            
            structured_data = []
            for match in jsonld_matches:
                try:
                    json_data = json.loads(match.strip())
                    structured_data.append(json_data)
                except json.JSONDecodeError:
                    continue
            
            return {
                "success": True,
                "json_data": extracted_data,
                "structured_data": structured_data,
                "total_found": len(extracted_data) + len(structured_data)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _enforce_rate_limit(self, url: str):
        """Enforce rate limiting for domains."""
        domain = urlparse(url).netloc
        current_time = time.time()
        
        if domain in self.rate_limit_domains:
            time_since_last = current_time - self.rate_limit_domains[domain]
            if time_since_last < self.delay_between_requests:
                time.sleep(self.delay_between_requests - time_since_last)
        
        self.rate_limit_domains[domain] = time.time()

# Tool metadata
TOOL_INFO = {
    "name": "web_operations",
    "description": "Comprehensive web operations tool for scraping and API calls",
    "version": "1.0.0",
    "author": "CBW Agents",
    "capabilities": [
        "fetch_url",
        "scrape_webpage",
        "search_web",
        "download_file",
        "validate_url",
        "extract_json_from_html"
    ],
    "requirements": ["requests", "beautifulsoup4", "urllib.parse", "re", "time"],
    "safety_features": [
        "Rate limiting",
        "Request timeout",
        "Retry logic",
        "User agent spoofing",
        "Error handling"
    ]
}

if __name__ == "__main__":
    # Example usage
    tool = WebOperationsTool()
    
    # Test URL validation
    result = tool.validate_url("https://example.com")
    print("Validation result:", result)
    
    # Test webpage scraping
    result = tool.scrape_webpage("https://example.com")
    print("Scraping result:", result.get("success", False))