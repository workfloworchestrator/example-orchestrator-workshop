# Integration tests

Tests that ensure the example orchestrator app works correctly with the latest orchestrator-core version. These are automatically executed in a github workflow.

You can also run them manually:

Environment setup:

1. Start the example orchestrator with `docker compose` as described in the previous section
2. Create a virtual environment
```
python -m venv .venv && source .venv/bin/activate
pip install requests pytest
```
1. Run the tests (**WARNING** this will remove all subscriptions in the local database):
```
pytest tests/integration_tests
```
