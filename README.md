# 5G Network Performance Dashboard

This script creates a dashboard for visualizing and analyzing 5G network performance data. The dashboard is built using Dash, a Python framework for building analytical web applications, and Plotly, a graphing library for creating interactive visualizations.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Dash
- pandas
- plotly
- numpy
- matplotlib
- dash-bootstrap-components

### Installation

1. Clone the repository or download the script.

2. Install the required dependencies using the following command:


## Usage

1. Place your 5G NR performance data file in the same directory as the script and update the file path in the `load_data` function.

2. Run the script using the following command:


3. Open a web browser and navigate to `http://127.0.0.1:8050` or the URL provided in the terminal.

4. Select the desired cell(s), performance indicator(s), and date range using the control panel.

5. Explore the different chart types available in the tabs to visualize the data.

## Features

- Select specific cells and performance indicators for analysis.
- Choose a custom date range to focus on specific time periods.
- View the data in different chart types, including line charts, bar charts, scatter plots, heatmaps, box plots, and histograms.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- This script is based on the Python Dash tutorial provided by Sigmoid Services. Check out their ebook "Python Dash: Build Interactive 5G KPI Dashboard from Scratch" for a comprehensive guide on building interactive dashboards using Dash and Plotly.
- Special thanks to the developers of Dash, Plotly, and other open-source libraries used in this script.
