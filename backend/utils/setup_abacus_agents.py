#!/usr/bin/env python
# utils/setup_abacus_agents.py

"""
Agent Setup Utility for Abacus.ai Integration

This script helps set up the required agents in your Abacus.ai account
for the NeonChat application. It will create and deploy agents for:
- Image Generation
- Search
- Diary Entries
- Model Selection
- Generic LLM (Chat)

Before running:
1. Make sure you have installed the Abacus.ai SDK: pip install abacusai
2. Set your ABACUS_API_KEY in the .env file or environment
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List, Optional
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("abacus_setup")

# Add parent directory to path for imports when running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

def setup_argument_parser():
    """Set up command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Set up Abacus.ai agents for NeonChat integration"
    )
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Only list existing agents, don't create new ones"
    )
    parser.add_argument(
        "--create-agents",
        action="store_true",
        help="Create and deploy required agents"
    )
    parser.add_argument(
        "--update-env",
        action="store_true",
        help="Update .env file with agent deployment IDs"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test agent functionality after setup"
    )
    return parser

def get_abacus_client():
    """Get Abacus.ai client with API key from environment"""
    try:
        from abacusai import ApiClient
        
        api_key = os.environ.get("ABACUS_API_KEY")
        if not api_key:
            logger.error("ABACUS_API_KEY not found in environment variables")
            print("Please set ABACUS_API_KEY in your .env file or environment")
            sys.exit(1)
        
        client = ApiClient(api_key=api_key)
        logger.info("Successfully initialized Abacus.ai client")
        
        # Test connection
        # This will fail if the API key is invalid
        user_info = client.get_user_info()
        logger.info(f"Connected as user: {user_info.get('email', 'unknown')}")
        
        return client
    except ImportError:
        logger.error("Failed to import Abacus.ai SDK. Please install it first.")
        print("Install Abacus.ai SDK with: pip install abacusai")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error initializing Abacus.ai client: {str(e)}")
        print(f"Failed to connect to Abacus.ai: {str(e)}")
        sys.exit(1)

def list_existing_agents(client):
    """List existing agents in the Abacus.ai account"""
    try:
        # This is a placeholder - adjust based on actual Abacus.ai SDK method
        agents = client.list_agents()
        
        if not agents:
            logger.info("No agents found in your Abacus.ai account")
            return []
        
        print("\nExisting Agents:")
        print("=================")
        
        for idx, agent in enumerate(agents, 1):
            print(f"{idx}. Name: {agent.get('name')}")
            print(f"   ID: {agent.get('id')}")
            print(f"   Status: {agent.get('status')}")
            print(f"   Type: {agent.get('type')}")
            if agent.get('deployment_id'):
                print(f"   Deployment ID: {agent.get('deployment_id')}")
            print()
        
        return agents
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        print(f"Failed to list agents: {str(e)}")
        return []

def create_agent_configs():
    """Create configuration templates for required agents"""
    return {
        "image_generation": {
            "name": "NeonChat Image Generation Agent",
            "description": "Agent for generating images from text prompts",
            "type": "IMAGE_GENERATION",
            "properties": {
                "default_model": "dall-e-3",
                "default_size": "1024x1024",
                "default_quality": "standard"
            }
        },
        "search": {
            "name": "NeonChat Search Agent",
            "description": "Agent for performing web searches",
            "type": "SEARCH",
            "properties": {
                "default_search_type": "normal",
                "include_sources": True
            }
        },
        "diary": {
            "name": "NeonChat Diary Agent",
            "description": "Agent for saving and managing diary entries",
            "type": "DIARY",
            "properties": {
                "storage_enabled": True,
                "categorization_enabled": True
            }
        },
        "model_picker": {
            "name": "NeonChat Model Picker Agent",
            "description": "Agent for selecting the best model for a query",
            "type": "MODEL_SELECTOR",
            "properties": {
                "available_models": ["gpt-4", "claude-3-opus", "gemini-pro", "llama-3"]
            }
        },
        "generic_llm": {
            "name": "NeonChat Generic LLM Agent",
            "description": "Default agent for chat functionality",
            "type": "CHAT",
            "properties": {
                "default_model": "gpt-4",
                "temperature": 0.7,
                "system_prompt": "You are a helpful assistant in the NeonChat application."
            }
        }
    }

def create_and_deploy_agents(client, agent_configs):
    """Create and deploy agents based on configurations"""
    # Dictionary to store deployment IDs for created agents
    deployment_ids = {}
    
    for agent_key, config in agent_configs.items():
        try:
            logger.info(f"Creating agent: {config['name']}")
            print(f"\nCreating {config['name']}...")
            
            # This is a placeholder - adjust based on actual Abacus.ai SDK method
            # In a real implementation, this would create and then deploy the agent
            response = client.create_agent(
                name=config["name"],
                description=config["description"],
                agent_type=config["type"],
                properties=config["properties"]
            )
            
            agent_id = response.get("id")
            logger.info(f"Agent created with ID: {agent_id}")
            
            # Deploy the agent
            logger.info(f"Deploying agent: {config['name']}")
            deployment = client.deploy_agent(agent_id=agent_id)
            
            deployment_id = deployment.get("deployment_id")
            logger.info(f"Agent deployed with deployment ID: {deployment_id}")
            
            deployment_ids[agent_key] = deployment_id
            print(f"✅ {config['name']} created and deployed successfully")
            print(f"   Deployment ID: {deployment_id}")
            
        except Exception as e:
            logger.error(f"Error creating agent {config['name']}: {str(e)}")
            print(f"❌ Failed to create {config['name']}: {str(e)}")
    
    return deployment_ids

