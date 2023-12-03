import pandas as pd
import matplotlib.pyplot as plt

def func():
    # Sample data
    data = {'Category': ['A', 'B', 'C', 'D', 'E'],
            'Values': [10, 25, 15, 30, 20]}

    # Create a DataFrame from the data
    df = pd.DataFrame(data)

    # Create a bar chart
    plt.figure(figsize=(8, 6))
    plt.bar(df['Category'], df['Values'], color='skyblue')
    plt.xlabel('Category')
    plt.ylabel('Values')
    plt.title('Pandas Bar Chart')

    # Display the chart
    plt.show()
    
func()    