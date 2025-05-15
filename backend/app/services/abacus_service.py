# app/services/abacus_service.py
import os
from typing import Dict, Any, List, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("abacus_service")

class AbacusService:
    """
    Service for interacting with the Abacus.ai API.
    This service will handle all communication with Abacus.ai agents and models.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Abacus.ai service.
        
        Args:
            api_key: Abacus.ai API key (if not provided, uses the one from environment)
        """
        self.api_key = api_key or os.environ.get("ABACUS_API_KEY")
        if not self.api_key:
            logger.warning("No Abacus.ai API key provided. Service will not function properly.")
        
        # Initialize agent deployment IDs (these will be set once the agents are created in Abacus.ai)
        self.agent_deployments = {
            "image_generation": os.environ.get("ABACUS_IMAGE_AGENT_ID", ""),
            "search": os.environ.get("ABACUS_SEARCH_AGENT_ID", ""),
            "diary": os.environ.get("ABACUS_DIARY_AGENT_ID", ""),
            "model_picker": os.environ.get("ABACUS_MODEL_PICKER_AGENT_ID", ""),
            "generic_llm": os.environ.get("ABACUS_GENERIC_LLM_AGENT_ID", ""),
        }
        
        # Initialize the Abacus.ai client
        try:
            from abacusai import ApiClient
            self.client = ApiClient(api_key=self.api_key)
            logger.info("Abacus.ai client initialized successfully")
        except ImportError:
            logger.error("Failed to import Abacus.ai SDK. Please install it with: pip install abacusai")
            self.client = None
        except Exception as e:
            logger.error(f"Error initializing Abacus.ai client: {str(e)}")
            self.client = None
        
        logger.info("AbacusService initialized - awaiting SDK installation")
    
    async def generate_image(self, prompt: str, size: str = "1024x1024", 
                            count: int = 1, quality: str = "standard") -> Dict[str, Any]:
        """
        Generate images using the Abacus.ai Image Generation Agent.
        
        Args:
            prompt: The text prompt describing the desired image
            size: Image dimensions (e.g., "512x512", "1024x1024")
            count: Number of images to generate
            quality: Quality setting ("standard", "hd", "cheaper", "expensive")
            
        Returns:
            Dictionary containing generated image URLs or error information
        """
        logger.info(f"Generating {count} images with prompt: {prompt}")
        
        if not self.client:
            return {
                "success": False,
                "error": "Abacus.ai client not initialized. Check API key and SDK installation."
            }
            
        try:
            response = self.client.execute_agent(
                deployment_id=self.agent_deployments["image_generation"],
                keyword_arguments={
                    'prompt': prompt,
                    'size': size,
                    'num_images': count,
                    'quality_mode': quality
                }
            )
            
            # Log response for debugging
            logger.debug(f"Image generation response: {response}")
            
            # Extract image URLs from response
            images = response.get('result', {}).get('image_urls', [])
            if not images:
                return {"success": False, "error": "No images were generated"}
                
            return {"success": True, "images": images}
        except Exception as e:
            logger.error(f"Error generating images: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def search(self, query: str, search_type: str = "normal") -> Dict[str, Any]:
        """
        Perform a search using the Abacus.ai Search Agent.
        
        Args:
            query: The search query
            search_type: Type of search ("normal" or "deep_research")
            
        Returns:
            Dictionary containing search results or error information
        """
        logger.info(f"Performing {search_type} search with query: {query}")
        
        if not self.client:
            return {
                "success": False,
                "error": "Abacus.ai client not initialized. Check API key and SDK installation."
            }
            
        try:
            # Configure search parameters based on search type
            search_args = {
                'query': query,
                'search_type': search_type,
                'max_results': 10  # Default number of results to return
            }
            
            # If deep research is selected, add additional parameters
            if search_type == "deep_research":
                search_args['depth'] = 'high'
                search_args['include_sources'] = True
            
            response = self.client.execute_agent(
                deployment_id=self.agent_deployments["search"],
                keyword_arguments=search_args
            )
            
            # Log response for debugging
            logger.debug(f"Search response: {response}")
            
            # Extract search results from response
            results = response.get('result', {}).get('search_results', [])
            if not results:
                return {"success": False, "error": "No search results found"}
                
            return {
                "success": True, 
                "results": results,
                "search_type": search_type
            }
        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def save_diary_entry(self, entry_text: str, user_id: str, 
                              context: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Save a diary entry using the Abacus.ai Diary Agent.
        
        Args:
            entry_text: The diary entry text
            user_id: User identifier
            context: Optional conversation context
            
        Returns:
            Dictionary containing confirmation or error information
        """
        logger.info(f"Saving diary entry for user {user_id}")
        
        if not self.client:
            return {
                "success": False,
                "error": "Abacus.ai client not initialized. Check API key and SDK installation."
            }
            
        try:
            # Prepare diary entry data
            diary_args = {
                'entry_text': entry_text,
                'user_id': user_id
            }
            
            # Add context if provided
            if context:
                diary_args['context'] = context
            
            response = self.client.execute_agent(
                deployment_id=self.agent_deployments["diary"],
                keyword_arguments=diary_args
            )
            
            # Log response for debugging
            logger.debug(f"Diary entry response: {response}")
            
            # Check for success in the response
            if response.get('success', False):
                return {
                    "success": True,
                    "message": "Diary entry saved successfully",
                    "entry_id": response.get('result', {}).get('entry_id', '')
                }
            else:
                return {"success": False, "error": "Failed to save diary entry"}
                
        except Exception as e:
            logger.error(f"Error saving diary entry: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def chat(self, prompt: str, model_id: Optional[str] = None, 
                  conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Chat with an Abacus.ai model or agent.
        
        Args:
            prompt: The user's message
            model_id: Specific model or agent ID to use (if None, uses the generic LLM agent)
            conversation_history: Previous conversation messages
            
        Returns:
            Dictionary containing the response or error information
        """
        logger.info(f"Sending chat message to Abacus.ai{f' using model {model_id}' if model_id else ''}")
        
        if not self.client:
            return {
                "success": False,
                "error": "Abacus.ai client not initialized. Check API key and SDK installation."
            }
            
        try:
            # If no model_id is provided, use the generic LLM agent
            deployment_id = model_id or self.agent_deployments["generic_llm"]
            
            # Prepare chat arguments
            chat_args = {
                'prompt': prompt
            }
            
            # Add conversation history if provided
            if conversation_history:
                chat_args['conversation_history'] = conversation_history
            
            response = self.client.execute_agent(
                deployment_id=deployment_id,
                keyword_arguments=chat_args
            )
            
            # Log response for debugging
            logger.debug(f"Chat response: {response}")
            
            # Extract response content
            response_text = response.get('result', {}).get('response', '')
            if not response_text:
                return {"success": False, "error": "No response generated"}
                
            return {
                "success": True,
                "response": response_text,
                "model_used": deployment_id
            }
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def pick_model(self, prompt: str, 
                         conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Use the Model Picker Agent to determine the best model for a given query.
        
        Args:
            prompt: The user's message
            conversation_history: Previous conversation messages
            
        Returns:
            Model ID that's best suited for the query
        """
        logger.info(f"Picking best model for prompt: {prompt[:50]}...")
        
        if not self.client:
            logger.warning("Abacus.ai client not initialized, using default model")
            return self.agent_deployments["generic_llm"]
            
        try:
            # Prepare model picker arguments
            picker_args = {
                'prompt': prompt
            }
            
            # Add conversation history if provided
            if conversation_history:
                picker_args['conversation_history'] = conversation_history
            
            response = self.client.execute_agent(
                deployment_id=self.agent_deployments["model_picker"],
                keyword_arguments=picker_args
            )
            
            # Extract the recommended model ID
            model_id = response.get('result', {}).get('model_id', '')
            
            if not model_id:
                logger.warning("No model recommendation received, using default model")
                return self.agent_deployments["generic_llm"]
                
            logger.info(f"Model picker recommended: {model_id}")
            return model_id
            
        except Exception as e:
            logger.error(f"Error in model picker: {str(e)}")
            # Fall back to default model on error
            return self.agent_deployments["generic_llm"]


# Create a singleton instance
abacus_service = AbacusService()
