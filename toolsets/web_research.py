"""
Web Research Toolset
Combines web operations and data processing for comprehensive research tasks.
"""

from typing import Dict, List, Any, Optional
import json
import time
from datetime import datetime

from ..tools.web_operations import WebOperationsTool
from ..tools.data_processing import DataProcessingTool
from ..tools.file_operations import FileOperationsTool

class WebResearchToolset:
    """
    Comprehensive web research toolset that combines web scraping,
    data processing, and file operations for research tasks.
    """
    
    def __init__(self, base_path: str = "./research_data"):
        """
        Initialize web research toolset.
        
        Args:
            base_path: Base directory for storing research data
        """
        self.web_tool = WebOperationsTool()
        self.data_tool = DataProcessingTool()
        self.file_tool = FileOperationsTool(base_path)
        self.base_path = base_path
        
    def research_topic(self, topic: str, max_sources: int = 10) -> Dict[str, Any]:
        """
        Conduct comprehensive research on a topic.
        
        Args:
            topic: Research topic
            max_sources: Maximum number of sources to analyze
            
        Returns:
            Dictionary with research results
        """
        try:
            research_session = {
                "topic": topic,
                "timestamp": datetime.now().isoformat(),
                "sources": [],
                "summary": {},
                "data_file": None
            }
            
            # Create research directory
            session_dir = f"research_{topic.replace(' ', '_')}_{int(time.time())}"
            self.file_tool.create_directory(session_dir)
            
            # Search for sources (placeholder - would integrate with search API)
            search_results = self.web_tool.search_web(topic, max_sources)
            
            if not search_results["success"]:
                return {"success": False, "error": "Search failed"}
            
            # Process each source
            for i, result in enumerate(search_results["results"][:max_sources]):
                source_data = self._process_source(result, session_dir, i)
                if source_data["success"]:
                    research_session["sources"].append(source_data["data"])
                
                # Rate limiting
                time.sleep(1)
            
            # Generate summary
            research_session["summary"] = self._generate_research_summary(research_session["sources"])
            
            # Save research data
            data_file = f"{session_dir}/research_data.json"
            save_result = self.file_tool.write_file(data_file, json.dumps(research_session, indent=2))
            
            if save_result["success"]:
                research_session["data_file"] = data_file
            
            return {
                "success": True,
                "research": research_session,
                "session_dir": session_dir
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_website_structure(self, url: str, depth: int = 2) -> Dict[str, Any]:
        """
        Analyze website structure and extract comprehensive information.
        
        Args:
            url: Website URL to analyze
            depth: Depth of crawling (limited for safety)
            
        Returns:
            Dictionary with website analysis
        """
        try:
            analysis = {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "structure": {},
                "content_analysis": {},
                "security_analysis": {},
                "performance_metrics": {}
            }
            
            # Scrape main page
            main_page = self.web_tool.scrape_webpage(url)
            if not main_page["success"]:
                return {"success": False, "error": "Failed to scrape main page"}
            
            # Analyze structure
            analysis["structure"] = {
                "title": main_page.get("title", ""),
                "total_links": len(main_page.get("links", [])),
                "total_images": len(main_page.get("images", [])),
                "meta_tags": main_page.get("meta_tags", {}),
                "content_length": len(main_page.get("text", ""))
            }
            
            # Content analysis
            text_content = main_page.get("text", "")
            analysis["content_analysis"] = self._analyze_content(text_content)
            
            # Security analysis
            analysis["security_analysis"] = self._analyze_website_security(main_page)
            
            # Extract and analyze links (limited depth for safety)
            if depth > 0 and len(main_page.get("links", [])) > 0:
                sample_links = main_page["links"][:5]  # Limit for safety
                analysis["linked_pages"] = []
                
                for link in sample_links:
                    link_analysis = self._analyze_linked_page(link["url"])
                    if link_analysis["success"]:
                        analysis["linked_pages"].append(link_analysis["data"])
            
            # Save analysis
            timestamp = int(time.time())
            filename = f"website_analysis_{timestamp}.json"
            self.file_tool.write_file(filename, json.dumps(analysis, indent=2))
            
            return {
                "success": True,
                "analysis": analysis,
                "filename": filename
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def monitor_website_changes(self, url: str, check_interval: int = 3600) -> Dict[str, Any]:
        """
        Monitor website for changes (basic implementation).
        
        Args:
            url: Website URL to monitor
            check_interval: Check interval in seconds
            
        Returns:
            Dictionary with monitoring setup
        """
        try:
            # Get current state
            current_state = self.web_tool.scrape_webpage(url)
            if not current_state["success"]:
                return {"success": False, "error": "Failed to fetch website"}
            
            # Calculate content hash
            content_hash = self._calculate_content_hash(current_state["content"])
            
            monitoring_data = {
                "url": url,
                "check_interval": check_interval,
                "last_check": datetime.now().isoformat(),
                "content_hash": content_hash,
                "title": current_state.get("title", ""),
                "status": "monitoring_active"
            }
            
            # Save monitoring state
            filename = f"monitor_{url.replace('https://', '').replace('/', '_')}.json"
            self.file_tool.write_file(filename, json.dumps(monitoring_data, indent=2))
            
            return {
                "success": True,
                "monitoring": monitoring_data,
                "filename": filename,
                "note": "This is a basic implementation. For continuous monitoring, implement a scheduled task."
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def extract_structured_data(self, url: str) -> Dict[str, Any]:
        """
        Extract structured data (JSON-LD, microdata) from webpage.
        
        Args:
            url: Webpage URL
            
        Returns:
            Dictionary with structured data
        """
        try:
            # Fetch webpage
            page_data = self.web_tool.scrape_webpage(url)
            if not page_data["success"]:
                return {"success": False, "error": "Failed to fetch webpage"}
            
            # Extract JSON data
            json_extraction = self.web_tool.extract_json_from_html(page_data["content"])
            
            # Analyze structured data
            structured_data = {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "json_ld_data": json_extraction.get("structured_data", []),
                "embedded_json": json_extraction.get("json_data", []),
                "analysis": {}
            }
            
            # Analyze structured data
            if structured_data["json_ld_data"]:
                structured_data["analysis"] = self._analyze_structured_data(structured_data["json_ld_data"])
            
            # Save results
            filename = f"structured_data_{int(time.time())}.json"
            self.file_tool.write_file(filename, json.dumps(structured_data, indent=2))
            
            return {
                "success": True,
                "structured_data": structured_data,
                "filename": filename
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _process_source(self, source: Dict[str, Any], session_dir: str, index: int) -> Dict[str, Any]:
        """Process a single research source."""
        try:
            url = source.get("url", "")
            if not url:
                return {"success": False, "error": "No URL provided"}
            
            # Scrape webpage
            page_data = self.web_tool.scrape_webpage(url)
            if not page_data["success"]:
                return {"success": False, "error": f"Failed to scrape {url}"}
            
            # Extract and save content
            source_data = {
                "url": url,
                "title": page_data.get("title", ""),
                "content": page_data.get("text", ""),
                "links": page_data.get("links", []),
                "images": page_data.get("images", []),
                "meta_tags": page_data.get("meta_tags", {}),
                "timestamp": datetime.now().isoformat()
            }
            
            # Save individual source
            filename = f"{session_dir}/source_{index:02d}.json"
            self.file_tool.write_file(filename, json.dumps(source_data, indent=2))
            
            return {
                "success": True,
                "data": source_data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_research_summary(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of research sources."""
        if not sources:
            return {"total_sources": 0, "analysis": "No sources found"}
        
        total_content = " ".join([source.get("content", "") for source in sources])
        
        summary = {
            "total_sources": len(sources),
            "total_words": len(total_content.split()),
            "unique_domains": len(set([source["url"].split("/")[2] for source in sources if "url" in source])),
            "common_keywords": self._extract_keywords(total_content),
            "source_titles": [source.get("title", "") for source in sources]
        }
        
        return summary
    
    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze text content."""
        words = content.split()
        sentences = content.split('.')
        
        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "average_words_per_sentence": len(words) / len(sentences) if sentences else 0,
            "keywords": self._extract_keywords(content),
            "readability_score": self._calculate_readability(content)
        }
    
    def _analyze_website_security(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic security analysis of webpage."""
        security_issues = []
        
        # Check for mixed content
        links = page_data.get("links", [])
        http_links = [link for link in links if link.get("url", "").startswith("http://")]
        if http_links:
            security_issues.append("Mixed content detected - HTTP resources on HTTPS page")
        
        # Check for external scripts
        content = page_data.get("content", "")
        if "script src=" in content.lower():
            security_issues.append("External scripts detected")
        
        return {
            "security_issues": security_issues,
            "risk_level": "low" if not security_issues else "medium",
            "recommendations": self._get_security_recommendations(security_issues)
        }
    
    def _analyze_linked_page(self, url: str) -> Dict[str, Any]:
        """Analyze a linked page (basic analysis)."""
        try:
            # Validate URL first
            validation = self.web_tool.validate_url(url)
            if not validation.get("valid", False):
                return {"success": False, "error": "Invalid URL"}
            
            # Get basic info (HEAD request for safety)
            response = self.web_tool.fetch_url(url, method="HEAD")
            if response["success"]:
                return {
                    "success": True,
                    "data": {
                        "url": url,
                        "status_code": response["status_code"],
                        "content_type": response["headers"].get("content-type", ""),
                        "content_length": response["headers"].get("content-length", "")
                    }
                }
            
            return {"success": False, "error": "Failed to fetch page"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate hash of content for change detection."""
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()
    
    def _extract_keywords(self, content: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from content."""
        # Simple keyword extraction (would use NLP libraries in production)
        words = content.lower().split()
        word_freq = {}
        
        for word in words:
            if len(word) > 3:  # Filter short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
    
    def _calculate_readability(self, content: str) -> float:
        """Simple readability score."""
        sentences = content.split('.')
        words = content.split()
        
        if not sentences:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        # Simple readability score (lower is more readable)
        return min(100.0, avg_sentence_length * 2)
    
    def _analyze_structured_data(self, structured_data: List[Dict]) -> Dict[str, Any]:
        """Analyze structured data (JSON-LD)."""
        analysis = {
            "total_items": len(structured_data),
            "data_types": [],
            "properties": set()
        }
        
        for item in structured_data:
            if isinstance(item, dict):
                data_type = item.get("@type", "unknown")
                if data_type not in analysis["data_types"]:
                    analysis["data_types"].append(data_type)
                
                analysis["properties"].update(item.keys())
        
        analysis["properties"] = list(analysis["properties"])
        return analysis
    
    def _get_security_recommendations(self, issues: List[str]) -> List[str]:
        """Get security recommendations based on issues."""
        recommendations = []
        
        for issue in issues:
            if "mixed content" in issue.lower():
                recommendations.append("Update all HTTP resources to HTTPS")
            elif "external scripts" in issue.lower():
                recommendations.append("Review and validate all external scripts")
        
        return recommendations

# Toolset metadata
TOOLSET_INFO = {
    "name": "web_research",
    "description": "Comprehensive web research toolset combining web operations and data analysis",
    "version": "1.0.0",
    "author": "CBW Agents",
    "capabilities": [
        "research_topic",
        "analyze_website_structure",
        "monitor_website_changes",
        "extract_structured_data"
    ],
    "tools_used": ["web_operations", "data_processing", "file_operations"],
    "safety_features": [
        "Rate limiting",
        "Request timeouts",
        "Depth limiting",
        "Content validation",
        "Error handling"
    ]
}

if __name__ == "__main__":
    # Example usage
    toolset = WebResearchToolset()
    
    # Test website analysis
    result = toolset.analyze_website_structure("https://example.com")
    print("Website analysis:", result["success"])