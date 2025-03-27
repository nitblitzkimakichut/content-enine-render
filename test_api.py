import requests
import json
import sys

def test_full_pipeline():
    """Test the full pipeline endpoint with a sample request"""
    print("Testing TitanFlow AI full pipeline...")
    
    # Load the sample request
    with open('sample_request.json', 'r') as f:
        data = json.load(f)
    
    # Send the request to the API
    try:
        response = requests.post(
            'http://localhost:8000/full-pipeline',
            json=data
        )
        
        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            
            # Save the result to a file
            with open('pipeline_result.json', 'w') as f:
                json.dump(result, f, indent=2)
            
            # Print summary
            print("\n✅ Pipeline test successful!")
            print(f"Analysis found {len(result['analysis']['hook_patterns'])} hook patterns")
            print(f"Generated script: '{result['script']['title']}'")
            print(f"Visual plan with {len(result['visual_plan']['scenes'])} scenes")
            print("\nComplete result saved to pipeline_result.json")
            
        else:
            print(f"\n❌ Error: {response.status_code} - {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API server.")
        print("Make sure the API is running with: python content_strategy_api.py")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

def main():
    """Main function to run tests"""
    test_full_pipeline()

if __name__ == "__main__":
    main() 