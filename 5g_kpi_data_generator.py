import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)

date_time = pd.date_range(start='5/1/2023', periods=30*24, freq='H')
cell_ids = ['Cell_' + str(i) for i in range(1, 11)]
kpi_categories = ['Accessibility', 'Retainability', 'Integrity', 'Mobility', 'Resource Usage', 'Traffic']

pis = {
    'Accessibility': ['Connection success rate (%)', 'Connection re-establishment rate (%)'],
    'Retainability': ['Call drop rate (%)', 'Drop per sec (drops/sec)'],
    'Integrity': ['Cell Throughput (Mbps)', 'User Throughput (Mbps)', 'Latency (ms)'],
    'Mobility': ['Handover success rate (%)', 'Handover failure rate (%)'],
    'Resource Usage': ['Resource Utilization (%)', 'Active UE'],
    'Traffic': ['Downlink Payload (MB)', 'Uplink Payload (MB)']
}

# Generate the data
data_list = []

cell_data = {cell_id: {} for cell_id in cell_ids}

for dt in date_time:
    for cell_id in cell_ids:
        cell_data[cell_id][dt] = {}
        for kpi_category in kpi_categories:
            for pi in pis[kpi_category]:

                base_value, std_dev, min_value, max_value = {
                    'Connection success rate (%)': (98, 1, 90, 100),
                    'Connection re-establishment rate (%)': (98, 1, 90, 100),
                    'Call drop rate (%)': (1, 0.5, 0, 2),
                    'Drop per sec (drops/sec)': (1, 0.1, 0, 5),  # Added hypothetical values for this PI
                    'Cell Throughput (Mbps)': (500, 100, 100, 1000),
                    'User Throughput (Mbps)': (500, 100, 100, 1000),
                    'Latency (ms)': (4, 1, 1, 10),
                    'Handover success rate (%)': (95, 2, 90, 100),
                    'Handover failure rate (%)': (5, 2, 0, 10),
                    'Resource Utilization (%)': (70, 10, 50, 100),
                    'Active UE': (100, 20, 10, 200),
                    'Downlink Payload (MB)': (5000, 1000, 1000, 10000),
                    'Uplink Payload (MB)': (5000, 1000, 1000, 10000)
                }[pi]

                value = np.random.normal(base_value, std_dev)
                
                prev_hour_value = cell_data[cell_id].get(dt - timedelta(hours=1), {}).get(pi, base_value)
                # Adding auto-regression component and smoothing with a moving average
                value = 0.8 * value + 0.2 * prev_hour_value + np.random.normal(0, std_dev / 10)

                value = max(min_value, min(max_value, value)) 

                cell_data[cell_id][dt][pi] = value

                data_list.append({
                    'date_time': dt,
                    'cell_id': cell_id,
                    'kpi_category': kpi_category,
                    'pi': pi,
                    'value': value
                })

data = pd.DataFrame(data_list)
data.to_csv('5G_NR_data.csv', index=False)