# tests/test_abacus_integration.py
import os
import sys
import asyncio
import json
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.abacus_service import abacus_service

# Load environment variables
load_dotenv()

async def test_image_generation():
    """Test image generation with Abacus.ai"""
    print("\n--- Testing Image Generation ---")
    result = await abacus_service.generate_image(
        prompt="A futuristic neon city skyline with flying cars",
        size="1024x1024",
        count=1,
        quality="standard"
    )
    print(f"Result: {json.dumps(result, indent=2)}")
    
    if result.get("success"):
        print("✅ Image generation test passed")
    else:
        print(f"❌ Image generation test failed: {result.get('error')}")
    
    return result

async def test_search():
    """Test search functionality with Abacus.ai"""
    print("\n--- Testing Search ---")
    result = await abacus_service.search(
        query="latest advancements in AI technology",
        search_type="normal"
    )
    print(f"Result: {json.dumps(result, indent=2)}")
    
    if result.get("success"):
        print("✅ Search test passed")
    else:
        print(f"❌ Search test failed: {result.get('error')}")
    
    return result

async def test_diary_entry():
    """Test diary entry saving with Abacus.ai"""
    print("\n--- Testing Diary Entry ---")
    result = await abacus_service.save_diary_entry(
        entry_text="Today I learned about Abacus.ai integration and its powerful features.",
        user_id="test_user_123",
        context=[
            {"role": "system", "content": "Diary entry from testing"},
            {"role": "user", "content": "Save this as a diary entry"}
        ]
    )
    print(f"Result: {json.dumps(result, indent=2)}")
    
    if result.get("success"):
        print("✅ Diary entry test passed")
    else:
        print(f"❌ Diary entry test failed: {result.get('error')}")
    
    return result

async def test_chat():
    """Test chat functionality with Abacus.ai"""
    print("\n--- Testing Chat ---")
    result = await abacus_service.chat(
        prompt="Tell me about the key features of Abacus.ai",
        conversation_history=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What can you tell me about AI platforms?"},
            {"role": "assistant", "content": "AI platforms provide various services like model training, deployment, and monitoring."}
        ]
    )
    print(f"Result: {json.dumps(result, indent=2)}")
    
    if result.get("success"):
        print("✅ Chat test passed")
    else:
        print(f"❌ Chat test failed: {result.get('error')}")
    
    return result

async def test_model_picker():
    """Test model picker functionality with Abacus.ai"""
    print("\n--- Testing Model Picker ---")
    model_id = await abacus_service.pick_model(
        prompt="Generate an image of a neon sign with the text 'Hello World'",
        conversation_history=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "I want to create some visual content."}
        ]
    )
    print(f"Recommended model: {model_id}")
    
    if model_id:
        print("✅ Model picker test passed")
    else:
        print("❌ Model picker test failed: No model recommended")
    
    return model_id

async def run_all_tests():
    """Run all Abacus.ai integration tests"""
    print("Running Abacus.ai Integration Tests")
    print("==================================")
    
    # Check if API key is set
    if not os.environ.get("ABACUS_API_KEY"):
        print("⚠️ WARNING: ABACUS_API_KEY not set in environment variables")
        print("Tests will likely fail. Please set the API key in your .env file")
    
    # Run all tests
    tests = [
        test_image_generation(),
        test_search(),
        test_diary_entry(),
        test_chat(),
        test_model_picker()
    ]
    
    results = await asyncio.gather(*tests)
    
    # Print summary
    print("\nTest Summary")
    print("===========")
    success_count = sum(1 for r in results[:4] if isinstance(r, dict) and r.get("success"))
    model_picker_success = bool(results[4])
    
    print(f"Tests passed: {success_count}/4 API endpoints")
    print(f"Model picker: {'✅ Passed' if model_picker_success else '❌ Failed'}")
    
    # Overall success status
    if success_count == 4 and model_picker_success:
        print("\n✅ All tests passed! Abacus.ai integration is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the above results for details.")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
