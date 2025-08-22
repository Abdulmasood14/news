import streamlit as st
import pandas as pd
import os
import glob
from datetime import datetime, date
import re
import requests
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="Company Scraper Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .company-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #ff6b9d 100%);
        border-radius: 25px;
        color: white;
        text-align: center;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        min-height: 200px;
        font-size: 26px;
        font-weight: 700;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        position: relative;
        overflow: hidden;
        padding: 60px 20px;
        cursor: pointer;
        border: none;
        margin: 10px 0;
    }
    
    .company-card:hover {
        transform: translateY(-15px) scale(1.03);
        box-shadow: 0 25px 50px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 50%, #ff6b9d 100%);
    }
    
    .main-header {
        text-align: center;
        color: #2E86AB;
        margin-bottom: 30px;
    }
    
    .section-header {
        color: #2E86AB;
        border-bottom: 2px solid #2E86AB;
        padding-bottom: 5px;
        margin-top: 20px;
        margin-bottom: 15px;
    }
    
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    
    .calendar-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 4px solid #2E86AB;
    }
    
    .date-info {
        font-size: 18px;
        color: #2E86AB;
        font-weight: 600;
        text-align: center;
        margin-bottom: 10px;
    }
    
    /* Style all Streamlit buttons to look like gradient cards */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #ff6b9d 100%) !important;
        border: none !important;
        border-radius: 25px !important;
        color: white !important;
        text-align: center !important;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        min-height: 200px !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2) !important;
        width: 100% !important;
        margin: 10px 0 !important;
    }
    
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        transform: translateY(-15px) scale(1.03) !important;
        box-shadow: 0 25px 50px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #764ba2 0%, #667eea 50%, #ff6b9d 100%) !important;
    }
    
    div[data-testid="stButton"] > button[kind="primary"]:active {
        transform: translateY(-8px) scale(1.01) !important;
    }
