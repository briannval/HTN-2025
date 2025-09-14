# Hack The North 2025

![Project Diagram](diagram/diagram.jpeg)


## Setting up

Make sure Python version >= 3.13 is used

```bash
  python --version
```

Create a virtual environment

```bash
  python -m venv venv
```

Start the virtual environment

```bash
  source venv/bin/activate
```

Install the required dependencies

```bash
  pip install -r requirements.txt
```

Or on Mac

```bash
  pip install -r requirementsMac.txt
```

## Running the app

Clean the **OpenSearch** index

```bash
  python scripts/initOpenSearchIndex.py
```

Run the application
```bash
  python main.py
```

## Contributors

- Brian Adhitya 
- Li Minghao
- Patrick Zhou
- Dorson Tang

