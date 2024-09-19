from datetime import datetime, timedelta
import os
from io import StringIO
from io import BytesIO
from PIL import Image
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import requests
import fitz  # PyMuPDF
import matplotlib
import traceback
# import logging
matplotlib.use('Agg')

# logging.basicConfig(level=logging.DEBUG)


def Main():
    try:
        # ***********************************************************************************************************************************
        yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

        ids = ['A16', 'A17']
        # logging.debug("Fetching data...")

        def fetch_and_display_image(station_id, date):
            url = f'https://dms.gfe.co.th/api/acc-api/trigger/summary-chart?station={station_id}&dam=LTKNMA&date={date}'
            headers = {
                'Referer': 'https://dms.gfe.co.th/LTKNMA/accelerometer',
                'X-XSRF-TOKEN': xsrf_token,
                'X-CSRF-TOKEN': csrf_token
            }

            response = session.get(url, headers=headers, cookies=cookies)

            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))

                # Get current directory where the script is running
                current_directory = os.path.dirname(os.path.abspath(__file__))
                file_name = f'{station_id}_Summary.png'
                file_path = os.path.join(current_directory, file_name)

                image.save(file_path)
                print(f"Saved: {file_path}")
            else:
                print(
                    f"Request for station {station_id} on {date} failed with status code {response.status_code}")

        # Initial request to get cookies and tokens
        login_url = 'https://dms.gfe.co.th/login'
        session = requests.Session()
        response = session.get(login_url)

        if response.status_code == 200:
            cookies = session.cookies
            xsrf_token = cookies.get('XSRF-TOKEN')
            csrf_token = response.text.split(
                'name="csrf-token" content="')[1].split('"')[0]

            # Loop through each ID and fetch the image
            for station_id in ids:
                fetch_and_display_image(station_id, yesterday)
        else:
            print(
                f"Initial request failed with status code {response.status_code}")
        # *****************************************************************************************************************************************
        # Depth of IPI for each inclinometer (Y-axis values)
        ipi_depths = {
            'INC1': [281.6, 278.1, 274.6, 271.1, 267.6, 264.1, 260.6, 257.1, 253.6],
            'INC2': [278.68, 275.18, 271.68, 268.18, 264.68, 261.18, 257.68, 254.18],
            'INC3': [281.54, 278.04, 274.54, 271.04, 267.54, 264.04, 260.54, 257.04, 253.54, 250.04, 246.54, 243.04, 239.54],
            'INC4': [278.35, 274.85, 271.35, 267.85, 264.35, 260.85, 257.35, 253.85, 250.35, 246.85, 243.35]
        }

        a_axis_urls = {
            'INC1': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=965156829&single=true&output=csv",
            'INC2': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=859019977&single=true&output=csv",
            'INC3': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=1435986749&single=true&output=csv",
            'INC4': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=610512643&single=true&output=csv",
        }

        b_axis_urls = {
            'INC1': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=1234181341&single=true&output=csv",
            'INC2': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=784108133&single=true&output=csv",
            'INC3': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=265982342&single=true&output=csv",
            'INC4': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=1596038973&single=true&output=csv",
        }

        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Function to fetch and prepare data

        def fetch_data(url):
            response = requests.get(url)
            if response.status_code == 200:
                data = pd.read_csv(StringIO(response.text))
                return data
            else:
                print(f"Failed to fetch data from {url}")
                return pd.DataFrame()

        # Process each inclinometer (INC)
        for inc in ['INC1', 'INC2', 'INC3', 'INC4']:
            a_axis_data = fetch_data(a_axis_urls[inc])
            b_axis_data = fetch_data(b_axis_urls[inc])

            # Use 'Row ID' as the index
            a_axis_data.set_index('Row ID', inplace=True)
            b_axis_data.set_index('Row ID', inplace=True)

            ipi_depth = ipi_depths[inc]
            last_depth_adjusted = ipi_depth[-1] - 3.5
            # Adjusted size for better layout
            fig = plt.figure(figsize=(20, 12))
            # Two rows for charts, one small for heading, one for table
            gs = fig.add_gridspec(3, 2, height_ratios=[2, 0.1, 0.5])
            yesterday = pd.Timestamp.now() - pd.DateOffset(days=1)
            yesterday_str = yesterday.strftime('%d/%m/%Y')

            # Plot A-Axis vs Depth of IPI (Left chart)
            ax1 = fig.add_subplot(gs[0, 0])
            for date in a_axis_data.columns:
                # Plot data and extend the line to the additional point
                extended_a_axis_values = list(
                    a_axis_data[date].dropna().values) + [0]
                extended_depth = ipi_depth[:len(
                    a_axis_data[date].dropna())] + [last_depth_adjusted]

                if date == yesterday_str:
                    ax1.plot(extended_a_axis_values, extended_depth, marker='o',
                             linestyle='--', color='blue', label=f'A-Axis {date}')
                else:
                    ax1.plot(extended_a_axis_values, extended_depth,
                             marker='o', label=f'A-Axis {date}')

            ax1.set_title(f'Deformation ,A-Axis ({inc})')
            ax1.set_xlabel('Displacement (mm)')
            ax1.set_ylabel('Sensors level (MSL)')
            ax1.legend(loc='upper right')
            ax1.grid(True, linestyle='--', alpha=0.6)

            # Plot B-Axis vs Depth of IPI (Right chart)
            ax2 = fig.add_subplot(gs[0, 1])
            for date in b_axis_data.columns:
                # Plot data and extend the line to the additional point
                extended_b_axis_values = list(
                    b_axis_data[date].dropna().values) + [0]
                extended_depth = ipi_depth[:len(
                    b_axis_data[date].dropna())] + [last_depth_adjusted]

                # Check if the date is yesterday and set style
                if date == yesterday_str:
                    ax2.plot(extended_b_axis_values, extended_depth, marker='o',
                             linestyle='--', color='blue', label=f'B-Axis {date}')
                else:
                    ax2.plot(extended_b_axis_values, extended_depth,
                             marker='o', linestyle='--', label=f'B-Axis {date}')

            ax2.set_title(f'Deformation ,B-Axis ({inc})')
            ax2.set_xlabel('Displacement (mm)')
            ax2.set_ylabel('Sensors level (MSL)')
            ax2.legend(loc='upper right')
            ax2.grid(True, linestyle='--', alpha=0.6)

            # Set x-axis limits to -100 and +100
            ax1.set_xlim([-100, 100])
            ax2.set_xlim([-100, 100])

            # # Add heading text for the table
            # ax_heading = fig.add_subplot(gs[1, :])
            # ax_heading.text(0.5, 0.5, f"Deformation for {yesterday_str}", horizontalalignment='center', verticalalignment='center', fontsize=12)
            # ax_heading.axis('off')  # Turn off axis for the heading

            # Add the table for yesterday's data below the heading
            ax_table = fig.add_subplot(gs[2, :])
            ax_table.axis('off')  # Turn off axis for the table

            # Prepare the data for the table
            a_axis_yesterday_values = list(
                a_axis_data[yesterday_str].dropna().values)
            b_axis_yesterday_values = list(
                b_axis_data[yesterday_str].dropna().values)

            # Create table data
            table_data = [[f'A-Axis (mm)\n{yesterday_str}', *a_axis_yesterday_values], [
                f'B-Axis (mm)\n{yesterday_str}', *b_axis_yesterday_values]]
            # Header labels as IPI names
            col_labels = ['IPI'] + \
                [f'IPI{i+1}' for i in range(len(a_axis_yesterday_values))]

            # Add table to the plot
            ax_table.table(cellText=table_data, colLabels=col_labels,
                           loc='center', cellLoc='center', bbox=[0.0, 0.2, 1.0, 1.0])

            plot_file = os.path.join(script_dir, f'{inc}.jpeg')
            print(f"{plot_file}")
            plt.savefig(plot_file, format='jpeg', bbox_inches='tight')

            plt.close()

        # *****************************************************************************************************************************************
        # URLs for A-Axis and B-Axis data for multiple INCs
        a_axis_urls = {
            'INC1': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=2107676910&single=true&output=csv",
            'INC2': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=971655478&single=true&output=csv",
            'INC3': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=734807517&single=true&output=csv",
            'INC4': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=1704339513&single=true&output=csv",
        }

        b_axis_urls = {
            'INC1': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=1459331572&single=true&output=csv",
            'INC2': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=55604534&single=true&output=csv",
            'INC3': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=1031578350&single=true&output=csv",
            'INC4': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=267894099&single=true&output=csv",
        }

        # Get the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Function to fetch and prepare data

        def fetch_data(url):
            response = requests.get(url)
            if response.status_code == 200:
                data = pd.read_csv(StringIO(response.text))
                data = data.melt(id_vars='Row ID',
                                 var_name='Date', value_name='Value')
                data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%Y')
                return data
            else:
                print(f"Failed to fetch data from {url}")
                return pd.DataFrame()

        # Process each INC
        for inc in ['INC1', 'INC2', 'INC3', 'INC4']:
            a_axis_data = fetch_data(a_axis_urls[inc])
            b_axis_data = fetch_data(b_axis_urls[inc])

            # Get yesterday's date
            yesterday = pd.Timestamp.now() - pd.DateOffset(days=1)

            # Filter data for yesterday
            a_axis_yesterday = a_axis_data[a_axis_data['Date'].dt.date == yesterday.date(
            )]
            b_axis_yesterday = b_axis_data[b_axis_data['Date'].dt.date == yesterday.date(
            )]

            # Pivot tables to make it easier to plot
            a_axis_pivot = a_axis_yesterday.pivot(
                index='Row ID', columns='Date', values='Value')
            b_axis_pivot = b_axis_yesterday.pivot(
                index='Row ID', columns='Date', values='Value')

            # Combine A-Axis and B-Axis data for the table/*****************************************************************************************************************************
            combined_yesterday = pd.concat(
                [a_axis_pivot, b_axis_pivot], axis=1, keys=['A-Axis', 'B-Axis'])
            combined_yesterday.fillna('No Data', inplace=True)

            # Flatten the column MultiIndex and rename the columns
            combined_yesterday.columns = [
                f'{col[0]}\n{col[1].strftime("%d/%m/%Y")}' for col in combined_yesterday.columns]
            combined_yesterday.reset_index(inplace=True)

            # Generate dynamic labels for the table header as 'IPI' + IPI names
            col_labels = ['IPI'] + \
                [f'IPI{i+1}' for i in range(len(a_axis_pivot.index))]

            # Transpose the table
            combined_yesterday = combined_yesterday.T
            combined_yesterday.columns = combined_yesterday.iloc[0]
            combined_yesterday = combined_yesterday[1:]
            combined_yesterday.reset_index(inplace=True)
            combined_yesterday.rename(
                columns={'index': 'Axis', 'IPI number': 'IPI number'}, inplace=True)

            # Set the column labels dynamically to match 'IPI' naming convention
            combined_yesterday.columns = col_labels

            # Plotting
            # Adjusted size for better layout
            fig = plt.figure(figsize=(18, 8))

            # Create a grid layout with specific height ratios
            gs = fig.add_gridspec(2, 2, height_ratios=[1, 0.3], width_ratios=[
                1, 1])  # Adjust height ratios for table

            # Plot A-Axis
            ax1 = fig.add_subplot(gs[0, 0])
            for row_id, group in a_axis_data.groupby('Row ID'):
                ax1.plot(group['Date'], group['Value'],
                         marker='o', label=row_id)
            ax1.set_title(f'A-Axis ({inc})')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('% Shear Strain')
            ax1.legend(loc='center left', bbox_to_anchor=(
                0.985, 0.5), frameon=False)
            ax1.grid(True, linestyle='--', alpha=0.6)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
            ax1.xaxis.set_major_locator(mdates.DayLocator())
            plt.xticks(rotation=45)

            # Plot B-Axis
            ax2 = fig.add_subplot(gs[0, 1])
            for row_id, group in b_axis_data.groupby('Row ID'):
                ax2.plot(group['Date'], group['Value'],
                         marker='o', label=row_id)
            ax2.set_title(f'B-Axis {inc})')
            ax2.set_xlabel('Date')
            ax2.legend(loc='center left', bbox_to_anchor=(
                0.985, 0.5), frameon=False)
            ax2.grid(True, linestyle='--', alpha=0.6)
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
            ax2.xaxis.set_major_locator(mdates.DayLocator())
            plt.xticks(rotation=45)

            ax_table = fig.add_subplot(gs[1, :])
            ax_table.axis('off')
            table_data = combined_yesterday
            ax_table.table(cellText=table_data.values, colLabels=table_data.columns,
                           loc='center', cellLoc='center', bbox=[0.0, -0.4, 1.0, 1.0])

            combined_plot_file = os.path.join(script_dir, f'Shear-{inc}.jpeg')
            print(f"{combined_plot_file}")
            plt.savefig(combined_plot_file, format='jpeg',
                        bbox_inches='tight')
            plt.close()  # Close the plot to free up memory

        # *****************************************************************************************************************************************
        # Define a list of dictionaries containing URLs, columns to plot, plot titles, and image names
        data_sources = [
            {
                'url': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=0&single=true&output=csv",
                'columns_to_plot': ['P.1-1', 'P.1-2', 'P.1-3', 'P.1-4', 'P.1-5', 'PO.10', 'PO.11', 'PO.12', 'PO.13', 'PO.14', 'PO.15', 'PO.16', 'WL2'],
                'title': 'Piezometer 0+125 vs Date/Time',
                'image_name': 'Piezo0+125.jpeg'
            },
            {
                'url': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=0&single=true&output=csv",
                'columns_to_plot': ['P.2-1', 'P.2-2', 'P.2-3', 'P.2-4', 'P.2-5', 'PO.1', 'PO.2', 'PO.3', 'PO.4', 'PO.5', 'PO.6', 'PO.7', 'PO.8', 'WL2'],
                'title': 'Piezometer 0+190 vs Date/Time',
                'image_name': 'Piezo0+190.jpeg'
            },
            {
                'url': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=0&single=true&output=csv",
                'columns_to_plot': ['P.3-1', 'P.3-2', 'P.3-3', 'P.3-4', 'P.3-5', 'PO.17', 'PO.18', 'PO.19', 'PO.20', 'PO.21', 'PO.22', 'PO.23', 'PO.24', 'WL2'],
                'title': 'Piezometer 0+250 vs Date/Time',
                'image_name': 'Piezo0+250.jpeg'
            },
            {
                'url': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=559499939&single=true&output=csv",
                'columns_to_plot': ['OW1', 'OW2', 'OW3', 'OW4', 'OW5', 'WL2'],
                'title': 'Observation Well(OW) vs Date/Time',
                'image_name': 'OW.jpeg'
            },
            {
                'url': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=942459285&single=true&output=csv",
                'columns_to_plot': ['OSP_PE1', 'OSP_PF1', 'WL2'],
                'title': 'Open end standpipe piezometer(OSP.1 PF,PE) vs Date/Time',
                'image_name': 'OSP1.jpeg'
            },
            {
                'url': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=510301664&single=true&output=csv",
                'columns_to_plot': ['OSP_PE2', 'OSP_PF2', 'WL2'],
                'title': 'Open end standpipe piezometer(OSP.2 PF,PE) vs Date/Time',
                'image_name': 'OSP2.jpeg'
            },
            {
                'url': "https://docs.google.com/spreadsheets/d/e/2PACX-1vQsYQCr3A0LYqtHqMYMT8XbWNyYMLPUjvnR5FBBKoc-oy45-FNZcKgQJaR4lfb77M9tS53HfpQkagDZ/pub?gid=1309255923&single=true&output=csv",
                'columns_to_plot': ['OSP_PE3', 'OSP_PF3', 'WL2'],
                'title': 'Open end standpipe piezometer(OSP.3 PF,PE) vs Date/Time',
                'image_name': 'OSP3.jpeg'
            },
        ]

        # Get the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Loop through each data source
        for source in data_sources:
            url = source['url']
            columns_to_plot = source['columns_to_plot']
            plot_title = source['title']
            image_name = source['image_name']

            # Send a GET request to the URL
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                # Read the CSV data into a DataFrame
                data = pd.read_csv(StringIO(response.text))

                # Replace 'No Pressure' with NaN (pd.NA)
                data.replace('No Pressure', pd.NA, inplace=True)

                # Convert Timestamp to datetime
                data['Timestamp'] = pd.to_datetime(
                    data['Timestamp'], format='%d/%m/%Y %H:%M:%S')

                # Get yesterday's data
                yesterday = pd.Timestamp.now() - pd.DateOffset(days=1)
                yesterday_data = data[data['Timestamp'].dt.date ==
                                      yesterday.date()]

                # Check if all values for yesterday are 'No Pressure'
                all_no_pressure = (
                    yesterday_data[columns_to_plot].isna().all()).all()

                # Filter numeric columns that exist in the data
                numeric_columns = [
                    col for col in columns_to_plot if col in data.columns and pd.api.types.is_numeric_dtype(data[col])]

                # Create the plot
                # Increased height to fit the table and heading
                plt.figure(figsize=(12, 12))

                # Plot each numeric column
                for column in numeric_columns:
                    if column == 'WL2':
                        # Set WL2 to have a blue dashed line
                        plt.plot(data['Timestamp'], data[column],
                                 linestyle='--', color='blue', label=column)
                    else:
                        # Default style for other columns
                        plt.plot(data['Timestamp'], data[column],
                                 linestyle='-', label=column)

                # Set plot title, labels, and formatting
                plt.title(plot_title)
                plt.xlabel(' ')
                plt.ylabel('Piezometric Head (MSL)')
                plt.xticks(rotation=45)

                # Set date format on x-axis
                ax = plt.gca()
                ax.xaxis.set_major_formatter(
                    mdates.DateFormatter('%d/%m/%y %H:%M'))
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())

                # Add major and minor grids for both x and y axes
                plt.grid(True, which='major', linestyle='-',
                         linewidth=0.75, color='gray', alpha=0.5)
                ax.grid(True, which='minor', linestyle=':',
                        linewidth=0.5, color='lightgray', alpha=0.4)

                # Enable minor ticks for both axes
                ax.minorticks_on()

                # Set legend to one column on the right-hand side
                ncol = 1  # Single column for the legend
                plt.legend(loc='center left', bbox_to_anchor=(
                    1.0, 0.5), ncol=ncol, frameon=False)

                # Add a text box with the latest values on the chart
                latest_data = data.iloc[-1]
                latest_timestamp = latest_data['Timestamp'].strftime(
                    '%d/%m/%Y %H:%M:%S')
                yesterday_date = latest_data['Timestamp'].strftime('%d/%m/%Y')
                # Check if the columns contain 'PO.7', 'PO.9', or 'PO.15' and set to 'Damaged'
                textstr = f'{latest_timestamp}\n'
                for col in columns_to_plot:
                    if col in ['PO.7', 'PO.9', 'PO.15']:
                        textstr += f'{col}: Damaged\n'
                    elif col in latest_data:
                        textstr += f'{col}: {latest_data[col] if pd.notna(latest_data[col]) else "No Pressure"}\n'

                plt.gca().text(0.02, 0.95, textstr, transform=plt.gca().transAxes, fontsize=10, ha='left', va='top',
                               bbox=dict(facecolor='white', edgecolor='black', alpha=0.5, boxstyle='round,pad=0.5'))

                # Add a heading and table below the chart
                if all_no_pressure:
                    heading = "Data of Yesterday: All 'No Pressure'"
                    table_data = pd.DataFrame(
                        index=[0], columns=columns_to_plot)
                    table_data.loc[0] = ['No Pressure'] * len(columns_to_plot)
                else:
                    heading = f"Maximum Results for {yesterday_date}"
                    max_data_yesterday = yesterday_data[columns_to_plot].max()
                    table_data = max_data_yesterday.fillna(
                        'No Pressure').to_frame().T

                    # Set 'Damaged' for specific headers
                    for col in ['PO.7', 'PO.9', 'PO.15']:
                        if col in table_data.columns:
                            table_data[col] = 'Damaged'

                # Adjust layout to fit heading and table
                # Adjust layout to fit heading and table
                plt.tight_layout(rect=[0, 0.4, 1, 0.85])

                # Plot the heading
                plt.figtext(0.5, 0.4, heading, ha='center', va='center',
                            fontsize=10, transform=plt.gcf().transFigure)

                # Add the table below the chart
                # Adjust inset_axes to fit the table
                ax_table = plt.gca().inset_axes([0, -0.6, 1, 0.3])
                ax_table.axis('off')
                ax_table.table(cellText=table_data.values, colLabels=table_data.columns,
                               loc='center', cellLoc='center', bbox=[0.0, 0.0, 1.0, 0.7])

                # Save the combined plot as a JPEG file
                plot_file = os.path.join(script_dir, image_name)
                plt.savefig(plot_file, format='jpeg',
                            bbox_inches='tight', pad_inches=0.1)
                print(f"Saved {image_name}")
                plt.close()

            else:
                print(f"Failed to fetch data from {url}")

        # *****************************************************************************************************************************************

        def add_images_and_text_to_pdf():
            try:
                SRCDIR = os.path.dirname(os.path.abspath(__file__))
                print("SRCDIR", SRCDIR)
                pdf_template_path = os.path.join(
                    SRCDIR, "Template-without-chart.pdf")
                # Generate a dynamic file name based on timestamp
                images = [
                    {
                        'path': os.path.join(SRCDIR, "Piezo0+125.jpeg"),
                        'page': 0,
                        'position': (50, 490),
                        'scale': 0.42
                    },
                    {
                        'path': os.path.join(SRCDIR, "Piezo0+190.jpeg"),
                        'page': 1,
                        'position': (50, 220),
                        'scale': 0.42
                    },
                    {
                        'path': os.path.join(SRCDIR, "Piezo0+250.jpeg"),
                        'page': 2,
                        'position': (50, 220),
                        'scale': 0.42
                    },
                    {
                        'path': os.path.join(SRCDIR, "OSP1.jpeg"),
                        'page': 3,
                        'position': (50, 220),
                        'scale': 0.42
                    },
                    {
                        'path': os.path.join(SRCDIR, "OSP2.jpeg"),
                        'page': 4,
                        'position': (50, 220),
                        'scale': 0.42
                    },
                    {
                        'path': os.path.join(SRCDIR, "OSP3.jpeg"),
                        'page': 5,
                        'position': (50, 220),
                        'scale': 0.42
                    },
                    {
                        'path': os.path.join(SRCDIR, "INC1.jpeg"),
                        'page': 6,
                        'position': (50, 220),
                        'scale': 0.34
                    },
                    {
                        'path': os.path.join(SRCDIR, "Shear-INC1.jpeg"),
                        'page': 6,
                        'position': (40, 500),
                        'scale': 0.33
                    },
                    {
                        'path': os.path.join(SRCDIR, "INC2.jpeg"),
                        'page': 7,
                        'position': (50, 220),
                        'scale': 0.34
                    },
                    {
                        'path': os.path.join(SRCDIR, "Shear-INC2.jpeg"),
                        'page': 7,
                        'position': (40, 500),
                        'scale': 0.33
                    },
                    {
                        'path': os.path.join(SRCDIR, "INC3.jpeg"),
                        'page': 8,
                        'position': (50, 220),
                        'scale': 0.34
                    },
                    {
                        'path': os.path.join(SRCDIR, "Shear-INC3.jpeg"),
                        'page': 8,
                        'position': (40, 500),
                        'scale': 0.33
                    },
                    {
                        'path': os.path.join(SRCDIR, "INC4.jpeg"),
                        'page': 9,
                        'position': (50, 220),
                        'scale': 0.34
                    },
                    {
                        'path': os.path.join(SRCDIR, "Shear-INC4.jpeg"),
                        'page': 9,
                        'position': (40, 500),
                        'scale': 0.33
                    },
                    {
                        'path': os.path.join(SRCDIR, "OW.jpeg"),
                        'page': 10,
                        'position': (50, 400),
                        'scale': 0.42
                    },
                    {
                        'path': os.path.join(SRCDIR, "A16_Summary.PNG"),
                        'page': 11,
                        'position': (50, 105),
                        'scale': 0.45
                    },
                    {
                        'path': os.path.join(SRCDIR, "A17_Summary.PNG"),
                        'page': 11,
                        'position': (50, 435),
                        'scale': 0.45
                    }
                ]
                file_name = f"LTKNMA-Report-{(datetime.now() - timedelta(1)).strftime('%d-%m-%Y')}-{(datetime.now() - timedelta(1)).strftime('%H-%M-%S')}.pdf"
                output_pdf_path = os.path.join(
                    SRCDIR, file_name)
                # Open the PDF template
                pdf_document = fitz.open(pdf_template_path)

                # Calculate yesterday's date
                yesterday = datetime.now() - timedelta(1)
                date_text = yesterday.strftime("%d/%m/%Y")

                # Define font path (adjust path to your font file)
                # font_path = os.path.join(os.path.dirname(__file__), "Noto Sans Thai Regular.ttf")
                # if not os.path.exists(font_path):
                #     raise FileNotFoundError(f"Font file not found: {font_path}")

                # Add text to all pages
                for page_num in range(len(pdf_document)):
                    page = pdf_document.load_page(page_num)

                    # Define text to add
                    text = f"Dam monitoring report {date_text}"

                    # Define text positioning
                    # Adjust to fit text size and position
                    text_position = fitz.Point(page.rect.width - 165, 30)

                    # Add text to the page
                    page.insert_text(
                        text_position,
                        text,
                        fontsize=8,
                        # fontfile=font_path,  # Use custom font
                        color=(0, 0, 0)     # Black color
                    )

                # Loop through the list of images
                for image_info in images:
                    image_path = image_info['path']
                    page_num = image_info['page']
                    position = image_info['position']
                    scale = image_info['scale']

                    if not os.path.exists(image_path):
                        raise FileNotFoundError(
                            f"Image file not found: {image_path}")
                    with Image.open(image_path) as img:
                        img_width, img_height = img.size
                        new_width = img_width * scale
                        new_height = img_height * scale

                        page = pdf_document.load_page(page_num)
                        page.insert_image(
                            fitz.Rect(position[0], position[1], position[0] +
                                      new_width, position[1] + new_height),
                            filename=image_path
                        )

                    # Delete the image file after insertion
                    # os.remove(image_path)
                    # print(f"Deleted image: {image_path}")

                pdf_document.save(output_pdf_path)
                pdf_document.close()

                print(
                    f"Images and text added to the PDF. Saved as {output_pdf_path}")

                return output_pdf_path
            #  # Open the PDF file with the default viewer
            #     if os.name == 'nt':  # For Windows
            #         os.startfile(output_pdf_path)
            #     elif os.name == 'posix':  # For macOS and Linux
            #         subprocess.call(['open' if sys.platform == 'darwin' else 'xdg-open', output_pdf_path])

            except Exception as e:
                print(f"Error: {e}")
                return None

        output_pdf_path_export = add_images_and_text_to_pdf()

        return output_pdf_path_export
    except Exception as e:
        print("Error in function Main():", e)
        traceback.print_exc()
