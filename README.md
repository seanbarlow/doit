# DoIt - Spec-Driven Development Framework

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/doit-toolkit/doit?style=social)](https://github.com/doit-toolkit/doit)
[![PyPI version](https://img.shields.io/pypi/v/doit-cli.svg)](https://pypi.org/project/doit-cli/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/github/actions/workflow/status/doit-toolkit/doit/tests.yml?label=tests)](https://github.com/doit-toolkit/doit/actions)
[![Docs](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://doit-toolkit.dev)

**See your architecture before you build it.** DoIt is an opinionated, AI-powered framework for specification-driven development. Define specifications, auto-generate diagrams, create roadmaps, and build with confidence.

[🚀 Quick Start](#quick-start) • [📖 Docs](https://doit-toolkit.dev) • [🤝 Contributing](#contributing) • [💬 Discord](https://discord.gg/doit) • [📝 Blog](https://doit-toolkit.dev/blog)

</div>

---

## ✨ Features

- **📋 Specification-Driven** - Define what you're building before you build it
- **📊 Auto-Generated Diagrams** - 100% automatic Mermaid diagrams from specs (user journeys, architecture, ER models, task dependencies, timelines)
- **🗺️ Intelligent Roadmapping** - Prioritized roadmaps with P1-P4 system and vision tracking
- **💾 Persistent Memory** - All project context stored in version-controlled `.doit/memory/` folder
- **🎯 Opinionated Approach** - Best practices built-in; strong opinions that reduce decision fatigue
- **🤖 AI-Powered** - Integrate any AI agent for implementation, testing, and documentation
- **👥 Team-Focused** - Quality gates, code reviews, and collaborative workflows built-in
- **📚 Living Docs** - Automatically organized and indexed project documentation
- **⚡ Zero Boilerplate** - 11 commands for the complete development lifecycle

## 🎯 The Problem DoIt Solves

Most projects fail not from technical debt, but from **architectural debt** - decisions made early without full context. Teams struggle with:

- ❌ Architecture decisions made in isolation
- ❌ Specifications that don't stay in sync with code
- ❌ Scattered documentation that's always out of date
- ❌ Roadmaps that don't reflect actual priorities
- ❌ Teams working from different understandings of the same system
- ❌ Manual diagram creation that becomes a chore

**DoIt solves this by making specification and decision-making the foundation of development.**

## 🚀 Quick Start

### Installation

```bash
# Using pipx (recommended)
pipx install doit-cli

# Or using pip
pip install doit-cli

# Or using uv (fastest)
uv tool install doit-cli
```

### Create Your First Project

```bash
# Create a new project
doit init

# Answer the guided setup questions
# - Project name
# - Description
# - Team size
# - Technology stack

# You'll get:
# ✅ Project scaffold
# ✅ .doit/memory/ folder with constitution
# ✅ tech-stack.md with your choices
# ✅ Ready to start specifying
```

### The DoIt Workflow

```bash
# 1. Write your specification
doit specit "A collaborative task management app with real-time updates"
# ↓ Auto-generates: user journey diagram, entity relationships

# 2. Create your technical plan
doit planit
# ↓ Auto-generates: architecture diagram, component dependencies

# 3. Break down into tasks
doit taskit
# ↓ Auto-generates: task dependencies, phase timeline

# 4. Implement with your AI agent
doit implementit

# 5. Run quality assurance
doit testit

# 6. Team review
doit reviewit

# 7. Check in and archive
doit checkin
```

**That's it.** From spec to shipped in 7 commands.

## 📚 The 11 Commands

| Command | Purpose | Output |
|---------|---------|--------|
| **specit** | Define user stories and features | User journey diagrams, spec.md |
| **constitution** | Document project principles | constitution.md |
| **planit** | Create technical architecture | Architecture diagram, plan.md |
| **taskit** | Break down into tasks | Task dependencies, timeline, tasks.md |
| **implementit** | Implement features | Runs AI agent on task queue |
| **testit** | Quality assurance | Test results, coverage reports |
| **reviewit** | Team code review | Review findings, review-report.md |
| **roadmapit** | Manage priorities | roadmap.md with P1-P4 items |
| **documentit** | Organize documentation | Organized docs/, index.md |
| **checkin** | Archive completed work | Moves items to completed_roadmap.md |
| **scaffoldit** | Bootstrap new projects | .doit/ structure, tech-stack.md |

## 🏗️ Project Structure

```
your-project/
├── README.md                    # Your project README
├── .doit/                       # DoIt configuration (version control!)
│   ├── memory/
│   │   ├── constitution.md      # Project principles
│   │   ├── spec.md              # Feature specifications
│   │   ├── plan.md              # Technical architecture
│   │   ├── tasks.md             # Task breakdown
│   │   ├── roadmap.md           # Feature priorities (P1-P4)
│   │   ├── tech-stack.md        # Technology choices
│   │   ├── review-report.md     # Code review findings
│   │   └── completed_roadmap.md # Archive of shipped features
│   ├── templates/
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   └── task-template.md
│   └── scripts/
│       ├── pre-spec.sh
│       ├── post-spec.sh
│       └── ...
├── docs/                        # Auto-organized documentation
│   ├── index.md                 # Documentation home
│   ├── getting-started/
│   ├── guides/
│   ├── reference/
│   ├── architecture/
│   └── examples/
├── src/                         # Your application code
├── tests/                       # Test files
└── .gitignore
```

## 📊 Auto-Generated Diagrams

DoIt automatically generates these diagram types from your specifications:

- **User Journey** - How users interact with your system
- **Architecture** - System components and boundaries
- **Component Dependencies** - Service relationships
- **Entity Relationships** - Database schema
- **Sequence Diagrams** - Time-based interactions
- **Task Dependencies** - Execution order and critical path
- **Phase Timeline** - Gantt chart of development phases
- **Finding Distribution** - Code review findings breakdown
- **Test Results** - Test pass/fail visualization

All diagrams are in Mermaid format, work in markdown, and update automatically when specs change.

## 🧠 Persistent Memory System

Your entire project context lives in version-controlled markdown files:

```
.doit/memory/
├── constitution.md        # "Why do we exist? What are our principles?"
├── spec.md                # "What are we building?"
├── plan.md                # "How will we build it?"
├── tasks.md               # "What are the specific tasks?"
├── roadmap.md             # "What's the priority order?"
├── tech-stack.md          # "What technologies are we using?"
├── review-report.md       # "What did we find in code review?"
└── completed_roadmap.md   # "What have we shipped?" (20-item archive)
```

Because these files are in git:
- ✅ Your entire team sees the same context
- ✅ History is preserved (git blame, logs)
- ✅ Decisions are documented with rationale
- ✅ New team members have full context
- ✅ No external dependencies or databases

## 🤖 AI Agent Integration

DoIt works with any AI agent. Popular integrations:

```bash
# OpenAI
doit implementit --agent openai --model gpt-4

# Anthropic Claude
doit implementit --agent anthropic --model claude-opus

# Local Ollama
doit implementit --agent ollama --model llama2

# Custom agents
doit implementit --agent custom --config agent-config.yaml
```

Agents have access to:
- Full project specification and architecture
- Task breakdown and dependencies
- Team's code review findings
- Project constitution and principles
- Tech stack documentation
- Previous successful implementations

## 📖 Documentation

- **[Getting Started](https://doit-toolkit.dev/docs/getting-started/)** - 5-minute tutorial
- **[Commands Reference](https://doit-toolkit.dev/docs/commands/)** - Detailed command documentation
- **[Architecture Guide](https://doit-toolkit.dev/docs/architecture/)** - Deep dive into DoIt's design
- **[Diagrams Gallery](https://doit-toolkit.dev/docs/diagrams/)** - All diagram types explained
- **[Best Practices](https://doit-toolkit.dev/docs/best-practices/)** - Team workflows and patterns
- **[API Reference](https://doit-toolkit.dev/api/)** - Python API documentation
- **[FAQ](https://doit-toolkit.dev/docs/faq/)** - Common questions answered

## 🎓 Learning Path

1. **[Quick Start](https://doit-toolkit.dev/docs/getting-started/)** (5 min) - Get DoIt running
2. **[First Project](https://doit-toolkit.dev/docs/first-project/)** (15 min) - Create your first spec
3. **[Team Workflows](https://doit-toolkit.dev/docs/team-workflows/)** (20 min) - Set up with your team
4. **[Advanced Features](https://doit-toolkit.dev/docs/advanced/)** (30 min) - Master all 11 commands
5. **[Custom Agents](https://doit-toolkit.dev/docs/custom-agents/)** (45 min) - Build your own AI integration

## 💡 Use Cases

### Software Startups
Define your MVP specification upfront, auto-generate architecture diagrams, keep your team aligned on priorities.

### Enterprise Teams
Maintain architectural consistency, document technical decisions, facilitate code reviews with structured findings.

### Open Source Projects
Reduce onboarding friction with accessible specifications, empower contributors with clear technical context.

### Consulting Firms
Deliver better architecture upfront, document design decisions, streamline handoff to client teams.

## 🔄 Comparison: DoIt vs. Spec-Kit

DoIt is an opinionated fork of Spec-Kit built for **teams and workflows**.

| Feature | Spec-Kit | DoIt |
|---------|----------|------|
| **Philosophy** | Flexible, foundational | Opinionated, team-focused |
| **Diagrams** | Basic (text-based) | Rich (auto-generated Mermaid) |
| **Roadmaps** | Not included | Built-in P1-P4 system |
| **Documentation** | Manual | Auto-organized with indexing |
| **Team Workflows** | Minimal | Quality gates, code review |
| **AI Integration** | None | Flexible agent support |
| **Living Docs** | Limited | Full memory system |

## 🤝 Contributing

We love contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for details on:

- Setting up development environment
- Running tests
- Submitting pull requests
- Reporting bugs
- Suggesting features
- Writing documentation

**Quick start for contributors:**

```bash
# Clone the repo
git clone https://github.com/doit-toolkit/doit.git
cd doit

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run type checks
mypy src/

# Format code
black src/ tests/
```

## 📋 Code of Conduct

This project is committed to providing a welcoming and inclusive environment. See [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) for our community guidelines.

## 🔐 Security

Found a security vulnerability? Please report it responsibly. See [SECURITY.md](./SECURITY.md) for details.

## 📝 License

DoIt is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

**In short:** You can use, modify, and distribute DoIt freely, including in commercial projects. Attribution appreciated but not required.

## 🐛 Reporting Issues

Found a bug? Have a feature request?

- **[GitHub Issues](https://github.com/doit-toolkit/doit/issues)** - Bug reports and feature requests
- **[Discussions](https://github.com/doit-toolkit/doit/discussions)** - Questions and ideas
- **[Discord](https://discord.gg/doit)** - Real-time chat with the team

Please include:
- DoIt version (`doit --version`)
- Python version (`python --version`)
- Operating system
- Steps to reproduce (for bugs)
- Expected vs. actual behavior

## 📊 Status

- **Current Version:** 1.0.0
- **Python Support:** 3.9, 3.10, 3.11, 3.12
- **Status:** Production Ready
- **Test Coverage:** 92%
- **Last Updated:** January 2026

See [CHANGELOG.md](./CHANGELOG.md) for release notes.

## 🙏 Acknowledgments

- Built on the excellent foundation of [Spec-Kit](https://github.com/speckit/speckit)
- Diagram generation powered by [Mermaid](https://mermaid.js.org/)
- Documentation inspired by [Stripe](https://stripe.com/docs) and [Vercel](https://vercel.com/docs)
- Community inspired by [Python Software Foundation](https://www.python.org/psf/)

## 💬 Community

- **[Discord Community](https://discord.gg/doit)** - Chat with developers
- **[Twitter](https://twitter.com/doit_toolkit)** - Latest updates
- **[Blog](https://doit-toolkit.dev/blog)** - Articles and tutorials
- **[GitHub Discussions](https://github.com/doit-toolkit/doit/discussions)** - Ask questions

## 📈 Roadmap

Current focus areas:

- [ ] VS Code extension for inline spec editing
- [ ] Web UI for roadmap and diagram visualization
- [ ] GitHub integration (PR comments with findings, auto-archive on merge)
- [ ] Jira/Linear integration for task management
- [ ] Enterprise self-hosted deployment guide
- [ ] Multi-language support (Python, Go, Rust, etc.)
- [ ] Performance improvements for large projects (10k+ tasks)

See [ROADMAP.md](./ROADMAP.md) for detailed plans and voting.

## 📞 Support

- **[Docs](https://doit-toolkit.dev)** - Comprehensive documentation
- **[Discord](https://discord.gg/doit)** - Community support
- **[Email](mailto:support@doit-toolkit.dev)** - Enterprise support
- **[GitHub Issues](https://github.com/doit-toolkit/doit/issues)** - Bug reports

---

<div align="center">

**Made with ❤️ by the DoIt community**

[⭐ Star us on GitHub](https://github.com/doit-toolkit/doit) • [🐦 Follow on Twitter](https://twitter.com/doit_toolkit) • [💬 Join Discord](https://discord.gg/doit)

</div>
