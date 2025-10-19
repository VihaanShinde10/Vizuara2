import wikipedia
import os
import json
import time
import re
import logging
from datetime import datetime
from typing import Dict, List, Union, Optional, Any

# Configure logging
logger = logging.getLogger("WikiComicGenerator")


class WikipediaExtractor:
    def __init__(self, data_dir: str = "data", language: str = "en"):
        """
        Initialize the Wikipedia extractor
        
        Args:
            data_dir: Directory to store extracted data
            language: Wikipedia language code
        """
        self.data_dir = data_dir
        self.create_project_structure()
        
        # Set Wikipedia language
        wikipedia.set_lang(language)
        
        logger.info(f"WikipediaExtractor initialized with data directory: {data_dir}, language: {language}")

    def create_project_structure(self) -> None:
        """Create necessary directories for the project"""
        try:
            # Create data directory if it doesn't exist
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
                logger.info(f"Created data directory: {self.data_dir}")
            
            # Create images directory if it doesn't exist
            images_dir = os.path.join(self.data_dir, "images")
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
                logger.info(f"Created images directory: {images_dir}")
        except Exception as e:
            logger.error(f"Failed to create project structure: {str(e)}")
            raise RuntimeError(f"Failed to create project structure: {str(e)}")

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a string to be used as a filename
        
        Args:
            filename: Original filename string
            
        Returns:
            Sanitized filename safe for all operating systems
        """
        # Replace invalid characters with underscores
        sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
        # Limit filename length
        return sanitized[:200]

    def search_wikipedia(self, query: str, results_limit: int = 15, retries: int = 3) -> Union[List[str], str]:
        """
        Search Wikipedia for a given query and return search results
        
        Args:
            query: Search query
            results_limit: Maximum number of results to return
            retries: Number of retries on network failure
            
        Returns:
            List of search results or error message string
        """
        if not query or not query.strip():
            return "Please enter a valid search term."
        
        query = query.strip()
        logger.info(f"Searching Wikipedia for: {query}")
        
        # Implement retry logic with exponential backoff
        attempt = 0
        while attempt < retries:
            try:
                search_results = wikipedia.search(query, results=results_limit)
                
                if not search_results:
                    suggestions = wikipedia.suggest(query)
                    if suggestions:
                        logger.info(f"No results found. Suggesting: {suggestions}")
                        return f"No exact results found. Did you mean: {suggestions}?"
                    logger.info("No results found and no suggestions available")
                    return "No results found for your search."
                
                logger.info(f"Found {len(search_results)} results for query: {query}")
                return search_results
                
            except ConnectionError as e:
                attempt += 1
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Connection error (attempt {attempt}/{retries}): {str(e)}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            except Exception as e:
                logger.error(f"Search error: {str(e)}")
                return f"An error occurred while searching: {str(e)}"
        
        return "Failed to connect to Wikipedia after multiple attempts. Please check your internet connection."

    def get_page_info(self, title: str, retries: int = 3) -> Dict[str, Any]:
        """
        Get detailed information about a specific Wikipedia page
        
        Args:
            title: Page title to retrieve
            retries: Number of retries on network failure
            
        Returns:
            Dictionary containing page information or error details
        """
        logger.info(f"Getting page info for: {title}")
        
        attempt = 0
        while attempt < retries:
            try:
                # First try with exact title match
                try:
                    page = wikipedia.page(title, auto_suggest=False)
                except wikipedia.DisambiguationError as e:
                    # If disambiguation page, return options
                    logger.info(f"Disambiguation error for '{title}'. Returning options.")
                    return {
                        "error": "Disambiguation Error",
                        "options": e.options[:15],  # Limit to 15 options
                        "message": "Multiple matches found. Please be more specific."
                    }
                except wikipedia.PageError:
                    # If exact title not found, try with auto-suggest
                    try:
                        logger.info(f"Exact page '{title}' not found. Trying with auto-suggest.")
                        page = wikipedia.page(title)
                    except Exception as inner_e:
                        logger.error(f"Page retrieval error: {str(inner_e)}")
                        return {
                            "error": "Page Error",
                            "message": f"Page '{title}' does not exist."
                        }
                
                # Create a dictionary with all the information
                page_info = {
                    "title": page.title,
                    "url": page.url,
                    "content": page.content,
                    "summary": page.summary,
                    "references": page.references,
                    "categories": page.categories,
                    "links": page.links,
                    "images": page.images,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Save the extracted data
                self._save_extracted_data(page_info)
                
                logger.info(f"Successfully retrieved page info for: {title}")
                return page_info
                
            except ConnectionError as e:
                attempt += 1
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Connection error (attempt {attempt}/{retries}): {str(e)}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            except Exception as e:
                logger.error(f"Unexpected error getting page info: {str(e)}")
                return {
                    "error": "General Error",
                    "message": f"An error occurred: {str(e)}"
                }
        
        return {
            "error": "Connection Error",
            "message": "Failed to connect to Wikipedia after multiple attempts. Please check your internet connection."
        }

    def _save_extracted_data(self, page_info: Dict[str, Any]) -> None:
        """
        Save extracted data to a JSON file
        
        Args:
            page_info: Dictionary containing page information
        """
        try:
            safe_title = self.sanitize_filename(page_info["title"])
            filename = f"{self.data_dir}/{safe_title}_data.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(page_info, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Saved extracted data to: {filename}")
        except Exception as e:
            logger.error(f"Failed to save extracted data: {str(e)}")
