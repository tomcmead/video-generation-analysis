==================================================
Installation Guide
==================================================

The guide for **Video Generation Analysis** using **Poetry** for dependency management.

----

.. note::

   This project requires **Python 3.11** or newer.

----

1. Prerequisites
================

Before installing the project, ensure you have the following tools installed:

- **Python (3.11+)** — Download the installer from the `official Python website <https://www.python.org/downloads/>`_.
- **Poetry** — Used for packaging and dependency management. Follow the official `Poetry installation guide <https://python-poetry.org/docs/#installation>`_.

----

2. Setup
========

Clone the repository and install the project dependencies.

**a. Clone the Repository**

.. code-block:: bash

   git clone https://github.com/tomcmead/video-generation-analysis.git
   cd video-generation-analysis

**b. Install Dependencies with Poetry**

This command reads the ``pyproject.toml`` file, creates a virtual environment, and installs all main and development dependencies.

.. code-block:: bash

   poetry install
   poetry install --with-docs

----

3. Environment Variables
========================

To run the video publishing and analysis features, you need to set up certain environment variables (e.g., API keys).

Create a file named ``.env`` in the root of the project directory (it is ignored by ``.gitignore``).

**File:** ``.env``

.. code-block:: bash

   # YouTube API key for publishing
   YOUTUBE_API_KEY=your_youtube_key_here

   # Service key for analysis platform
   ANALYSIS_SERVICE_SECRET=your_secret_key_here

----

4. Run Application
==================

Execute the project’s main entry point within Poetry’s virtual environment.

.. code-block:: bash

   poetry run python video_generation_analysis/main.py

----

5. Development
==============

Run all tests in the ``tests/`` directory:

.. code-block:: bash

   poetry run pytest

Statically check code for type errors based on the Python version and strictness rules defined:

.. code-block:: bash

   poetry run mypy video_generation_analysis

Check code quality and automatically format it according to the rules defined in the ``pyproject.toml`` file:

.. code-block:: bash

   poetry run ruff format .

Create distributable files (``.whl`` and ``.tar.gz``) based on the package metadata:

.. code-block:: bash

   poetry build

Build documentation:

.. code-block:: bash

   poetry run sphinx-build -b html source _build