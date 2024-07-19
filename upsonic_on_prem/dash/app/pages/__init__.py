import os
import importlib.util

# Define the path to the pages directory
pages_dir = os.path.dirname(__file__)

# Initialize the urls and pages lists
urls = []
pages = []

# List all subdirectories in the pages directory
for subdir in os.listdir(pages_dir):
    subdir_path = os.path.join(pages_dir, subdir)
    if os.path.isdir(subdir_path):
        page_file = os.path.join(subdir_path, 'page.py')
        if os.path.isfile(page_file):
            # Import the page.py file
            module_name = f"app.pages.{subdir}.page"
            spec = importlib.util.spec_from_file_location(module_name, page_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Assuming each page.py has an 'url' and 'location' attribute
            if hasattr(module, 'url'):
                urls.append(module.url)
            if hasattr(module, 'location'):
                pages.append([module.name, module.location])


