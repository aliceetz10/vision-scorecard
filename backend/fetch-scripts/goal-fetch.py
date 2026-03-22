import os
import requests
import pypdf # You need to install this: pip install pypdf

# Setup paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT should be the 'backend' folder if we are in 'backend/fetch-scripts'
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# The URLs of the PDF files
waterloo_pdf_url = "https://www.waterloo.ca/media/3hynwfeg/strategic-plan-2023-2026.pdf"
kitchener_pdf_url = "https://www.kitchener.ca/media/txvmxzyl/cao_2023-2026_strategic_plan.pdf"
cambridge_pdf_url = "https://www.cambridge.ca/en/learn-about/resources/strategic-plan/City-of-Cambridge-2024-2026-StrategicPlan.pdf"

# The names and paths for local files
# We ensure they go into backend/data/raw and backend/data/processed
waterloo_local_filename = os.path.join(PROJECT_ROOT, "data", "raw", "Waterloo_Strategic_Plan_2023-2026.pdf")
waterloo_text_filename = os.path.join(PROJECT_ROOT, "data", "processed", "Waterloo_Strategic_Plan_2023-2026.txt")

kitchener_local_filename = os.path.join(PROJECT_ROOT, "data", "raw", "Kitchener_Strategic_Plan_2023-2026.pdf")
kitchener_text_filename = os.path.join(PROJECT_ROOT, "data", "processed", "Kitchener_Strategic_Plan_2023-2026.txt")

cambridge_local_filename = os.path.join(PROJECT_ROOT, "data", "raw", "Cambridge_Strategic_Plan_2024-2026.pdf")
cambridge_text_filename = os.path.join(PROJECT_ROOT, "data", "processed", "Cambridge_Strategic_Plan_2024-2026.txt")

def download_pdf(url, filename):
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, stream=True)
        
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Success! Document saved as: {filename}")
            return True
        else:
            print(f"Failed to download {url}. Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"An error occurred during download of {url}: {e}")
        return False

def extract_text(pdf_path, txt_path):
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(txt_path), exist_ok=True)
        
        print(f"Converting {pdf_path} to text...")
        with open(pdf_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            text = ""
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"--- Page {i+1} ---\n" + page_text + "\n"
            
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Success! Text saved as: {txt_path}")
        
    except Exception as e:
        print(f"An error occurred during text extraction of {pdf_path}: {e}")

if __name__ == "__main__":
    # Waterloo
    if download_pdf(waterloo_pdf_url, waterloo_local_filename):
        extract_text(waterloo_local_filename, waterloo_text_filename)
        
    # Kitchener
    if download_pdf(kitchener_pdf_url, kitchener_local_filename):
        extract_text(kitchener_local_filename, kitchener_text_filename)
        
    # Cambridge
    if download_pdf(cambridge_pdf_url, cambridge_local_filename):
        extract_text(cambridge_local_filename, cambridge_text_filename)