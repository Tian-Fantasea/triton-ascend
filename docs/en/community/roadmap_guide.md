# Community Roadmap Writing and Publishing Guide
Use GitHub Issues to track and manage each organization's plans and mid-to-long-term goals. This document provides references and specifications for community projects on writing Roadmap-type Issues, to help create and maintain high-quality Roadmaps.

Below is a complete Roadmap Issue example demonstrating the practical application of all recommended elements. It is recommended to review this example first for an overall impression, then read the detailed specification instructions that follow.

```markdown
Create Issue title: [Roadmap] Triton-Ascend Core Roadmap 2026 Q1

---
# Triton-Ascend Core Roadmap 2026 Q1

This quarter focuses on long sequence parallel capability enhancement, FSDP training capability construction, and documentation system optimization, continuously improving training performance, ecosystem compatibility, and development usability.

## Focus

- Long Sequence: Enhance KV Allgather CP parallel capability and CP code maintainability
- FSDP Capability: Build FSDP2 training backend and Attn+MoE end-to-end training solution
- Documentation: Systematically optimize documentation structure and contribution compliance docs

## Long Sequence Enhancement

- [ ] **KV Allgather CP parallel scheme support**
Goal: Support KV Allgather CP parallel scheme
Issue: [Related Issue link]

- [ ] **CP code refactoring and interface alignment**
Goal: Complete CP code refactoring, align interfaces with TE, improve ease of integration for ecosystem libraries like VeRL
Issue: [Related Issue link]

## FSDP Capability

- [ ] **FSDP2-based training backend setup**
Goal: Set up a training backend based on the FSDP2 scheme, supporting direct HuggingFace model integration and decoupling from mcore
Issue: [Related Issue link]

- [ ] **Attn(FSDP) + MoE(EP+FSDP) training solution**
Goal: Build end-to-end training capability based on Qwen and QwenVL series
Issue: [Related Issue link]

## Documentation Optimization

- [ ] **Documentation structure optimization [🙋 Help Wanted]**
Goal: Adjust existing documentation structure, carry out systematic documentation optimization, and supplement contribution guidelines, directory structure, documentation license, and other compliance-related content
Issue: [Related Issue link]

```

## 1. Title Format

**Format:** `[Roadmap] <Project Name> Roadmap <Time Range>`, quarterly releases use Q1/Q2/Q3/Q4 markers, semi-annual releases use H1/H2 markers

**Examples:**

- `[Roadmap] MindSpeed Core Roadmap 2026 Q1`

## 2. Top-level Content

### 2.1 Opening Description (optional)

Provide a project overview, vision, or brief summary of the overall direction.

### 2.2 Focus Section

List the 3-5 most critical focus areas for this cycle, recommended to be grouped by the project's **functional domains** or **technical modules**, covering a holistic perspective:

```markdown
## Focus

• New feature & function: New feature and function development...
• Feature compatibility & reliability: Full compatibility and production-grade reliability...
• Usability: Usability improvements...
• Kernel optimization: Kernel optimization...
• Reinforcement learning: Reinforcement learning framework integration...
• Multimodal: Multimodal enhancements...
```

**Characteristics:**

- Summarize and describe the main development directions of the current project for the current cycle at a high level, no need to elaborate in detail

## 3. Major Functional Module Sections

### 3.1 Section Division Principles

Group by the project's **functional domains** or **technical modules**, such as:

- **Base Engine Features** - Base engine features
- **Parallelism** - Parallel processing
- **Server Reliability** - Server reliability
- **Kernel** - Kernel optimization

### 3.2 Structure of Each Module

Each module contains multiple **specific work items**, formatted as follows:

```markdown
## [Module Name]

- [ ] **Work item name/feature description**
Goal: [Goal description]
Owner: @GitHubID      [optional]
Issue: [Related Issue link]   [optional]
PR: [Related PR link]         [optional]

- [ ] **Another work item**
Goal: [Goal description]
Owner: @GitHubID      [optional]
Issue: [Related Issue link]   [optional]
PR: [Related PR link]         [optional]
```

## 4. Key Metadata Fields

Each work item should contain the following key information:

### 4.1 Goal

- **Meaning**: Work objective or brief description
- **Usage**: Explain the goal of this work item
- **Example**: `Goal: Support configuring pipelines in the repository`

### 4.2 Owner

- **Meaning**: Responsible person
- **Format**: `Owner: @GitHubID`
- **Usage**: Clarify who is responsible for or leading this work item
- **Example**: `Owner: @zhangsan`

### 4.3 Issue

- **Meaning**: Associated Gitcode Issue
- **Format**: `Issue: <Issue link>`
- **Usage**: Track detailed design and discussion
- **Example**: `Issue: https://github.com/triton-lang/triton-ascend/issues`

### 4.4 PR (Pull Request)

- **Meaning**: Related implementation PR
- **Format**: `PR: <PR link>`
- **Usage**: Link implementation work
- **Example**: `PR: https://github.com/triton-lang/triton-ascend/pulls`

## 5. Optional Supplementary Content

### 5.1 🙋 Help Wanted Marker

For work items where community developer contributions are especially welcome, it is recommended to use the **[🙋 Help Wanted]** marker to indicate:

```markdown
- [ ] **Work item name [🙋 Help Wanted]**
Goal: [Goal description]
Owner: TBD
Issue: #123
```

### 5.2 Sub-issues

List cross-cycle related Roadmap Issues or breakdown Issues for large work items at the bottom of the Roadmap Issue.

**Difference from the Issue field in work items:**

- **Issue field in work items**: Links to the specific work item's detailed design, discussion, or tracking Issue
- **Sub-issues section**: Used to associate Roadmap Issues from other cycles (e.g., unfinished work from the previous quarter), or to break down large work items into multiple independently tracked sub-Issues

```markdown
## Sub-issues

[xxx Roadmap (2025 Q4) #12780](link)  <!-- Related previous quarter Roadmap -->
[Feature X Phase 2 #12800](link)      <!-- Breakdown of a large work item -->
```
