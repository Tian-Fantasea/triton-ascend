# Contributing Guide

Thank you for your interest in contributing to the Triton-Ascend project! This document will help you understand how to contribute to the project.

## Developer Certificate of Origin (DCO)

All commits must include a `Signed-off-by:` line. Use `git commit -s` to add it automatically:

```bash
git commit -s -m "your commit message"
```

This will automatically add a line `Signed-off-by: Your Name <your.email@example.com>` at the end of your commit message, indicating that you certify the origin and authorization of the contribution.

## Development Environment Setup

### Local Environment Without NPU (Code Style Checks)

Triton-Ascend's build depends on `torch_npu` and only supports Linux. However, code style checks and basic tests can be performed on any system:

```bash
git clone https://github.com/{your_username}/triton-ascend.git
cd triton-ascend

pip install pre-commit
pre-commit install
pre-commit run --all-files
```

### Full Development Environment with NPU

Please first follow the [Installation Guide](installation_guide.md) to complete the installation and configuration of Python, CANN, and torch_npu.

**Quick Installation**:

```bash
git clone https://github.com/triton-lang/triton-ascend.git
cd triton-ascend
# Pull AscendNPU-IR
git submodule update --init --depth 1

# Optional: Use local LLVM build
# export LLVM_SYSPATH=/path/to/LLVM

pip install -e .
```

**Manual Installation**:

Prerequisites: LLVM 22 must be installed. For installation instructions, refer to: https://github.com/triton-lang/triton-ascend/blob/main/docs/en/installation_guide.md#manual-installation---llvm-based-build, where LLVM_INSTALL_PREFIX is the LLVM installation path

```bash
LLVM_SYSPATH=${LLVM_INSTALL_PREFIX} \
TRITON_BUILD_WITH_CCACHE=true \
TRITON_BUILD_WITH_CLANG_LLD=true \
TRITON_BUILD_PROTON=OFF \
TRITON_WHEEL_NAME="triton-ascend" \
TRITON_APPEND_CMAKE_ARGS="-DTRITON_BUILD_UT=OFF" \
python3 setup.py install
```

**Docker Installation**:

```bash
docker build \
  --build-arg CANN_BASE_IMAGE=quay.io/ascend/cann:8.5.0-a3-ubuntu22.04-py3.10 \
  -t triton-ascend-image:latest -f ./docker/Dockerfile .
```

### Install Development Dependencies

```bash
pip install -r python/requirements.txt
pip install -r python/test-requirements.txt
```

## Code Style

### Coding Standards

