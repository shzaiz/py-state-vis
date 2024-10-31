# Simple Python State Visualizer

## Overview

The `Visualizer` class provides a powerful way to visualize Python objects, including their attributes and relationships, in a graphical format using the Graphviz DOT language. It handles various data types, including primitives, lists, dictionaries, and custom objects, allowing for a clear understanding of complex data structures.


## Installation

To use the `Visualizer`, ensure you have the following dependencies installed:

```bash
pip install pydot
```

You may also need Graphviz installed on your system to render the graphs. You can download it from [Graphviz's official site](https://graphviz.gitlab.io/download/).

## Usage

Here's a basic example of how to use the `Visualizer` class:

```python
from visualizer import Visualizer  # Make sure to adjust the import based on your file structure

# Create an instance of Visualizer
visualizer = Visualizer()

# Example object to visualize
example_object = {
    "name": "Alice",
    "age": 30,
    "friends": ["Bob", "Charlie"],
    "details": {
        "hobbies": ["reading", "hiking"],
        "active": True
    }
}

# Visualize the example object
graph = visualizer.visualize(example_object)

# Save the graph to a file
graph.write('output_graph.dot')
```

TBD... The code is still under construction...