def update_env_file(deployment_ids):
    """Update .env file with agent deployment IDs"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    
    # Read existing content if file exists
    existing_content = {}
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    existing_content[key] = value
    
    # Update with new deployment IDs
    env_mapping = {
        "image_generation": "ABACUS_IMAGE_AGENT_ID",
        "search": "ABACUS_SEARCH_AGENT_ID",
        "diary": "ABACUS_DIARY_AGENT_ID",
        "model_picker": "ABACUS_MODEL_PICKER_AGENT_ID",
        "generic_llm": "ABACUS_GENERIC_LLM_AGENT_ID"
    }
    
    for agent_key, env_var in env_mapping.items():
        if agent_key in deployment_ids:
            existing_content[env_var] = deployment_ids[agent_key]
    
    # Write back to .env file
    with open(env_path, "w") as f:
        for key, value in existing_content.items():
            f.write(f"{key}={value}\n")
    
    logger.info(f"Updated .env file with agent deployment IDs")
    print(f"\n✅ Updated .env file with agent deployment IDs")
    print(f"   File location: {env_path}")

def test_agent_functionality(client, deployment_ids):
    """Test the functionality of deployed agents"""
    print("\nTesting Agent Functionality")
    print("==========================")
    
    try:
        # Test image generation
        if "image_generation" in deployment_ids:
            print("\nTesting Image Generation Agent...")
            response = client.execute_agent(
                deployment_id=deployment_ids["image_generation"],
                keyword_arguments={
                    "prompt": "A simple test image of a blue circle",
                    "size": "512x512",
                    "num_images": 1,
                    "quality_mode": "standard"
                }
            )
            if response.get("result", {}).get("image_urls"):
                print("✅ Image Generation Agent working correctly")
            else:
                print("❌ Image Generation Agent test failed")
        
        # Test search
        if "search" in deployment_ids:
            print("\nTesting Search Agent...")
            response = client.execute_agent(
                deployment_id=deployment_ids["search"],
                keyword_arguments={
                    "query": "What is Abacus.ai?",
                    "search_type": "normal"
                }
            )
            if response.get("result", {}).get("search_results"):
                print("✅ Search Agent working correctly")
            else:
                print("❌ Search Agent test failed")
        
        # Test diary agent
        if "diary" in deployment_ids:
            print("\nTesting Diary Agent...")
            response = client.execute_agent(
                deployment_id=deployment_ids["diary"],
                keyword_arguments={
                    "entry_text": "This is a test diary entry",
                    "user_id": "test_user"
                }
            )
            if response.get("success") or response.get("result"):
                print("✅ Diary Agent working correctly")
            else:
                print("❌ Diary Agent test failed")
        
        # Test model picker
        if "model_picker" in deployment_ids:
            print("\nTesting Model Picker Agent...")
            response = client.execute_agent(
                deployment_id=deployment_ids["model_picker"],
                keyword_arguments={
                    "prompt": "Generate an image of a sunset"
                }
            )
            if response.get("result", {}).get("model_id"):
                print("✅ Model Picker Agent working correctly")
            else:
                print("❌ Model Picker Agent test failed")
        
        # Test generic LLM
        if "generic_llm" in deployment_ids:
            print("\nTesting Generic LLM Agent...")
            response = client.execute_agent(
                deployment_id=deployment_ids["generic_llm"],
                keyword_arguments={
                    "prompt": "Hello, how are you?"
                }
            )
            if response.get("result", {}).get("response"):
                print("✅ Generic LLM Agent working correctly")
            else:
                print("❌ Generic LLM Agent test failed")
        
    except Exception as e:
        logger.error(f"Error testing agents: {str(e)}")
        print(f"❌ Agent testing failed: {str(e)}")

def main():
    """Main function to run the script"""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    print("Abacus.ai Agent Setup for NeonChat")
    print("=================================")
    
    # Get Abacus.ai client
    client = get_abacus_client()
    
    # List existing agents
    existing_agents = list_existing_agents(client)
    
    # If only listing, exit here
    if args.list_only:
        return
    
    # Create and deploy agents if requested
    deployment_ids = {}
    if args.create_agents:
        agent_configs = create_agent_configs()
        deployment_ids = create_and_deploy_agents(client, agent_configs)
    
    # Update .env file if requested
    if args.update_env and deployment_ids:
        update_env_file(deployment_ids)
    
    # Test agent functionality if requested
    if args.test and deployment_ids:
        test_agent_functionality(client, deployment_ids)
    
    print("\nSetup Complete!")
    print("==============")
    print("To use these agents in NeonChat, make sure your .env file contains all the deployment IDs")
    print("and the Abacus.ai service is properly configured.")
    
    # Print usage instructions
    if not args.create_agents:
        print("\nTo create agents, run: python setup_abacus_agents.py --create-agents --update-env")
    
    if not args.test and args.create_agents:
        print("\nTo test your agents, run: python setup_abacus_agents.py --test")

if __name__ == "__main__":
    main()
