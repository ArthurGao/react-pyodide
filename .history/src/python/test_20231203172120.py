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
    #plt.show()
    #return plt.gcf().canvas
    # Save the chart to a BytesIO object
    image_stream = io.BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)

    # Display the chart using IPython.display
    display(Image(data=image_stream.read()))

    # Get the chart as a base64-encoded image
    image_stream.seek(0)
    image_data = image_stream.read()
    image_base64 = pyodide._module._getBase64FromUint8Array(pyodide._module._imageDataToUint8Array(image_data))
    return image_base64

func()