- **Python**: Follow [PEP 8](https://pep8.org/) coding style
- **C++**: Follow [LLVM Coding Standards](https://llvm.org/docs/CodingStandards.html)

### Code Checking Tools

The project uses [pre-commit](https://pre-commit.com/) to manage code checks, including the following tools:

| Tool | Purpose |
|---|---|
| ruff | Python code linting and formatting (line width 120) |
| yapf | Python code formatting (based on PEP 8, line width 120) |
| clang-format | C/C++ code formatting |
| mypy | Python type checking |
| pre-commit hooks | Trailing whitespace, end-of-file newline, YAML/TOML checks, large file detection, private key detection, etc. |

### Install and Run pre-commit

```bash
pip install pre-commit
pre-commit install        # Install git hook to run automatically on commits
pre-commit run --all-files  # Manually check all files
```

Before submitting a PR, it's recommended to run:

```bash
pre-commit run --from-ref origin/main --to-ref HEAD
```

### Unit Testing Standards

- **Python Tests**: Use [pytest](https://docs.pytest.org/)
- **C++ Tests**: Use [Google Test](https://github.com/google/googletest/blob/master/docs/primer.md)
- Test case design intent should be clearly reflected through naming. For test case design, refer to https://github.com/triton-lang/triton-ascend/blob/main/third_party/ascend/unittest/pytest_ut/test_gather.py

## Running Tests

### Test Directory Structure

| Directory | Content |
|---|---|
| `third_party/ascend/unittest/pytest_ut/` | Ascend-specific operator unit tests |
| `third_party/ascend/unittest/autotune_ut/` | Ascend autotune tests |
| `third_party/ascend/unittest/kernels/` | Third-party operator library validation (vLLM, etc.) |

### Using pytest

```bash

# Run Ascend-specific operator unit tests
python -m pytest third_party/ascend/unittest/pytest_ut/ -v -n 8

# Run a specific test file
python -m pytest third_party/ascend/unittest/pytest_ut/test_index_select_inductor.py -v
```

### PyTorch Inductor Validation

Triton-Ascend supports the PyTorch Inductor backend. You can validate Inductor integration through the following methods:

```bash

# Run Inductor operator tests
python -m pytest third_party/ascend/unittest/pytest_ut/test_index_select_inductor.py -v
```

You can also write tests using `torch.compile(..., backend="inductor")` to validate Inductor integration. Refer to the `test_inductor_add` example in `third_party/ascend/tutorials/07-profiler.py`.

### Third-Party Operator Library Validation

Triton-Ascend provides an integration validation framework for third-party operator libraries to ensure the correctness of Triton-based operator libraries on Ascend NPU.

**vLLM Kernels Validation**:

```bash
# Run all kernel validation
python -m pytest third_party/ascend/unittest/kernels/test_triton_kernel.py -v

# Run specific kernel validation
python -m pytest third_party/ascend/unittest/kernels/test_triton_kernel.py -v --kernel={kernel_name}
```

Currently covered vLLM kernels include: attention, rope, layer_norm, fused_gdn_gating, l2norm, etc. For the complete list, see the `third_party/ascend/unittest/kernels/vllm/` directory.

**Adding New Kernel Test Cases**:

Process for adding new third-party kernel test cases:
1. Prepare golden data (inputs and expected outputs) on GPU and save as `.pt` files
2. Add kernel operator files under `third_party/ascend/unittest/kernels/{library}/`
3. Upload `.pt` files to the OBS bucket: `https://triton-ascend-artifacts.obs.cn-southwest-2.myhuaweicloud.com/test/kernels/{library}_pt/{kernel_name}.pt`

For detailed instructions, see `third_party/ascend/unittest/kernels/README.md`.

## Fork-Pull Development Model

### 1. Fork the Repository

Fork [triton-lang/triton-ascend](https://github.com/triton-lang/triton-ascend) to your own account on GitHub.

### 2. Clone and Configure Remote Repository

```bash
git clone https://github.com/{your_username}/triton-ascend.git
cd triton-ascend
git submodule update --init --depth 1
git remote add upstream https://github.com/triton-lang/triton-ascend.git
```

### 3. Create Development Branch

```bash
git checkout -b {feature_branch_name} origin/main
git fetch upstream
git rebase upstream/main
```

### 4. Development and Self-Testing

After completing development, please ensure:
- Code passes pre-commit checks
- New code has corresponding test cases
- All related tests pass
- If operator implementations are modified, it's recommended to run Inductor validation and kernel comparison tests

### 5. Commit Code

```bash
git add {changed_files}
git commit -s -m "Brief description of this change"
git push origin {feature_branch_name}
```

Please follow the [How to Write a Git Commit Message](https://cbea.ms/git-commit/#why-not-how) specification for commit messages.

### 6. Create Pull Request

Create a Pull Request on GitHub from your fork repository's development branch to the `main` branch of `triton-lang/triton-ascend`. The CI pipeline will run automatically.

## PR Guidelines

### PR Title Prefixes

PR titles are recommended to use the following prefixes to indicate categories:

| Prefix | Description |
|---|---|
| `[BugFix]` | Bug fix |
| `[Kernel]` | Operator related |
| `[Core]` | Core module |
| `[Feature]` | New feature |
| `[Refactor]` | Code refactoring |
| `[Revert]` | Code revert |
| `[Perf]` | Performance optimization |
| `[Doc]` | Documentation update |
| `[Test]` | Test related |
| `[CI]` | CI/CD related |
| `[Misc]` | Other miscellaneous |

### PR Checklist

- [ ] Non-trivial changes (not just typo fixes)
- [ ] Follow [commit message guidelines](https://cbea.ms/git-commit/#why-not-how)
- [ ] Ran `pre-commit run --from-ref origin/main --to-ref HEAD`
- [ ] Added test cases, or explained why tests are not needed
- [ ] If adding lit tests, follow [MLIR Testing Best Practices](https://mlir.llvm.org/getting_started/TestingGuide/#filecheck-best-practices)

### PR Review and Merge

- PRs require at least 2 LGTMs (Looks Good To Me) and 1 Approval before merging
- Reviewers cannot add LGTM to their own PRs
- After creating a PR, please merge it promptly to reduce merge conflict risks

## Issue Guidelines

### Submitting Issues

When reporting issues, please include the following information:

- Software versions (Triton-Ascend, Python, OS, etc.)
- Issue type (bug report or feature request)
- Add corresponding labels
- Issue description: What happened?
- Expected behavior: What should have happened?
- Reproduction steps: Be as detailed as possible

### Issue Collaboration

- If you find an open Issue that you plan to work on, please comment on the Issue first
- For Issues that have been open for a while, please confirm the issue still exists before working on it
- If you resolve an Issue you reported yourself, please notify others before closing

## Notes

- Avoid committing unrelated changes
- Keep commit history clean and organized
- Please rebase with the latest upstream code before creating a PR
- For bug fix PRs, please link all related Issues

## More Information

- [Security Note](../../SECURITYNOTE.md)
- [Governance](governance.md)
- [FAQ](../FAQ.md)
