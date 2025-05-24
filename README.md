# 🐝 D-Bee: Natural Language to SQL Execution in Seconds 

D-Bee is an open-source tool that transforms plain English into executable SQL queries in seconds.

## Overview

D-Bee leverages local models installed in machine using Ollama to process and execute queries efficiently. The application is built with a focus on extensibility and ease of use.

![D-Bee in action](images/dbee_demo.jpeg)


## How to run the application

1. Ollama is must have to run this project: `pip install ollama`
2. Install the Llama 3.1 model: `python -m ollama.download --model llama3.1`
3. Install the required packages with pip: `pip install -r requirements.txt`
4. Run the application using: `fastapi run server/route.py`


## Features

- Natural language query processing
- Direct query execution and result display
- Context-aware schema understanding
- Modular plug-and-play architecture

## Roadmap

### Phase 1 - Core Implementation
- [x] Basic application setup with Llama 3.1 integration
- [x] Word-to-query execution system
- [x] Direct result display implementation

### Phase 2 - Enhanced Features
- [ ] Testing and benchmarking on different models like `sqlcoder` [wip]
- [ ] Improved schema context understanding [wip]
- [ ] Choose between installed models from ui
- [x] user can modify the query from ui
- [x] update/delete query gaurdrailing
- [ ] Enhanced query processing capabilities
- [ ] Remembering chat context
- [ ] Advanced result visualization

### Phase 3 - Architecture
- [ ] Plug-and-play component system
- [ ] Modular extension support
- [ ] API integration capabilities

## Getting Started

[Installation and setup instructions will evolve as the project develops]

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

[License information to be added]