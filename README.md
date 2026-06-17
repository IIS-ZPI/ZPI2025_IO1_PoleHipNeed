# NBP Currency Analytics System

A console-based analytical application implemented in Python, engineered to fetch, model, and perform advanced statistical operations on currency exchange datasets provided by the National Bank of Poland (NBP) API.

## 1. Technologies and Implementation Details

* **Programming Language:** Python (v3.11)
* **Application Type:** Command Line Interface (CLI) / Console Application

## 2. Deployment and Execution Guide

### Distribution and Deployment
The application is compiled and distributed as a standalone Windows executable (`.exe`). The official, production-ready binaries are hosted and deployed via **GitHub Releases**.

### How to Run the Application
1. Navigate to the **Releases** section of this GitHub repository.
2. Download the latest version of the executable asset (`main.exe`).
3. Open your terminal or command prompt, navigate to the download directory, and execute the binary.
```cmd
main.exe
```
*Note: Due to compilation via PyInstaller, no local Python runtime interpreter or external dependency installation is required on the host user's machine. However, beacuse the executable is exclusive to Windows, users of other operating systems should clone this repository and run the Python interpreter.*

## 3. Project Documentation Directory

All high-level engineering artifacts, system architecture specifications, modeling diagrams (component, sequence, and activity flows), and formal project reports are centralized within the repository:
* **Documentation Location:** `/docs`

## 4. Backlog and Project Management

Project requirement tracking and task distributions, are fully managed using native GitHub orchestration tools:
* **Backlog Location:** **GitHub Issues**

## 5. Continuous Integration (CI) and Automated Testing

The development lifecycle of the system is governed by an automated continuous integration and continuous delivery (CI/CD) pipeline built using GitHub Actions.

Continuous integration workflow is executed after a push to develop, release or main branch or after a pull request to these branches. The workflow executes the following steps:
- runs a Python runtime environment,
- installs dependencies specified in requirements.txt file,
- checks for code linting and formatting issues,
- runs unit tests.

If everything succeeds, a push or merge becomes possible.

Continuous delivery workflow is executed after the continuous integration workflow finishes and only if a new tag has been pushed. It executes the following steps:
- runs a Python runtime environment,
- installs dependencies specified in requirements.txt file,
- builds an executable file (.exe, exclusive to Windows)
- pushes a new release on GitHub and attaches the executable as an artifact.

## 6. Test reports

All historical validation outcomes, bug-tracking summaries and formal verification reports from testing and code fixing routines can be found in:
* **Test Reports Location:** `/docs/test_reports`
