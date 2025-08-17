"""
Quick test script to verify the ETL agent setup

This script tests the basic functionality without requiring the ETL service to be running.
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        from core.api_client import APIClient, DataSource, User, QueryResult
        print("✅ API client imports successful")
    except ImportError as e:
        print(f"❌ API client import failed: {e}")
        return False
    
    try:
        from core.etl_agent import etl_agent, ETLAgentDeps
        print("✅ ETL agent imports successful")
    except ImportError as e:
        print(f"❌ ETL agent import failed: {e}")
        return False
    
    try:
        from core.model import get_openai_client, get_openai_model
        print("✅ Model imports successful")
    except ImportError as e:
        print(f"❌ Model imports failed: {e}")
        return False
    
    return True


def test_agent_initialization():
    """Test if the agent can be initialized."""
    print("\n🤖 Testing agent initialization...")
    
    try:
        from core.etl_agent import etl_agent, ETLAgentDeps
        from core.api_client import APIClient
        
        # Initialize with dummy values
        api_client = APIClient(base_url='http://localhost:8000', user_id='test-user')
        agent_deps = ETLAgentDeps(api_client=api_client)
        
        print("✅ Agent initialization successful")
        api_client.close()
        return True
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return False


def test_environment_setup():
    """Test environment configuration."""
    print("\n🌍 Testing environment setup...")
    
    # Check if .env.example exists
    env_example_path = Path(".env.example")
    if env_example_path.exists():
        print("✅ .env.example file found")
    else:
        print("❌ .env.example file not found")
        return False
    
    # Check if required environment variables are documented
    try:
        with open(env_example_path, 'r') as f:
            content = f.read()
            if 'API_KEY' in content and 'ETL_API_URL' in content:
                print("✅ Required environment variables documented")
            else:
                print("❌ Missing required environment variables in .env.example")
                return False
    except Exception as e:
        print(f"❌ Error reading .env.example: {e}")
        return False
    
    return True


def test_tool_availability():
    """Test if agent tools are properly registered."""
    print("\n🛠️  Testing tool availability...")
    
    try:
        from core.etl_agent import etl_agent
        
        # Check if agent has tools
        if hasattr(etl_agent, '_tools') and etl_agent._tools:
            print(f"✅ Agent has {len(etl_agent._tools)} tools registered")
            
            # List some key tools
            tool_names = [tool.name for tool in etl_agent._tools.values()]
            key_tools = ['ping_service', 'create_user', 'list_data_sources', 'query_data']
            
            for tool in key_tools:
                if tool in tool_names:
                    print(f"  ✅ {tool}")
                else:
                    print(f"  ❌ {tool} not found")
                    
        else:
            print("❌ No tools registered in agent")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Tool availability test failed: {e}")
        return False


def test_file_structure():
    """Test if all required files are present."""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'core/etl_agent.py',
        'core/api_client.py', 
        'core/model.py',
        'demo.py',
        'test_scenarios.py',
        'requirements.txt',
        '.env.example'
    ]
    
    all_files_present = True
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} missing")
            all_files_present = False
    
    return all_files_present


def main():
    """Run all tests."""
    print("🚀 ETL Pydantic AI Agent - Quick Test Suite")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Environment Setup", test_environment_setup),
        ("Module Imports", test_imports),
        ("Agent Initialization", test_agent_initialization),
        ("Tool Availability", test_tool_availability),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The ETL agent is ready to use.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your API keys")
        print("2. Ensure your ETL service is running")
        print("3. Run 'python demo.py' for interactive demo")
        print("4. Run 'python test_scenarios.py' for comprehensive testing")
        print("5. Start the API server with 'python main.py' or 'uvicorn main:app --reload'")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)