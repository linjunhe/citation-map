import requests
import pandas as pd
import time
from typing import Optional, List, Dict, Any

# Base URL for the OpenAlex API
OPENALEX_API_URL = "https://api.openalex.org"

def _get_paginated_results(session: requests.Session, url: str) -> List[Dict[str, Any]]:
    """
    A helper function to handle OpenAlex API cursor pagination.
    It fetches all pages of results for a given URL.
    """
    all_results = []
    # Use cursor pagination, starting with '*'
    params = {'per_page': 200, 'cursor': '*'}
    
    while params['cursor']:
        try:
            response = session.get(url, params=params)
            response.raise_for_status()  # Raise an exception for bad responses
            data = response.json()
            
            results = data.get('results', [])
            all_results.extend(results)
            
            # Get the next_cursor. If None, the loop will stop.
            params['cursor'] = data.get('meta', {}).get('next_cursor')
            
            # Comply with the OpenAlex politeness policy (10 requests/sec)
            time.sleep(0.1) 
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e} (URL: {url})")
            print(f"Response content: {response.text}")
            break  # Stop on error
            
    return all_results

def get_citation_data_by_orcid(orcid: str, output_csv: str, email: Optional[str] = None) -> None:
    """
    Fetches citation data for all publications of an author via their ORCID iD
    and exports the data to a CSV file.

    Args:
    orcid (str): The author's ORCID iD (e.g., "0000-0002-4255-2538").
    output_csv (str): The file path for the output CSV (e.g., "citations.csv").
    email (Optional[str]): Your email address. Providing this is polite practice
                           for the OpenAlex API, allowing them to contact you.
    """
    
    # 1. Set up the requests session
    session = requests.Session()
    if email:
        # Add the 'mailto' param for polite API access
        session.params = {'mailto': email}
        print(f"Set 'mailto' parameter to: {email}")

    # This list will store all rows for the final CSV
    all_rows = []

    try:
        # --- Step 1: Get the author's OpenAlex ID and works_api_url from ORCID ---
        # Note: OpenAlex API can handle the full ORCID URL or just the ID
        orcid_url = f"https://orcid.org/{orcid}"
        author_url = f"{OPENALEX_API_URL}/authors/{orcid_url}"
        
        print(f"Fetching author details: {author_url}")
        response = session.get(author_url)
        response.raise_for_status()
        author_data = response.json()
        
        works_api_url = author_data.get('works_api_url')
        if not works_api_url:
            print(f"Error: Could not find 'works_api_url' for ORCID: {orcid}")
            return

        print(f"Author found. Fetching works from: {works_api_url}")

        # --- Step 2: Get all publications for the author ---
        my_publications = _get_paginated_results(session, works_api_url)
        print(f"Found {len(my_publications)} total publications.")

        # --- Step 3: Iterate through each publication to get its citations ---
        for i, my_pub in enumerate(my_publications):
            my_pub_title = my_pub.get('title', 'N/A')
            cited_by_api_url = my_pub.get('cited_by_api_url')
            cited_by_count = my_pub.get('cited_by_count', 0)
            
            print(f"\n--- Processing my publication {i+1}/{len(my_publications)} ---")
            print(f"Title: {my_pub_title}")
            print(f"Citations: {cited_by_count}")

            if not cited_by_api_url or cited_by_count == 0:
                print("No citations or 'cited_by_api_url' unavailable. Skipping.")
                continue
                
            print(f"Fetching citing works from: {cited_by_api_url}")
            
            # Get all papers that cite this publication
            citing_papers = _get_paginated_results(session, cited_by_api_url)

            # --- Step 4: Extract details from each citing paper ---
            for citing_paper in citing_papers:
                # Internal key 'title'
                citing_title = citing_paper.get('title', 'N/A')
                authorships = citing_paper.get('authorships', [])
                
                if not authorships:
                    # Record the citing paper even if it has no author data
                    row = {
                        'my_publication': my_pub_title,
                        'cited_by_title': citing_title,
                        'cited_by_author': 'N/A',
                        'cited_by_institution': 'N/A',
                        'cited_by_country': 'N/A'
                    }
                    all_rows.append(row)
                    continue

                # Iterate through each author of the citing paper
                for authorship in authorships:
                    # Internal key 'author'
                    author_name = authorship.get('author', {}).get('display_name', 'N/A')
                    institutions = authorship.get('institutions', [])
                    
                    if not institutions:
                        # Record the author even if they have no institution data
                        row = {
                            'my_publication': my_pub_title,
                            'cited_by_title': citing_title,
                            'cited_by_author': author_name,
                            'cited_by_institution': 'N/A',
                            'cited_by_country': 'N/A'
                        }
                        all_rows.append(row)
                        continue

                    # Iterate through each institution for the author
                    for inst in institutions:
                        # Internal keys 'institution' and 'country'
                        inst_name = inst.get('display_name', 'N/A')
                        country_code = inst.get('country_code', 'N/A')
                        
                        # This is a single row in the final CSV
                        row = {
                            'my_publication': my_pub_title,
                            'cited_by_title': citing_title,
                            'cited_by_author': author_name,
                            'cited_by_institution': inst_name,
                            'cited_by_country': country_code
                        }
                        all_rows.append(row)

    except requests.exceptions.RequestException as e:
        print(f"A fatal API error occurred: {e}")
        return
    except Exception as e:
        print(f"An unexpected error occurred during data processing: {e}")
        return

    # --- Step 5: Export all collected data to a CSV ---
    if not all_rows:
        print("No citation data was found.")
        return
        
    print(f"\nData processing complete. Generated {len(all_rows)} total rows.")
    
    # Create DataFrame using Pandas
    df = pd.DataFrame(all_rows)
    
    # Reorder columns to match the user's request
    df = df[['my_publication', 'cited_by_title', 'cited_by_author', 'cited_by_institution', 'cited_by_country']]
    
    try:
        # Use 'utf-8-sig' encoding to ensure Excel handles non-English characters correctly
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"Data successfully exported to: {output_csv}")
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
