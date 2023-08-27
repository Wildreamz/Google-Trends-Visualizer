"""
Google_Trends_2.0.0.0

This script provides functions to fetch and visualize Google Trends data for specified keywords over a given timeframe.
It allows users to compare the popularity of different keywords and visualize their trends over time.

Key Updates:
    - Streamlined functions.
    - Allow user to access and export fetched data.

"""

## Import Modules -----------------------------------------------------------##

# Standard library imports
from datetime import datetime  # For date manipulations

# Third-party imports
import pandas as pd  # Data manipulation and analysis
import matplotlib.pyplot as plt  # Plotting library
import matplotlib.dates as mdates  # Date formatting for plots
import mplcursors  # Interactive data selection cursors for Matplotlib
import seaborn as sns  # Data visualization library based on Matplotlib
from pytrends.request import TrendReq  # Google Trends API

# Setting up the plotting style
sns.set()

# Close previously opened figures
plt.close('all')

## Define Functions ---------------------------------------------------------##

def divide_timeframe_range(start_date: str, end_date: str):
    """
    Function to divide the timeframe into two halves. 

    Args:
    - start_date (str): The start date in the format 'YYYY-MM-DD'
    - end_date (str): The end date in the format 'YYYY-MM-DD'

    Returns:
    - tuple: The start, midpoint, and end dates as strings in 'YYYY-MM-DD' format.
    """
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    midpoint_date_obj = start_date_obj + (end_date_obj - start_date_obj) / 2
    return start_date_obj.strftime('%Y-%m-%d'), midpoint_date_obj.strftime('%Y-%m-%d'), end_date_obj.strftime('%Y-%m-%d')

def get_data(keywords: list, timeframe_range: tuple, geo: str, youtube: bool):
    """
    Function to build a payload and return the trends for each keyword over time. 

    Args:
    - keywords (list): List of keywords for which to get the trends.
    - timeframe_range (tuple): Tuple containing the start and end dates as strings in 'YYYY-MM-DD' format.
    - geo (str): The geolocation for which to get the trends.
    - youtube (bool): A flag indicating whether to get trends from YouTube (True) or Google Search (False).

    Returns:
    - DataFrame: A DataFrame containing the combined trends for all keywords over time.

    """
    pytrends = TrendReq(hl='en-US', tz=360)
    start_date, midpoint_date, end_date = divide_timeframe_range(*timeframe_range)
    trends_data = []
    for time_range in [(start_date, midpoint_date), (midpoint_date, end_date)]:
        pytrends.build_payload(kw_list=keywords, timeframe=' '.join(time_range), geo=geo, cat="29" if youtube else "0")
        trends_data.append(pytrends.interest_over_time())
    
    for keyword in keywords:
        mean_second_half_start = trends_data[1][keyword].iloc[0]
        mean_first_half_end = trends_data[0][keyword].iloc[-1]
        scale_factor = mean_second_half_start / mean_first_half_end if mean_first_half_end != 0 else 1
        trends_data[0][keyword] *= scale_factor

    combined_data = pd.concat(trends_data)
    return combined_data

