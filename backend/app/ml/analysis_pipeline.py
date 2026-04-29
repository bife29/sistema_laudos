"""Pipeline de análise EEG — orquestra leitura, pré-processamento e análise.

Suporta dois tipos de montagem:
- Referencial: canais como Fp1, O1, C3 (sistema 10-20)
- Bipolar: canais como FP1-F7, F7-T7, P7-O1 (montagem longitudinal)
"""

import numpy as np

from backend.app.ml.edf_reader import read_edf
from backend.app.ml.preprocessing import (
    apply_bandpass_filter,
    apply_notch_filter,
    compute_band_power,
    identify_base_rhythm,
    check_age_normal,
)


# Canais padrão do sistema 10-20 (referencial)
STANDARD_CHANNELS = [
    "Fp1", "Fp2", "F3", "F4", "C3", "C4", "P3", "P4",
    "O1", "O2", "F7", "F8", "T3", "T4", "T5", "T6",
    "Fz", "Cz", "Pz",
]

LEFT_CHANNELS = ["Fp1", "F3", "C3", "P3", "O1", "F7", "T3", "T5"]
RIGHT_CHANNELS = ["Fp2", "F4", "C4", "P4", "O2", "F8", "T4", "T6"]
POSTERIOR_CHANNELS = ["O1", "O2", "P3", "P4"]

# Montagem bipolar longitudinal — canais do lado esquerdo e direito
BIPOLAR_LEFT = ["FP1-F7", "F7-T7", "T7-P7", "P7-O1", "FP1-F3", "F3-C3", "C3-P3", "P3-O1"]
BIPOLAR_RIGHT = ["FP2-F8", "F8-T8", "T8-P8", "P8-O2", "FP2-F4", "F4-C4", "C4-P4", "P4-O2"]
BIPOLAR_POSTERIOR = ["P7-O1", "P3-O1", "P8-O2", "P4-O2", "T7-P7", "T8-P8"]

# Nomes alternativos para canais bipolares (T3=T7, T4=T8, T5=P7, T6=P8)
BIPOLAR_LEFT_ALT = ["FP1-F7", "F7-T3", "T3-T5", "T5-O1", "FP1-F3", "F3-C3", "C3-P3", "P3-O1"]
BIPOLAR_RIGHT_ALT = ["FP2-F8", "F8-T4", "T4-T6", "T6-O2", "FP2-F4", "F4-C4", "C4-P4", "P4-O2"]
BIPOLAR_POSTERIOR_ALT = ["T5-O1", "P3-O1", "T6-O2", "P4-O2"]


def _detect_montage(channel_names: list[str]) -> str:
    """Detecta se o EDF usa montagem referencial ou bipolar."""
    has_dash = sum(1 for ch in channel_names if "-" in ch)
    if has_dash > len(channel_names) * 0.5:
        return "bipolar"
    return "referencial"


def _find_channel_indices(channel_names: list[str], target_channels: list[str]) -> list[int]:
    """Encontra índices dos canais alvo na lista de canais do exame.
    
    Faz match case-insensitive e trata espaços.
    """
    name_map = {ch.strip().upper(): i for i, ch in enumerate(channel_names)}
    indices = []
    for target in target_channels:
        idx = name_map.get(target.strip().upper())
        if idx is not None:
            indices.append(idx)
    return indices


def _find_bipolar_indices(channel_names: list[str], targets_list: list[list[str]]) -> list[int]:
    """Tenta encontrar canais bipolares em múltiplas listas de alternativas."""
    for targets in targets_list:
        indices = _find_channel_indices(channel_names, targets)
        if len(indices) >= 2:
            return indices
    return []


