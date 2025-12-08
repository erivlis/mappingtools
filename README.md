# MappingTools

> Do stuff with Mappings and more

This library provides utility functions for creating, manipulating, and transforming data structures,
which have or include Mapping-like characteristics.

Including inverting dictionaries, converting class-like objects to dictionaries, creating nested defaultdicts,
and unwrapping complex objects.

<table>
  <tr style="vertical-align: middle;">
    <td>Package</td>
    <td>
      <img alt="PyPI - Version" class="off-glb" loading="lazy" src="https://img.shields.io/pypi/v/mappingtools.svg?logo=pypi&logoColor=lightblue">
      <img alt="PyPI - Status" class="off-glb" loading="lazy" src="https://img.shields.io/pypi/status/mappingtools.svg?logo=pypi&logoColor=lightblue">
      <img alt="PyPI - Python Version" class="off-glb" loading="lazy" src="https://img.shields.io/pypi/pyversions/mappingtools.svg?logo=python&label=Python&logoColor=lightblue">
      <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dd/mappingtools.svg?logo=pypi&logoColor=lightblue">
      <img alt="PyPI - Dependents" src="https://dependents.info/erivlis/mappingtools/badge?logo=pypi&logoColor=lightblue">
      <img alt="Libraries.io SourceRank" src="https://img.shields.io/librariesio/sourcerank/pypi/mappingtools.svg?logo=Libraries.io&label=SourceRank">
    </td>
  </tr>
  <tr>
    <td>Code</td>
    <td>
      <img alt="GitHub" src="https://img.shields.io/github/license/erivlis/mappingtools">
      <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/erivlis/mappingtools.svg?label=Size&logo=git">
      <img alt="GitHub last commit (by committer)" src="https://img.shields.io/github/last-commit/erivlis/mappingtools.svg?&logo=git">
      <a href="https://github.com/erivlis/mappingtools/graphs/contributors"><img alt="Contributors" src="https://img.shields.io/github/contributors/erivlis/mappingtools.svg?&logo=git"></a>
    </td>
  </tr>
  <tr>
    <td>Tools</td>
    <td>
      <a href="https://www.jetbrains.com/pycharm/"><img alt="PyCharm" src="https://img.shields.io/badge/PyCharm-FCF84A.svg?logo=PyCharm&logoColor=black&labelColor=21D789&color=FCF84A"></a>
      <a href="https://github.com/astral-sh/uv"><img alt="uv" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" style="max-width:100%;"></a>
      <a href="https://github.com/astral-sh/ruff"><img alt="Ruff" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" style="max-width:100%;"></a>
      <!--a href="https://squidfunk.github.io/mkdocs-material/"><img src="https://img.shields.io/badge/Material_for_MkDocs-526CFE?&logo=MaterialForMkDocs&logoColor=white&labelColor=grey"></a-->
      <a href="https://hatch.pypa.io"><img alt="Hatch project" class="off-glb" loading="lazy" src="https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg"></a>
      <a href="https://commitizen-tools.github.io/commitizen"><img alt="commitizen" src="https://custom-icon-badges.demolab.com/badge/commitizen-7e56c2?logo=commitizen&labelColor=grey"></a>
    </td>
  </tr>
  <tr>
    <td>CI/CD</td>
    <td>
      <a href="https://github.com/erivlis/mappingtools/actions/workflows/test.yml"><img alt="Test" src="https://github.com/erivlis/mappingtools/actions/workflows/test.yml/badge.svg"></a>
      <a href="https://github.com/erivlis/mappingtools/actions/workflows/test-beta.yml"><img alt="Publish" src="https://github.com/erivlis/mappingtools/actions/workflows/test-beta.yml/badge.svg"></a>
      <a href="https://github.com/erivlis/mappingtools/actions/workflows/publish.yml"><img alt="Publish" src="https://github.com/erivlis/mappingtools/actions/workflows/publish.yml/badge.svg"></a>
      <a href="https://github.com/erivlis/mappingtools/actions/workflows/publish-docs.yaml"><img alt="Publish Docs" src="https://github.com/erivlis/mappingtools/actions/workflows/publish-docs.yml/badge.svg"></a>
    </td>
  </tr>
  <tr>
    <td>Scans</td>
    <td>
      <a href="https://codecov.io/gh/erivlis/mappingtools"><img alt="Coverage" src="https://codecov.io/gh/erivlis/mappingtools/graph/badge.svg?token=POODT8M9NV"/></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Quality Gate Status" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=alert_status"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Security Rating" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=security_rating"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Maintainability Rating" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=sqale_rating"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Reliability Rating" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=reliability_rating"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Lines of Code" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=ncloc"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Vulnerabilities" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=vulnerabilities"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Bugs" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=bugs"></a>
      <a href="https://app.codacy.com/gh/erivlis/mappingtools/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade"><img alt="Codacy Quality" src="https://app.codacy.com/project/badge/Grade/8b83a99f939b4883ae2f37d7ec3419d1"></a>
      <a href="https://app.codacy.com/gh/erivlis/mappingtools/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage"><img alt="Codacy Coverage" src="https://app.codacy.com/project/badge/Coverage/8b83a99f939b4883ae2f37d7ec3419d1"/></a>
      <a href="https://www.codefactor.io/repository/github/erivlis/mappingtools/overview/main"><img src="https://www.codefactor.io/repository/github/erivlis/mappingtools/badge/main" alt="CodeFactor" /></a>
      <a href="https://app.deepsource.com/gh/erivlis/mappingtools/" target="_blank"><img alt="DeepSource" title="DeepSource" src="https://app.deepsource.com/gh/erivlis/mappingtools.svg/?label=active+issues&show_trend=true&token=5hN3svCsdJtdULGTc68MngKa"/></a>
      <a href="https://app.deepsource.com/gh/erivlis/mappingtools/" target="_blank"><img alt="DeepSource" title="DeepSource" src="https://app.deepsource.com/gh/erivlis/mappingtools.svg/?label=resolved+issues&show_trend=true&token=5hN3svCsdJtdULGTc68MngKa"/></a>
      <a href="https://snyk.io/test/github/erivlis/mappingtools"><img alt="Snyk" src="https://snyk.io/test/github/erivlis/mappingtools/badge.svg"></a>
    </td>
  </tr>
</table>

## 🚀 Why use MappingTools?

Built for developers who need more than just standard dictionaries.

| Problem                 | Solution                                                                                             |
|:------------------------|:-----------------------------------------------------------------------------------------------------|
| **Deep JSON Diffing**   | Use `flattened()` to collapse nested JSON into single-layer paths for easy comparison.               |
| **Data Collisions**     | Use `inverse()` to swap keys/values without losing data (automatically creates sets for duplicates). |
| **Slow Config Loading** | Use `MeteredDict` to profile exactly how many times your app reads specific config keys.             |
| **Quick Serialization** | Use `simplify()` to instantly convert Dataclasses, DateTime, and custom objects into pure Dicts.     |

## Documentation

https://erivlis.github.io/mappingtools/

## Development

### Ruff

```shell
ruff check src

ruff check tests
```

### Test

#### Standard (cobertura) XML Coverage Report

```shell
python -m pytest tests --cov=src --cov-branch --doctest-modules --cov-report=xml
```

#### HTML Coverage Report

```shell
python -m pytest tests --cov=src --cov-branch --doctest-modules --cov-report=html
```
