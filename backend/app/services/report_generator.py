"""Serviço de geração de laudos EEG."""

from backend.app.core.config import get_settings
from backend.app.services.llm_provider import get_llm


SYSTEM_PROMPT = """Você é um médico neurofisiologista experiente brasileiro.
Escreva laudos de eletroencefalograma seguindo o padrão brasileiro.
Use terminologia médica técnica apropriada em português.
Seja objetivo e preciso.
NÃO invente informações não fornecidas nos dados.
Indique "EEG NORMAL" ou "EEG ANORMAL" na conclusão."""


def build_report_prompt(
    patient_name: str,
    patient_age: str,
    indication: str,
    duration_minutes: float,
    analysis_data: dict,
) -> str:
    """Monta o prompt para geração do laudo."""

    classification = analysis_data.get("classification", "indeterminado")
    base_rhythm = analysis_data.get("base_rhythm_hz", "não calculado")
    has_asymmetry = analysis_data.get("has_asymmetry", False)
    asymmetry_desc = analysis_data.get("asymmetry_details", {}).get("description", "Não avaliado")
    spike_count = analysis_data.get("spike_count", 0)
    patterns = analysis_data.get("detected_patterns", {})
    pattern_list = ", ".join(patterns.keys()) if patterns else "Nenhum detectado"

    return f"""Escreva um laudo de eletroencefalograma completo com a seguinte estrutura:

DADOS DO PACIENTE:
- Nome: {patient_name}
- Idade: {patient_age}
- Indicação: {indication}

DADOS TÉCNICOS:
- Duração: {duration_minutes:.0f} minutos
- Condições: ambulatorial
- Qualidade: Satisfatória

ANÁLISE COMPUTADORIZADA:
- Classificação: {classification}
- Ritmo de base: {base_rhythm} Hz nas regiões posteriores
- Assimetria: {"Sim — " + asymmetry_desc if has_asymmetry else "Não detectada"}
- Paroxismos detectados: {spike_count} eventos
- Padrões anormais: {pattern_list}

ESTRUTURA DO LAUDO:
1. IDENTIFICAÇÃO
2. INFORMAÇÕES TÉCNICAS
3. ATIVIDADE DE BASE
4. ATIVIDADE EPILEPTIFORME
5. CONCLUSÃO

REGRAS:
- Use terminologia médica técnica
- Seja objetivo e preciso
- NÃO invente dados não fornecidos
- Indique EEG NORMAL ou EEG ANORMAL na conclusão"""


async def generate_report(
    patient_name: str,
    patient_age: str,
    indication: str,
    duration_minutes: float,
    analysis_data: dict,
) -> str:
    """Gera o texto do laudo via LLM."""
    llm = get_llm()
    prompt = build_report_prompt(
        patient_name=patient_name,
        patient_age=patient_age,
        indication=indication,
        duration_minutes=duration_minutes,
        analysis_data=analysis_data,
    )
    return await llm.generate(prompt=prompt, system_prompt=SYSTEM_PROMPT)
