# Contributing
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)
## Overview
All development of this project happens through GitHub. We welcome constructive collaboration from the community to help implement new features or fix bugs. 
## Code of Conduct
Before contributing, please familiarise yourself with our [Code of Conduct](CODE_OF_CONDUCT.md).
## Semantic Versioning
This project adheres to the [semantic versioning specification](https://semver.org). We release patch versions for critical bugfixes, minor versions for new features or non-essential changes, and major versions for any breaking changes. A brief summary of the specification is each release will have a version number in the format x.y.z:
- When releasing critical bug fixes, we make a patch release by changing the z number (ex: 1.0.0 to 1.0.1).
- When releasing new features or non-critical fixes, we make a minor release by changing the y number (ex: 1.0.5 to 1.1.0). 
- When releasing breaking changes, we make a major release by changing the x number (ex: 1.3.2 to 2.0.0). 
## Changelog
Every significant change is documented in the [changelog file](../CHANGELOG.md). To make this process easier, we utilise a specific commit format called [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#summary). The most important prefixes you should have in mind are:
- `fix:` which represents bug fixes, and correlates to a SemVer patch.
- `feat:` which represents a new feature, and correlates to a SemVer minor.
- `feat!:`, or fix!:, refactor!:, etc., which represent a breaking change (indicated by the !) and will result in a SemVer major. 

[Release Please](https://github.com/googleapis/release-please) is then used to automate the process of updating the [changelog file](../CHANGELOG.md) and bumping the version number.
## Branching 
All changes should occur in a branch specific to that fix or feature. A pull request can then be submitted for review. All code changes will be incorporated directly into the main branch. Code that lands in main must be compatible with the latest stable release. It may contain additional features, but no breaking changes. We should be able to release a new minor version from the tip of main at any time.