</style>
""", unsafe_allow_html=True)

class CompanyDataProcessor:
    def __init__(self, github_repo="Abdulmasood14/news", csv_directory="scraper_csv_outputs"):
        self.github_repo = github_repo
        self.csv_directory = csv_directory
        self.companies_data = {}
        self.available_dates = []
        self.load_available_dates()
    
    def load_available_dates(self):
        """Load all available dates from GitHub CSV files"""
        try:
            # GitHub API URL to get contents of the directory
            api_url = f"https://api.github.com/repos/{self.github_repo}/contents/{self.csv_directory}"
            
            response = requests.get(api_url)
            if response.status_code == 200:
                files = response.json()
                dates = []
                
                for file_info in files:
                    if file_info['name'].endswith('.csv'):
                        try:
                            date_from_file = self.extract_date_from_filename(file_info['name'])
                            if date_from_file:
                                dates.append(date_from_file)
                        except Exception as e:
                            st.error(f"Error processing {file_info['name']}: {str(e)}")
                
                self.available_dates = sorted(list(set(dates)), reverse=True)  # Most recent first
            else:
                st.error(f"Failed to access GitHub repository: {response.status_code}")
                self.available_dates = []
                
        except Exception as e:
            st.error(f"Error connecting to GitHub: {str(e)}")
            self.available_dates = []
    
    def extract_date_from_filename(self, filename):
        """Extract date from CSV filename (format: DD.MM.YYYY.csv)"""
        # Match pattern: DD.MM.YYYY.csv
        date_pattern = r'(\d{2})\.(\d{2})\.(\d{4})\.csv
    
    def load_company_data_for_date(self, selected_date):
        """Load company data for specific date from GitHub"""
        if not selected_date:
            return
        
        # Construct GitHub raw URL for the CSV file
        date_str = selected_date.strftime("%d.%m.%Y")
        csv_filename = f"{date_str}.csv"
        github_raw_url = f"https://raw.githubusercontent.com/{self.github_repo}/master/{self.csv_directory}/{csv_filename}"
        
        try:
            # Download CSV from GitHub
            response = requests.get(github_raw_url)
            if response.status_code == 200:
                # Read CSV content
                csv_content = StringIO(response.text)
                df = pd.read_csv(csv_content)
                
                # Validate columns
                required_columns = ['Company_Name', 'Extracted_Links', 'Extracted_Text']
                if not all(col in df.columns for col in required_columns):
                    st.error(f"CSV file must contain columns: {required_columns}")
                    return
                
                # Process the data
                companies_data = {}
                
                for index, row in df.iterrows():
                    company_name = str(row['Company_Name']).strip().upper()
                    
                    if company_name and company_name != 'NAN':
                        companies_data[company_name] = {
                            'company_name': company_name,
                            'extracted_links': str(row['Extracted_Links']) if pd.notna(row['Extracted_Links']) else '',
                            'extracted_text': str(row['Extracted_Text']) if pd.notna(row['Extracted_Text']) else '',
                            'file_path': github_raw_url,
                            'extraction_date': selected_date,
                            'row_number': index + 1
                        }
                
                self.companies_data = companies_data
            else:
                st.error(f"Failed to download CSV file for {date_str} from GitHub (Status: {response.status_code})")
                self.companies_data = {}
                
        except Exception as e:
            st.error(f"Error loading data for {date_str}: {str(e)}")
            self.companies_data = {}
    
    def get_companies_list(self):
        """Get list of all companies for selected date"""
        return list(self.companies_data.keys())
    
    def get_company_data(self, company_name):
        """Get data for specific company"""
        return self.companies_data.get(company_name)
    
    def get_available_dates(self):
        """Get list of available dates"""
        return self.available_dates
    
    def get_summary_stats(self):
        """Get summary statistics for current data"""
        total_companies = len(self.companies_data)
        
        total_links = 0
        total_text_length = 0
        
        for data in self.companies_data.values():
            # Count links (assuming they're separated by some delimiter)
            links_text = data.get('extracted_links', '')
            if links_text:
                # Count URLs or lines
                total_links += len([line for line in links_text.split('\n') if line.strip()])
            
            # Count text length
            text_content = data.get('extracted_text', '')
            total_text_length += len(text_content)
        
        return {
            'total_companies': total_companies,
            'total_links': total_links,
            'total_text_length': total_text_length
        }

def main():
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = None
    
    # Initialize data processor
    processor = CompanyDataProcessor()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Handle button clicks from dashboard
    if st.session_state.get('selected_company'):
        st.session_state.page = "Company Details"
    
    page = st.sidebar.selectbox("Choose a page", ["Dashboard", "Company Details"], 
                               index=0 if st.session_state.page == "Dashboard" else 1)
    
    if page == "Dashboard":
        st.session_state.page = "Dashboard"
        show_dashboard(processor)
    elif page == "Company Details":
        st.session_state.page = "Company Details"
        show_company_details(processor)

def show_dashboard(processor):
    """Display main dashboard with company cards"""
    st.markdown("<h1 class='main-header'>Company Data Scraper Dashboard</h1>", unsafe_allow_html=True)
    
    # Calendar Section
    st.markdown("<div class='calendar-section'>", unsafe_allow_html=True)
    st.markdown("### Select Date")
    
    available_dates = processor.get_available_dates()
    
    if not available_dates:
        st.warning("No CSV files found in the GitHub repository.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    # Date selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Show available dates for selection
        if available_dates:
            # Add a default "Select a date" option
            date_options = ["Select a date..."] + available_dates
            
            # Find current selection index
            if st.session_state.selected_date and st.session_state.selected_date in available_dates:
                current_index = available_dates.index(st.session_state.selected_date) + 1
            else:
                current_index = 0
            
            selected_option = st.selectbox(
                "Available dates:",
                date_options,
                index=current_index,
                format_func=lambda x: x.strftime("%d %B %Y (%A)") if x != "Select a date..." else x
            )
            
            # Update session state only if a real date is selected
            if selected_option != "Select a date...":
                st.session_state.selected_date = selected_option
            else:
                st.session_state.selected_date = None
    
    with col2:
        # Calendar picker (alternative selection)
        if available_dates:
            calendar_date = st.date_input(
                "Or pick a date:",
                value=st.session_state.selected_date if st.session_state.selected_date else available_dates[0],
                min_value=min(available_dates) if available_dates else date.today(),
                max_value=max(available_dates) if available_dates else date.today()
            )
            
            if calendar_date in available_dates:
                st.session_state.selected_date = calendar_date
            elif calendar_date not in available_dates:
                st.warning(f"No data available for {calendar_date.strftime('%d.%m.%Y')}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Load data for selected date and show company cards
    if st.session_state.selected_date:
        processor.load_company_data_for_date(st.session_state.selected_date)
        
        # Show current date info
        st.markdown(f"<div class='date-info'>Showing data for: {st.session_state.selected_date.strftime('%d %B %Y (%A)')}</div>", 
                   unsafe_allow_html=True)
        
        # Get companies data
        companies = processor.get_companies_list()
        
        if not companies:
            st.info(f"No company data found for {st.session_state.selected_date.strftime('%d.%m.%Y')}")
            return
        
        # Show only total companies metric
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.metric("Total Companies", len(companies))
        
        st.markdown("---")
        
        # Company cards
        st.markdown("<h2 class='section-header'>Company Data Cards</h2>", unsafe_allow_html=True)
        
        # Create cards in grid layout (2 columns)
        cols_per_row = 2
        for i in range(0, len(companies), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, company in enumerate(companies[i:i+cols_per_row]):
                with cols[j]:
                    # Create a button with the company name
                    if st.button(
                        company,
                        key=f"card_{company}_{i}_{j}",
                        help=f"Click to view details for {company}",
                        use_container_width=True
                    ):
                        st.session_state.selected_company = company
                        st.rerun()

def show_company_details(processor):
    """Display detailed view for selected company"""
    
    if not st.session_state.selected_date:
        st.error("Please select a date first from the Dashboard")
        if st.button("← Back to Dashboard"):
            st.session_state.page = "Dashboard"
            st.rerun()
        return
    
    # Load data for current date
    processor.load_company_data_for_date(st.session_state.selected_date)
    
    companies = processor.get_companies_list()
    if not companies:
        st.error("No company data available for selected date")
        if st.button("← Back to Dashboard"):
            st.session_state.page = "Dashboard"
            st.rerun()
        return
    
    # Company selector
    default_company = st.session_state.get('selected_company', companies[0] if companies else None)
    if default_company not in companies:
        default_company = companies[0]
    
    selected_company = st.selectbox("Select Company", companies, 
                                   index=companies.index(default_company))
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = "Dashboard"
        if 'selected_company' in st.session_state:
            del st.session_state.selected_company
        st.rerun()
    
    data = processor.get_company_data(selected_company)
    
    if not data:
        st.error(f"No data found for {selected_company}")
        return
    
    # Company header
    st.markdown(f"<h1 class='main-header'>{selected_company} - Detailed View</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='date-info'>Data from: {st.session_state.selected_date.strftime('%d %B %Y')}</div>", 
               unsafe_allow_html=True)
    
    # Summary information
    st.markdown("<h3 class='section-header'>Summary Information</h3>", unsafe_allow_html=True)
    
    # Center the single metric
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.metric("Company Name", data['company_name'])
    
    # Extracted Links Section
    st.markdown("<h3 class='section-header'>Extracted Links</h3>", unsafe_allow_html=True)
    
    links_text = data.get('extracted_links', '')
    if links_text and links_text.strip() and links_text.lower() != 'nan':
        # Split links by newlines or other separators
        links_list = [link.strip() for link in links_text.split('\n') if link.strip()]
        
        if links_list:
            st.write(f"Found {len(links_list)} links:")
            
            # Show links in expandable section
            with st.expander("View All Links", expanded=True):
                for i, link in enumerate(links_list, 1):
                    if link.startswith('http'):
                        st.markdown(f"[{link}]({link})")
                    else:
                        st.write(f"{link}")
            
            # Download links
            if st.button("Download Links as Text"):
                st.download_button(
                    label="Download Links",
                    data='\n'.join(links_list),
                    file_name=f"{selected_company}_links_{st.session_state.selected_date.strftime('%d%m%Y')}.txt",
                    mime="text/plain"
                )
        else:
            st.info("No valid links found")
    else:
        st.info("No links available for this company")
    
    # Extracted Text Content Section
    st.markdown("<h3 class='section-header'>Extracted Text Content</h3>", unsafe_allow_html=True)
    
    text_content = data.get('extracted_text', '')
    if text_content and text_content.strip() and text_content.lower() != 'nan':
        # Text search
        text_search = st.text_input("Search in text content", placeholder="Enter keyword to search...")
        
        display_text = text_content
        if text_search and text_search in text_content.lower():
            # Simple highlighting
            display_text = text_content.replace(text_search, f"**{text_search}**")
        
        # Show preview
        st.text_area("Content Preview", text_content[:500] + "..." if len(text_content) > 500 else text_content, height=100)
        
        # Full content in expandable section
        with st.expander("View Full Content", expanded=False):
            st.markdown(display_text)
        
        # Download text content
        if st.button("Download Text Content"):
            st.download_button(
                label="Download Text",
                data=text_content,
                file_name=f"{selected_company}_content_{st.session_state.selected_date.strftime('%d%m%Y')}.txt",
                mime="text/plain"
            )
    else:
        st.info("No text content available for this company")
    
    # Raw data section
    st.markdown("<h3 class='section-header'>Raw Data</h3>", unsafe_allow_html=True)
    
    if st.button("Show Raw Data"):
        st.json({
            'company_name': data['company_name'],
            'row_number': data['row_number'],
            'extraction_date': str(data['extraction_date']),
            'extracted_links': data['extracted_links'][:200] + "..." if len(data['extracted_links']) > 200 else data['extracted_links'],
            'extracted_text': data['extracted_text'][:200] + "..." if len(data['extracted_text']) > 200 else data['extracted_text']
        })

if __name__ == "__main__":
    main()
        match = re.search(date_pattern, filename)
        
        if match:
            day, month, year = match.groups()
            try:
                return date(int(year), int(month), int(day))
            except ValueError:
                return None
        
        return None
    
    def load_company_data_for_date(self, selected_date):
        """Load company data for specific date"""
        if not selected_date:
            return
        
        # Find CSV file for the selected date
        date_str = selected_date.strftime("%d.%m.%Y")
        csv_filename = f"{date_str}.csv"
        csv_path = os.path.join(self.csv_directory, csv_filename)
        
        if not os.path.exists(csv_path):
            st.error(f"No data file found for {date_str}")
            return
        
        try:
            # Read the CSV file with your actual format
            df = pd.read_csv(csv_path)
            
            # Validate columns
            required_columns = ['Company_Name', 'Extracted_Links', 'Extracted_Text']
            if not all(col in df.columns for col in required_columns):
                st.error(f"CSV file must contain columns: {required_columns}")
                return
            
            # Process the data
            companies_data = {}
            
            for index, row in df.iterrows():
                company_name = str(row['Company_Name']).strip().upper()
                
                if company_name and company_name != 'NAN':
                    companies_data[company_name] = {
                        'company_name': company_name,
                        'extracted_links': str(row['Extracted_Links']) if pd.notna(row['Extracted_Links']) else '',
                        'extracted_text': str(row['Extracted_Text']) if pd.notna(row['Extracted_Text']) else '',
                        'file_path': csv_path,
                        'extraction_date': selected_date,
                        'row_number': index + 1
                    }
            
            self.companies_data = companies_data
            
        except Exception as e:
            st.error(f"Error loading data for {date_str}: {str(e)}")
            self.companies_data = {}
    
    def get_companies_list(self):
        """Get list of all companies for selected date"""
        return list(self.companies_data.keys())
    
    def get_company_data(self, company_name):
        """Get data for specific company"""
        return self.companies_data.get(company_name)
    
    def get_available_dates(self):
        """Get list of available dates"""
        return self.available_dates
    
    def get_summary_stats(self):
        """Get summary statistics for current data"""
        total_companies = len(self.companies_data)
        
        total_links = 0
        total_text_length = 0
        
        for data in self.companies_data.values():
            # Count links (assuming they're separated by some delimiter)
            links_text = data.get('extracted_links', '')
            if links_text:
                # Count URLs or lines
                total_links += len([line for line in links_text.split('\n') if line.strip()])
            
            # Count text length
            text_content = data.get('extracted_text', '')
            total_text_length += len(text_content)
        
        return {
            'total_companies': total_companies,
            'total_links': total_links,
            'total_text_length': total_text_length
        }

def main():
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = None
    
    # Initialize data processor
    processor = CompanyDataProcessor()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Handle button clicks from dashboard
    if st.session_state.get('selected_company'):
        st.session_state.page = "Company Details"
    
    page = st.sidebar.selectbox("Choose a page", ["Dashboard", "Company Details"], 
                               index=0 if st.session_state.page == "Dashboard" else 1)
    
    if page == "Dashboard":
        st.session_state.page = "Dashboard"
        show_dashboard(processor)
    elif page == "Company Details":
        st.session_state.page = "Company Details"
        show_company_details(processor)

def show_dashboard(processor):
    """Display main dashboard with company cards"""
    st.markdown("<h1 class='main-header'>Company Data Scraper Dashboard</h1>", unsafe_allow_html=True)
    
    # Calendar Section
    st.markdown("<div class='calendar-section'>", unsafe_allow_html=True)
    st.markdown("### Select Date")
    
    available_dates = processor.get_available_dates()
    
    if not available_dates:
        st.warning("No CSV files found in the scraper_csv_outputs directory.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    # Date selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Show available dates for selection
        if available_dates:
            # Add a default "Select a date" option
            date_options = ["Select a date..."] + available_dates
            
            # Find current selection index
            if st.session_state.selected_date and st.session_state.selected_date in available_dates:
                current_index = available_dates.index(st.session_state.selected_date) + 1
            else:
                current_index = 0
            
            selected_option = st.selectbox(
                "Available dates:",
                date_options,
                index=current_index,
                format_func=lambda x: x.strftime("%d %B %Y (%A)") if x != "Select a date..." else x
            )
            
            # Update session state only if a real date is selected
            if selected_option != "Select a date...":
                st.session_state.selected_date = selected_option
            else:
                st.session_state.selected_date = None
    
    with col2:
        # Calendar picker (alternative selection)
        if available_dates:
            calendar_date = st.date_input(
                "Or pick a date:",
                value=st.session_state.selected_date if st.session_state.selected_date else available_dates[0],
                min_value=min(available_dates) if available_dates else date.today(),
                max_value=max(available_dates) if available_dates else date.today()
            )
            
            if calendar_date in available_dates:
                st.session_state.selected_date = calendar_date
            elif calendar_date not in available_dates:
                st.warning(f"No data available for {calendar_date.strftime('%d.%m.%Y')}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Load data for selected date and show company cards
    if st.session_state.selected_date:
        processor.load_company_data_for_date(st.session_state.selected_date)
        
        # Show current date info
        st.markdown(f"<div class='date-info'>Showing data for: {st.session_state.selected_date.strftime('%d %B %Y (%A)')}</div>", 
                   unsafe_allow_html=True)
        
        # Get companies data
        companies = processor.get_companies_list()
        
        if not companies:
            st.info(f"No company data found for {st.session_state.selected_date.strftime('%d.%m.%Y')}")
            return
        
        # Show only total companies metric
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.metric("Total Companies", len(companies))
        
        st.markdown("---")
        
        # Company cards
        st.markdown("<h2 class='section-header'>Company Data Cards</h2>", unsafe_allow_html=True)
        
        # Create cards in grid layout (2 columns)
        cols_per_row = 2
        for i in range(0, len(companies), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, company in enumerate(companies[i:i+cols_per_row]):
                with cols[j]:
                    # Create a button with the company name
                    if st.button(
                        company,
                        key=f"card_{company}_{i}_{j}",
                        help=f"Click to view details for {company}",
                        use_container_width=True
                    ):
                        st.session_state.selected_company = company
                        st.rerun()

def show_company_details(processor):
    """Display detailed view for selected company"""
    
    if not st.session_state.selected_date:
        st.error("Please select a date first from the Dashboard")
        if st.button("← Back to Dashboard"):
            st.session_state.page = "Dashboard"
            st.rerun()
        return
    
    # Load data for current date
    processor.load_company_data_for_date(st.session_state.selected_date)
    
    companies = processor.get_companies_list()
    if not companies:
        st.error("No company data available for selected date")
        if st.button("← Back to Dashboard"):
            st.session_state.page = "Dashboard"
            st.rerun()
        return
    
    # Company selector
    default_company = st.session_state.get('selected_company', companies[0] if companies else None)
    if default_company not in companies:
        default_company = companies[0]
    
    selected_company = st.selectbox("Select Company", companies, 
                                   index=companies.index(default_company))
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = "Dashboard"
        if 'selected_company' in st.session_state:
            del st.session_state.selected_company
        st.rerun()
    
    data = processor.get_company_data(selected_company)
    
    if not data:
        st.error(f"No data found for {selected_company}")
        return
    
    # Company header
    st.markdown(f"<h1 class='main-header'>{selected_company} - Detailed View</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='date-info'>Data from: {st.session_state.selected_date.strftime('%d %B %Y')}</div>", 
               unsafe_allow_html=True)
    
    # Summary information
    st.markdown("<h3 class='section-header'>Summary Information</h3>", unsafe_allow_html=True)
    
    # Center the single metric
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.metric("Company Name", data['company_name'])
    
    # Extracted Links Section
    st.markdown("<h3 class='section-header'>Extracted Links</h3>", unsafe_allow_html=True)
    
    links_text = data.get('extracted_links', '')
    if links_text and links_text.strip() and links_text.lower() != 'nan':
        # Split links by newlines or other separators
        links_list = [link.strip() for link in links_text.split('\n') if link.strip()]
        
        if links_list:
            st.write(f"Found {len(links_list)} links:")
            
            # Show links in expandable section
            with st.expander("View All Links", expanded=True):
                for i, link in enumerate(links_list, 1):
                    if link.startswith('http'):
                        st.markdown(f"[{link}]({link})")
                    else:
                        st.write(f"{link}")
            
            # Download links
            if st.button("Download Links as Text"):
                st.download_button(
                    label="Download Links",
                    data='\n'.join(links_list),
                    file_name=f"{selected_company}_links_{st.session_state.selected_date.strftime('%d%m%Y')}.txt",
                    mime="text/plain"
                )
        else:
            st.info("No valid links found")
    else:
        st.info("No links available for this company")
    
    # Extracted Text Content Section
    st.markdown("<h3 class='section-header'>Extracted Text Content</h3>", unsafe_allow_html=True)
    
    text_content = data.get('extracted_text', '')
    if text_content and text_content.strip() and text_content.lower() != 'nan':
        # Text search
        text_search = st.text_input("Search in text content", placeholder="Enter keyword to search...")
        
        display_text = text_content
        if text_search and text_search in text_content.lower():
            # Simple highlighting
            display_text = text_content.replace(text_search, f"**{text_search}**")
        
        # Show preview
        st.text_area("Content Preview", text_content[:500] + "..." if len(text_content) > 500 else text_content, height=100)
        
        # Full content in expandable section
        with st.expander("View Full Content", expanded=False):
            st.markdown(display_text)
        
        # Download text content
        if st.button("Download Text Content"):
            st.download_button(
                label="Download Text",
                data=text_content,
                file_name=f"{selected_company}_content_{st.session_state.selected_date.strftime('%d%m%Y')}.txt",
                mime="text/plain"
            )
    else:
        st.info("No text content available for this company")
    
    # Raw data section
    st.markdown("<h3 class='section-header'>Raw Data</h3>", unsafe_allow_html=True)
    
    if st.button("Show Raw Data"):
        st.json({
            'company_name': data['company_name'],
            'row_number': data['row_number'],
            'extraction_date': str(data['extraction_date']),
            'extracted_links': data['extracted_links'][:200] + "..." if len(data['extracted_links']) > 200 else data['extracted_links'],
            'extracted_text': data['extracted_text'][:200] + "..." if len(data['extracted_text']) > 200 else data['extracted_text']
        })

if __name__ == "__main__":
    main()
