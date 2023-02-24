# PyBrewer [![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg)](LICENSE)

*PyBrewer* is a tool for management homebrew formulas.

## Terms of use

By using this project or its source code, for any purpose and in any shape or form, you grant your **implicit agreement** to all the following statements:

- You **condemn Russia and its military aggression against Ukraine**
- You **recognize that Russia is an occupant that unlawfully invaded a sovereign state**
- You **support Ukraine's territorial integrity, including its claims over temporarily occupied territories of Crimea and Donbas**
- You **reject false narratives perpetuated by Russian state propaganda**

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
