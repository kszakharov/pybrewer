# PyBrewer [![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg)](LICENSE)

*PyBrewer* is a tool for management homebrew formulas.

<script src="https://api.github.com/repos/kszakharov/pybrewer"></script>

## Contents

1. [Requirements](#requirements)
2. [Installations](#installation)
3. [Updating](#updating)
4. [Usages](#usages)
5. [Development](#development)
6. [License](#the-unlicense)

## Requirements

- python (3.9+)

## Installation

On macOS or Linux, you can install *PyBrewer* via [Homebrew](https://brew.sh/):

```bash
brew tap kzakharov/tools git@ghe.cloud.croc.ru:kzakharov/homebrew-kzakharov.git
brew install pybrewer --HEAD
```

## Updating

```bash
brew update
brew upgrade pybrewer --fetch-HEAD
```

## Usages

First you need to update the `poetry.lock` file
```bash
poetry lock --no-update
```

## Development

```bash
poetry install
```

## The Unlicense
Project License can be found [here](LICENSE).
