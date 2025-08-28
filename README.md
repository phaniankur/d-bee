## 🐝 D-Bee: AI MySQL Co-pilot

D-Bee is an AI co-pilot that transforms plain English into complex executable SQL queries in seconds.

## Overview

D-Bee leverages local models installed in machine using Ollama to process and execute queries efficiently. The application is built with a focus on extensibility and ease of use.

![D-Bee in action](images/dbee_demo.jpeg)


## How to run the application

1. Ollama is must have to run this project: `pip install ollama`
2. Install the Llama 3.1 model: `python -m ollama.download --model llama3.1`
3. Install the required packages with pip: `pip install -r requirements.txt`
4. Run the application using: `uvicorn server.route:app --host 0.0.0.0 --port 5656`
5. App shall run in `http://localhost:5656/`

## Features

- Natural language query processing
- Direct query execution and result display
- Context-aware schema understanding
- Modular plug-and-play architecture

## Flow Diagram

                ┌──────────────────┐
                │ intent_classifier │
                └─────────┬────────┘
                          │
         ┌────────────────┴────────────────┐
         │                │                │
   intent="sql_query"  intent="execute"  intent="chitchat"
         │                │                │
         └────────────────┴────────────────┘
                          │
                ┌─────────▼─────────┐
                │  get_chat_history │
                └─────────┬─────────┘
                          │
         ┌────────────────┴────────────────┐
         │                                 │
 intent="sql_query"/"execute"        intent="chitchat"
         │                                 │
┌────────▼─────────┐                 ┌─────▼─────┐
│   get_schema_ctx │                 │  chitchat │
└────────┬─────────┘                 └─────┬─────┘
         │                                 │
 ┌───────▼─────────┐                       │
 │   generate_sql  │                       │
 └───────┬─────────┘                       │
         │                                 │
 ┌───────▼─────────┐                       │
 │    validate     │                       │
 └───────┬─────────┘                       │
         │                                 │
 ┌───────▼─────────┐                       │
 │     execute     │                       │
 └───────┬─────────┘                       │
         │                                 │
         ▼                                 ▼
        END                               END


## Roadmap

### Phase 1 - Core Implementation
- [x] Basic application setup with Llama 3.1 integration
- [x] Word-to-query execution system
- [x] Direct result display implementation

### Phase 2 - Enhanced Features
- [ ] Testing and benchmarking on different models like `sqlcoder` [wip]
- [x] Improved schema context understanding
- [x] Cache db tables and schema
- [ ] Understanding user intent to execution (query, results, analysis)[wip]
- [x] Short term memory (remembering chat context)
- [ ] Long term memory
- [ ] Planning Mode
- [ ] Choose between installed models from ui
- [x] user can modify the query from ui
- [x] update/delete query gaurdrailing
- [x] Remembering chat context
- [ ] Advanced result visualization
- [ ] Human intervention if required.
- [x] Gaurdrail for Non sql questions shall not be executed.
- [ ] Stream response instead of waiting for full response. 

### Phase 3 - UI
- [ ] A user can describe the schema of the database from ui.
- [ ] Migrate to Next.js
- [ ] New Chat UI
- [ ] Store old chat history to prevent re-execution of queries.

### Phase 4 - Architecture
- [ ] Plug-and-play component system
- [ ] Modular extension support
- [ ] API integration capabilities

## Getting Started

[Installation and setup instructions will evolve as the project develops]

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

[License information to be added]