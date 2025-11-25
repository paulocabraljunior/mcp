import plotly.express as px
import base64
import os

df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species", title="Iris Dataset")

# Force template
fig.update_layout(template="plotly_white")

img_bytes = fig.to_image(format="png", width=800, height=400, scale=2)

with open("test_chart.png", "wb") as f:
    f.write(img_bytes)

print("Image generated: test_chart.png")
