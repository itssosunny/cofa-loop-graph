#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-.}"
mkdir -p "${TARGET_DIR}"
TARGET_DIR="$(cd "${TARGET_DIR}" && pwd)"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SOL_MODEL_ID="${SOL_MODEL_ID:-gpt-6.1-sol}"
TERRA_MODEL_ID="${TERRA_MODEL_ID:-gpt-5.6-terra}"
LUNA_MODEL_ID="${LUNA_MODEL_ID:-gpt-6-luna}"

echo "============================================================"
echo "Installing cofa-loop-graph plugin & subagents"
echo "  Target directory: ${TARGET_DIR}"
echo "  Models: Sol=${SOL_MODEL_ID}, Terra=${TERRA_MODEL_ID}, Luna=${LUNA_MODEL_ID}"
echo "============================================================"

# 1. Install Codex Subagents (*.toml files)
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
CODEX_AGENTS_DIR="${CODEX_HOME}/agents"
CODEX_CONFIG="${CODEX_HOME}/config.toml"
mkdir -p "${CODEX_AGENTS_DIR}"

# Copy regular files and substitute model IDs
sed -e "s/model = \"gpt-5.6-terra\"/model = \"${TERRA_MODEL_ID}\"/" \
    "${SCRIPT_DIR}/agents/executor.toml" > "${CODEX_AGENTS_DIR}/executor.toml"

sed -e "s/model = \"gpt-6-luna\"/model = \"${LUNA_MODEL_ID}\"/" \
    "${SCRIPT_DIR}/agents/luna_checker.toml" > "${CODEX_AGENTS_DIR}/luna_checker.toml"

sed -e "s/model = \"gpt-6.1-sol\"/model = \"${SOL_MODEL_ID}\"/" \
    "${SCRIPT_DIR}/agents/architect.toml" > "${CODEX_AGENTS_DIR}/architect.toml"

echo "✓ Installed 3 subagents to ${CODEX_AGENTS_DIR}"

# Idempotently register subagents and multi_agent feature in config.toml
touch "${CODEX_CONFIG}"

# Ensure [features] multi_agent = true
python3 -c "
import pathlib
p = pathlib.Path('${CODEX_CONFIG}')
text = p.read_text(encoding='utf-8') if p.exists() else ''
if '[features]' not in text:
    text += '\n[features]\nmulti_agent = true\n'
elif 'multi_agent' not in text:
    text = text.replace('[features]', '[features]\nmulti_agent = true')
p.write_text(text, encoding='utf-8')
"
echo "✓ Ensured multi_agent = true under [features] in ${CODEX_CONFIG}"

if ! grep -q '\[agents\.executor\]' "${CODEX_CONFIG}"; then
    cat << 'EOF' >> "${CODEX_CONFIG}"

[agents.executor]
description = "Fast implementation worker for bounded Tracer-Bullet vertical slices, UI components, API routes, and tests."
config_file = "./agents/executor.toml"
EOF
    echo "✓ Registered [agents.executor] in ${CODEX_CONFIG}"
fi

if ! grep -q '\[agents\.luna_checker\]' "${CODEX_CONFIG}"; then
    cat << 'EOF' >> "${CODEX_CONFIG}"

[agents.luna_checker]
description = "System-1 ultra-fast read-only checker for requirement predicates, quantitative metrics, and qualitative rubrics."
config_file = "./agents/luna_checker.toml"
EOF
    echo "✓ Registered [agents.luna_checker] in ${CODEX_CONFIG}"
fi

if ! grep -q '\[agents\.architect\]' "${CODEX_CONFIG}"; then
    cat << 'EOF' >> "${CODEX_CONFIG}"

[agents.architect]
description = "System-2 independent read-only reviewer for code correctness, anti-over-engineering, and code-to-documentation fidelity."
config_file = "./agents/architect.toml"
EOF
    echo "✓ Registered [agents.architect] in ${CODEX_CONFIG}"
fi

