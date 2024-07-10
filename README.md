## Langchain
#### This repo contains frontend and backend code for the AI Prototype

---

### Frameworks used
* Frontend
  - Framework:- NextJs on top of React
  - Package manager:- Bun
  - Styling:- Tailwind CSS
  - Application type:- SPA

---

* Backend
  - Framework:- Flask on top of Python
  - Package manager:- PIP
  - Tools:- Langchain
  - Vector Db:- ChromaDb

### How to use
* Frontend
  - Install packages
    ```node
    bun install
    ```
    or

    ```node
    yarn install
    ```
    ---

  - Run development environment
    ```node
    bun run dev
    ```

    or

    ```node
    yarn run dev
    ```
    ---
  
  - Create production build
    ```node
    bun run build
    ```

    or

    ```node
    yarn run build
    ```


* Backend
  - Create a virtual environment and activate it

    ```python
    python3 -m venv venv
    ```
    
    ```python
    source venv/bin/activate
    ```
  
  - Install requirements
    ```python
    pip install -r requirements.txt
    ```
  
  - Create a `.env` at the root of backend folder and add the following values
    ```
    OPENAI_API_KEY="<openai_api_key>"
    
    API_KEY="<polygon_api_key>"
    
    BASE_URL="https://api.polygon.io"
    
    VERSION="v2"
    
    AGGS_ENDPOINT="aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_}/{to}"

    ```
  
  - Run the development environment
    ```python
    python app.py
    ```

    or

    ```python
    flask run --port 5000 --reload
    ```

    or to run with gunicorn

    ```python
    gunicorn -w 4 -b 127.0.0.1:5000 app:app
    ```
  ---

  - You can also run this with Docker

    ```docker
    docker build . -t "backend:v1"
    ```

    ```docker
    docker run -dp 5000:5000 backend:v1
    ```
