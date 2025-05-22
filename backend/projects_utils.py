# projects_utils.py

import json
import os
import streamlit as st
from config_utils import get_config_directory # Import the correct function

PROJECTS_FILENAME = "projects.json"

def get_projects_filepath():
    """Gets the full path to the projects.json file."""
    # projects.json should reside in the same directory as config.json
    try:
        # Use the new function to get the directory directly
        config_dir = get_config_directory()
    except Exception as e: # Fallback if get_config_directory fails
        st.error(f"Error getting config directory: {e}. Defaulting to current directory for projects.json.")
        print(f"Error getting config directory: {e}. Defaulting to cwd.")
        config_dir = os.getcwd()
    return os.path.join(config_dir, PROJECTS_FILENAME)

def load_projects():
    """
    Loads project data from projects.json.
    Returns an empty dictionary if the file doesn't exist or is invalid.
    """
    filepath = get_projects_filepath()
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Handle empty file case
            content = f.read()
            if not content:
                return {}
            projects_data = json.loads(content)
            # Basic validation: ensure it's a dictionary
            if not isinstance(projects_data, dict):
                st.error(f"Error: {PROJECTS_FILENAME} does not contain a valid JSON object. Starting fresh.")
                return {}
            return projects_data
    except json.JSONDecodeError:
        st.error(f"Error decoding JSON from {filepath}. Starting with an empty project list.")
        return {}
    except Exception as e:
        st.error(f"An unexpected error occurred while loading projects: {e}")
        return {}

def save_projects(projects_data):
    """
    Saves the provided projects data dictionary to projects.json.
    """
    filepath = get_projects_filepath()
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(projects_data, f, indent=2, ensure_ascii=False)
        # Optional: Add a success message, but might be too noisy
        # st.toast("Projects saved successfully.")
    except Exception as e:
        st.error(f"An error occurred while saving projects: {e}")

def get_project_details(project_name):
    """
    Retrieves the details for a specific project by name.
    Returns the project's dictionary or None if not found.
    """
    projects = load_projects()
    return projects.get(project_name)

# Note: Ensure config_utils.py has a function get_config_path()
# that returns the expected path to config.json.
# Example placeholder if needed:
# def get_config_path():
#     # Logic to determine the path to config.json
#     # For example, it might be in the current working directory or a specific subfolder
#     return os.path.join(os.getcwd(), "config.json") # Adjust as needed