def plot_keyword_trends(trends_data, dpi=80, save_figure=False, figure_path='plot.png'):
    """
    Function to plot the trends for each keyword over time.

    Args:
    - trends_data (dataframe): Dataframe of Google Trends data.
    - dpi (int): The DPI for the plot.
    - save_figure (bool): A flag indicating whether to save the figure or not.
    - figure_path (str): The path to save the figure if save_figure is True.
    """

    # combined_data = pd.concat(trends_data)
    fig, ax = plt.subplots(figsize=(10, 6), dpi=dpi)
    fig.patch.set_facecolor('#19232d')
    ax.set_facecolor('#19232d')

    colors = ['#00FFFF', '#FF69B4', '#00ff99', '#ffff99', '#B2DF8A', '#32AA15']
    marker_size = 2  
    for i, keyword in enumerate(keywords):
        ax.plot(trends_data.index, trends_data[keyword], label=keyword, linewidth=2, alpha=0.9, color=colors[i % len(colors)], marker='s', markersize=marker_size)

    title = f'Google Trends - Keyword Trends\nTimeframe: {timeframe_range[0]} to {timeframe_range[1]}'
    title += '' if geo == '' else f'  Geolocation: {geo}'
    title += '  Source: YouTube Trends' if youtube else '  Source: Google Search Trends'

    ax.set_title(title, color='white')
    ax.set_ylabel('Interest over Time', color='white')
    ax.legend()
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    plt.xticks(rotation=45, color='white')
    plt.yticks(color='white')

    years = mdates.YearLocator()   
    years_fmt = mdates.DateFormatter('%Y')
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(years_fmt)

    # Enable cursor functionality
    cursor = mplcursors.cursor(ax)
    cursor.connect("add", lambda sel: sel.annotation.set_text(
        'Date: {}\nInterest: {:.2f}'.format(mdates.num2date(sel.target[0]).strftime('%Y-%m-%d'), sel.target[1])
    ))

    plt.tight_layout()
    if save_figure:
        plt.savefig(figure_path, dpi=dpi, facecolor='#19232d', edgecolor='#19232d')
    else:
        plt.show()

def plot_interest_ratio(trends_data, dpi=80, save_figure=False, figure_path='plot.png'):
    """
    Function to plot the ratio of search interest of Keyword 1 over Keyword 2 over time.

    Args:
    - trends_data (dataframe): Dataframe of Google Trends data.
    - dpi (int): The DPI for the plot.
    - save_figure (bool): A flag indicating whether to save the figure or not.
    - figure_path (str): The path to save the figure if save_figure is True.
    """

    keyword1 = trends_data.columns[0]
    keyword2 = trends_data.columns[1]

    # Calculate ratio
    ratio_data = trends_data[keyword1] / trends_data[keyword2]

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 6), dpi=dpi)
    fig.patch.set_facecolor('#19232d')
    ax.set_facecolor('#19232d')

    legend_label = f'{keyword1}\n/{keyword2}'
    
    ax.plot(ratio_data.index, ratio_data.values, label=legend_label, color='#FFA07A')

    title_line_1 = f'Interest Ratio Over Time ({timeframe_range[0]} - {timeframe_range[1]})'
    title_line_2 = f'Keyword 1: {keyword1}\nKeyword 2: {keyword2}'
    ax.set_title(title_line_1 + '\n' + title_line_2, color='white')
    ax.set_ylabel('Interest Ratio', color='white')
    ax.legend()
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    plt.xticks(rotation=45, color='white')
    plt.yticks(color='white')

    years = mdates.YearLocator()   
    years_fmt = mdates.DateFormatter('%Y')
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(years_fmt)

    # Enable cursor functionality
    cursor = mplcursors.cursor(ax)
    cursor.connect("add", lambda sel: sel.annotation.set_text(
        'Date: {}\nRatio: {:.2f}'.format(mdates.num2date(sel.target[0]).strftime('%Y-%m-%d'), sel.target[1])
    ))

    plt.tight_layout()
    if save_figure:
        plt.savefig(figure_path)
    plt.show()

def export_data_as_csv(df,csv_name):
    """
    Function to export a given pandas DataFrame to a CSV file.

    Args:
        - df (pandas.DataFrame): The DataFrame to be exported.
        - csv_name (str): The name (including path, if necessary) of the CSV file to which the data will be written.
    """
    df.to_csv(csv_name)
    return

## Main ---------------------------------------------------------------------##
        
# Set your desired parameters here
keywords = [
    "(PyTorch+PyTorch regression+PyTorch deep learning)",
    "(TensorFlow+TensorFlow regression+TensorFlow deep learning)"
]

timeframe_range = '2015-01-01', '2023-08-30'
geo = ''
youtube = False

# Call the function with the defined parameters
trends_data = get_data(keywords, timeframe_range, geo, youtube = youtube)
plot_keyword_trends(trends_data, dpi=120, save_figure=False, figure_path='plot.png')
plot_interest_ratio(trends_data, dpi=120, save_figure=False, figure_path='plot.png')
export_data_as_csv(trends_data,"Google_Trends_Data.csv")

print("Run completed.")