def analyze_asymmetry(data: np.ndarray, sfreq: float, channel_names: list[str]) -> dict:
    """Analisa assimetria entre hemisférios. Suporta montagem referencial e bipolar."""
    montage = _detect_montage(channel_names)

    if montage == "bipolar":
        left_idx = _find_bipolar_indices(channel_names, [BIPOLAR_LEFT, BIPOLAR_LEFT_ALT])
        right_idx = _find_bipolar_indices(channel_names, [BIPOLAR_RIGHT, BIPOLAR_RIGHT_ALT])
    else:
        left_idx = _find_channel_indices(channel_names, LEFT_CHANNELS)
        right_idx = _find_channel_indices(channel_names, RIGHT_CHANNELS)

    if not left_idx or not right_idx:
        return {
            "has_asymmetry": False,
            "description": "Canais insuficientes para análise de assimetria",
            "montage": montage,
            "left_channels": len(left_idx),
            "right_channels": len(right_idx),
        }

    left_power = compute_band_power(data[left_idx], sfreq)
    right_power = compute_band_power(data[right_idx], sfreq)

    asymmetry_scores = {}
    for band in ["delta", "theta", "alpha", "beta"]:
        l_val = left_power.get(band, 0)
        r_val = right_power.get(band, 0)
        avg = (l_val + r_val) / 2
        if avg > 0:
            asymmetry_scores[band] = abs(l_val - r_val) / avg
        else:
            asymmetry_scores[band] = 0

    has_asymmetry = any(score > 0.3 for score in asymmetry_scores.values())
    dominant_side = "esquerdo" if left_power.get("total", 0) > right_power.get("total", 0) else "direito"

    return {
        "has_asymmetry": has_asymmetry,
        "scores": asymmetry_scores,
        "dominant_side": dominant_side,
        "montage": montage,
        "left_channels": len(left_idx),
        "right_channels": len(right_idx),
        "description": (
            f"Assimetria detectada com predomínio no hemisfério {dominant_side}"
            if has_asymmetry
            else "Simétrico"
        ),
    }


def run_full_analysis(file_path: str, patient_age_years: int = 30) -> dict:
    """
    Pipeline completo de análise de um arquivo EDF.
    Suporta montagem referencial (10-20) e bipolar.
    """
    # 1. Ler arquivo
    result = read_edf(file_path)
    metadata = result["metadata"]

    data = result["data"]
    sfreq = metadata["sampling_rate"]
    channel_names = metadata["channel_names"]

    # 2. Pré-processamento
    filtered = apply_bandpass_filter(data, sfreq)
    filtered = apply_notch_filter(filtered, sfreq)

    # 3. Detectar tipo de montagem
    montage = _detect_montage(channel_names)

    # 4. Ritmo de base
    if montage == "bipolar":
        posterior_idx = _find_bipolar_indices(
            channel_names, [BIPOLAR_POSTERIOR, BIPOLAR_POSTERIOR_ALT]
        )
    else:
        posterior_idx = _find_channel_indices(channel_names, POSTERIOR_CHANNELS)

    if posterior_idx:
        base_rhythm = identify_base_rhythm(filtered, sfreq, posterior_idx)
        age_check = check_age_normal(base_rhythm["frequency_hz"], patient_age_years)
    else:
        # Fallback: usar todos os canais para tentar encontrar ritmo dominante
        base_rhythm = identify_base_rhythm(filtered, sfreq, list(range(min(4, len(channel_names)))))
        age_check = check_age_normal(base_rhythm["frequency_hz"], patient_age_years)
        age_check["description"] = age_check.get("description", "") + " (canais posteriores não identificados, análise global)"

    # 5. Assimetria
    asymmetry = analyze_asymmetry(filtered, sfreq, channel_names)

    # 6. Classificação
    is_abnormal = asymmetry["has_asymmetry"] or (age_check.get("is_normal") is False)
    classification = "anormal" if is_abnormal else "normal"

    return {
        "metadata": {**metadata, "montage_type": montage},
        "classification": classification,
        "base_rhythm_hz": base_rhythm["frequency_hz"],
        "base_rhythm_normal": age_check.get("is_normal"),
        "base_rhythm_description": age_check.get("description", ""),
        "has_asymmetry": asymmetry["has_asymmetry"],
        "asymmetry_details": asymmetry,
        "detected_patterns": {},
        "spike_count": 0,
        "artifacts_detected": {},
    }
