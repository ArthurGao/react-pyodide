import pandas as pd
import matplotlib.pyplot as plt
import io
import base64


def draw(content):

    # Create a DataFrame from the data
    df = pd.read_csv(StringIO(data_string))

    # Extract 'ds' and 'y' columns
    x = df['ds']
    y = df['y']

    # Create a line plot
    plt.plot(x, y)
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.title('Plot of y vs. ds')
    plt.xticks(rotation=45)


    # Display the chart
    #plt.show()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the image as base64
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    return image_base64
draw