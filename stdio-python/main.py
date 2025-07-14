import argparse
from config.env import load_env
from server.mcp_server import start_mcp_server

def main():
    parser = argparse.ArgumentParser(description="Run the Foxit Cloud API MCP Service.")
    parser.add_argument("--host", required=True, help="The Foxit Cloud API host URL.")
    parser.add_argument("--client_id", required=True, help="The Foxit Cloud API client ID.")
    parser.add_argument("--client_secret", required=True, help="The Foxit Cloud API client secret.")

    args = parser.parse_args()

    try:
        # Pass the arguments to the environment loader
        load_env(args.host, args.client_id, args.client_secret)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

    # Start the MCP server
    start_mcp_server("stdio")


if __name__ == "__main__":
    main()