# Register evaluate MCP server in config.toml
mkdir -p "${CODEX_HOME}/cofa"
cp -f "${SCRIPT_DIR}/.cofa/luna_mcp.py" "${CODEX_HOME}/cofa/luna_mcp.py"
chmod +x "${CODEX_HOME}/cofa/luna_mcp.py"

if ! grep -q '\[mcp_servers\.evaluate\]' "${CODEX_CONFIG}"; then
    cat << EOF >> "${CODEX_CONFIG}"

[mcp_servers.evaluate]
command = "python3"
args = ["${CODEX_HOME}/cofa/luna_mcp.py", "mcp"]
EOF
    echo "✓ Registered [mcp_servers.evaluate] in ${CODEX_CONFIG}"
fi

# 2. Register Plugin via Codex CLI (if available)
if command -v codex >/dev/null 2>&1; then
    echo "• Registering marketplace and installing plugin via codex CLI..."
    codex plugin marketplace add "${SCRIPT_DIR}" || true
    codex plugin add cofa-loop-graph@cofa || true
    echo "✓ Plugin registered via codex CLI"
fi

# 3. Install Skills (to ~/.codex/skills, ~/.agents/skills, and ${TARGET_DIR}/.agents/skills)
SKILLS=("cofa-loop-graph" "grill-me" "to-questionnaire" "sharpen" "verification-before-completion" "evaluate")
CODEX_SKILLS_DIR="${CODEX_HOME}/skills"
GLOBAL_SKILLS_DIR="${GLOBAL_SKILLS_DIR:-${HOME}/.agents/skills}"
LOCAL_SKILLS_DIR="${TARGET_DIR}/.agents/skills"

for skill in "${SKILLS[@]}"; do
    for base_dir in "${CODEX_SKILLS_DIR}" "${GLOBAL_SKILLS_DIR}" "${LOCAL_SKILLS_DIR}"; do
        if [[ -z "${base_dir}" ]]; then
            continue
        fi
        mkdir -p "${base_dir}/${skill}"
        cp -f "${SCRIPT_DIR}/skills/${skill}/SKILL.md" "${base_dir}/${skill}/"
        if [[ -d "${SCRIPT_DIR}/skills/${skill}/agents" ]]; then
            mkdir -p "${base_dir}/${skill}/agents"
            cp -f "${SCRIPT_DIR}/skills/${skill}/agents/"* "${base_dir}/${skill}/agents/"
        fi
    done
done

echo "✓ Installed 6 skills to ${CODEX_SKILLS_DIR}, ${GLOBAL_SKILLS_DIR}, and ${LOCAL_SKILLS_DIR}"

# 4. Install .cofa verification suite and helper scripts
COFA_DIR="${TARGET_DIR}/.cofa"
mkdir -p "${COFA_DIR}"
cp -f "${SCRIPT_DIR}/.cofa/cofa_verify.py" "${COFA_DIR}/cofa_verify.py"
cp -f "${SCRIPT_DIR}/.cofa/with_server.py" "${COFA_DIR}/with_server.py"
cp -f "${SCRIPT_DIR}/.cofa/log_decision.sh" "${COFA_DIR}/log_decision.sh"
cp -f "${SCRIPT_DIR}/.cofa/luna_mcp.py" "${COFA_DIR}/luna_mcp.py"
chmod +x "${COFA_DIR}/cofa_verify.py" "${COFA_DIR}/with_server.py" "${COFA_DIR}/log_decision.sh" "${COFA_DIR}/luna_mcp.py"

if [[ ! -f "${COFA_DIR}/trace.json" ]]; then
    cp -f "${SCRIPT_DIR}/.cofa/trace.template.json" "${COFA_DIR}/trace.json"
    echo "✓ Initialized ${COFA_DIR}/trace.json from template"
else
    echo "• Retained existing ${COFA_DIR}/trace.json"
fi

echo "✓ Installed cofa_verify.py, with_server.py, log_decision.sh, and luna_mcp.py to ${COFA_DIR}"
echo "============================================================"
echo "Installation complete. Start with: python3 .cofa/cofa_verify.py --cheatsheet"
echo "============================================================"
