import requests
from bs4 import BeautifulSoup
import re
import zipfile
import os
import pandas as pd
import mysql.connector
# from tkinter import Tk, Label, Button, StringVar, Entry, messagebox
from datetime import datetime, timedelta
from database_cloud import store_data_in_mysql
import sys
from google.cloud import storage
from io import BytesIO


# Adding user agent - GeeksforGeeks and GPT ALSO
# Otherwise we get error
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
def download_bhavcopy_zip(url,flag):
    # Make a request to the BSE website
    if flag==0: # only in 2nd case
        response = requests.get(url, headers=headers)

    if flag==1 or response.status_code == 200:
        # We have the content of page in HTML - response.txt/ response.content
        # Parse the HTML content of the page
        if flag==0:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find the download link for the ZIP file
            # a searches for anchor tag- Get latest ZIP file
            zip_link = soup.find('a', href=re.compile(r'BhavCopy/Equity/\w+_CSV\.ZIP', re.IGNORECASE))

        if flag==1 or zip_link:
            # Extract the download link
            if flag==0:
                download_url = zip_link['href']
            else:
                download_url=url
            print(download_url)
            # Extract date using regular expression
            match = re.search(r'EQ(\d{2})(\d{2})(\d{2})', download_url)
            if match:
                day, month, year = match.groups()
                date_string = f"{day}{month}{year}"
                print(f"Extracted Date: {date_string}")
            else:
                print("Date not found in the URL.")

           
            # Download the ZIP file
            # Again user agent to avoid error
            response_zip = requests.get(download_url,headers=headers)

            if response_zip.status_code == 200:
                # Save the ZIP file to Cloud Storage
                client = storage.Client()

                # Specify your Cloud Storage bucket name
                bucket_name = 'model-factor-412306.appspot.com'
              
                # Specify the Cloud Storage object name (file path within the bucket)
                object_name = f'Equity_Bhaavcopy.zip'

                # Extract the ZIP file contents using pandas
                # Get the CSV file name dynamically
                with BytesIO(response_zip.content) as zip_content:
                    with zipfile.ZipFile(zip_content) as zip_ref:
                        csv_file_name = next(name for name in zip_ref.namelist() if name.lower().endswith('.csv'))
                        csv_content = zip_ref.read(csv_file_name)

                # Read the CSV content using pandas
                data = pd.read_csv(BytesIO(csv_content))

                print('CSV file read successfully:', data.head())

                # with open('Equity_Bhaavcopy.zip', 'wb') as zip_file:
                #     zip_file.write(response_zip.content)
                # print('Equity Bhavcopy ZIP downloaded successfully.')

                # # zipfile library is used to create/ append/ read/ write
                # # Create path for data extracted from ZIP File
                # extract_path = 'extractedData'
                # with zipfile.ZipFile('Equity_Bhaavcopy.zip') as zip_ref:
                #     zip_ref.extractall(extract_path)

                # print('ZIP file contents extracted successfully.')

                # # Read the CSV file using pandas
                # # File name kaha se aayega ? 
                
                # # ALL FILES -> GET CSV FILE NAME FROM THHERE
                # # extracted_files = os.listdir(extract_path)
                # # # Find the CSV file dynamically (assuming there is only one CSV file)
                # # csv_file_name = next(file for file in extracted_files if file.lower().endswith('.csv'))
                # # print(csv_file_name)
                # csv_file_name = f'EQ{date_string}.CSV'
                # csv_file_path = os.path.join(extract_path, csv_file_name)

                # # Read the CSV file using pandas
                # data = pd.read_csv(csv_file_path)

                # print('CSV file read successfully:', data.head())
                # # Store data in MySQL
                store_data_in_mysql(data, 'Stocks', 'stocks',date_string)  
            else:
                print('Failed to download ZIP file. Please check date and ensure it is not a holiday for Stock Market')
        else:
            print('ZIP file link not found on the page.')
    else:
        print('Failed to fetch the pagefff.')




# URL of the BSE Bhavcopy page
# bse_url = "https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx"

# Call the function to download the ZIP file
# download_bhavcopy_zip(bse_url)
        
# REPLACED ABOVE STUFF
def fetch_latest_data():
    bse_url = "https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx"
    download_bhavcopy_zip(bse_url,0)

def fetch_data_for_date_range(start_date, end_date):
    # Convert string representations to datetime.date objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    current_date = start_date
    while current_date <= end_date:
        # Format the current date as 'ddmmyy'
        date_string = current_date.strftime('%d%m%y')

        # Construct the URL for the current date
        url = f"https://www.bseindia.com/download/BhavCopy/Equity/EQ{date_string}_CSV.ZIP"
        print(url,1)
        # Call the function to download and extract the ZIP file
        download_bhavcopy_zip(url,1)

        # Move to the next date
        current_date += timedelta(days=1)

# def get_date_range_from_user():
#     root = Tk()
#     root.title("Date Range Selector")

#     start_label = Label(root, text="Enter start date (dd-mm-yyyy):")
#     start_label.pack()

#     start_var = StringVar()
#     start_entry = Entry(root, textvariable=start_var)
#     start_entry.pack()

#     end_label = Label(root, text="Enter end date (dd-mm-yyyy):")
#     end_label.pack()

#     end_var = StringVar()
#     end_entry = Entry(root, textvariable=end_var)
#     end_entry.pack()

#     def get_date_range():
#         try:
#             start_date = datetime.strptime(start_var.get(), '%d-%m-%Y').date()
#             end_date = datetime.strptime(end_var.get(), '%d-%m-%Y').date()

#             if start_date > end_date:
#                 messagebox.showerror("Error", "Start date cannot be greater than end date.")
#             else:
#                 root.destroy()
#                 fetch_data_for_date_range(start_date, end_date)
#         except ValueError:
#             messagebox.showerror("Error", "Invalid date format. Please use dd-mm-yyyy.")

#     submit_button = Button(root, text="Submit", command=get_date_range)
#     submit_button.pack()

#     root.mainloop()


if __name__ == "__main__":
    print("Choose an option:")
    print("1. Fetch latest data")
    print("2. Fetch data for a date range")
    fetch_latest_data()
    # fetch_data_for_date_range('2024-01-14','2024-01-24')
    # if len(sys.argv) < 2:
    #     print("Please provide a choice (1 or 2) as a command-line argument.")
    # else:
    #     choice = sys.argv[1]
    #     if choice == "1":
    #         fetch_latest_data()
    #     elif choice == "2":
    #         get_date_range_from_user()
    #     else:
    #         print("Invalid choice. Please enter 1 or 2.")
    # choice = input("Enter your choice (1 or 2): ")
    # if choice == "1":
        # fetch_latest_data()
    # elif choice == "2":
        # get_date_range_from_user()
    # else:
        # print("Invalid choice. Please enter 1 or 2.")





