"""Pipeline de análise EEG — orquestra leitura, pré-processamento e análise."""

import numpy as np

from backend.app.ml.edf_reader import read_edf
from backend.app.ml.preprocessing import (
    apply_bandpass_filter,
    apply_notch_filter,
    compute_band_power,
    identify_base_rhythm,
    check_age_normal,
)


# Canais padrão do sistema 10-20
STANDARD_CHANNELS = [
    "Fp1", "Fp2", "F3", "F4", "C3", "C4", "P3", "P4",
    "O1", "O2", "F7", "F8", "T3", "T4", "T5", "T6",
    "Fz", "Cz", "Pz",
]

LEFT_CHANNELS = ["Fp1", "F3", "C3", "P3", "O1", "F7", "T3", "T5"]
RIGHT_CHANNELS = ["Fp2", "F4", "C4", "P4", "O2", "F8", "T4", "T6"]
POSTERIOR_CHANNELS = ["O1", "O2", "P3", "P4"]


def _find_channel_indices(channel_names: list[str], target_channels: list[str]) -> list[int]:
    """Encontra índices dos canais alvo na lista de canais do exame."""
    name_map = {ch.upper(): i for i, ch in enumerate(channel_names)}
    indices = []
    for target in target_channels:
        idx = name_map.get(target.upper())
        if idx is not None:
            indices.append(idx)
    return indices


def analyze_asymmetry(data: np.ndarray, sfreq: float, channel_names: list[str]) -> dict:
    """Analisa assimetria entre hemisférios."""
    left_idx = _find_channel_indices(channel_names, LEFT_CHANNELS)
    right_idx = _find_channel_indices(channel_names, RIGHT_CHANNELS)

    if not left_idx or not right_idx:
        return {"has_asymmetry": False, "description": "Canais insuficientes para análise"}

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
        "description": (
            f"Assimetria detectada com predomínio no hemisfério {dominant_side}"
            if has_asymmetry
            else "Simétrico"
        ),
    }


def run_full_analysis(file_path: str, patient_age_years: int = 30) -> dict:
    """
    Pipeline completo de análise de um arquivo EDF.
    Retorna dicionário com todos os resultados.
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

    # 3. Ritmo de base
    posterior_idx = _find_channel_indices(channel_names, POSTERIOR_CHANNELS)
    if posterior_idx:
        base_rhythm = identify_base_rhythm(filtered, sfreq, posterior_idx)
        age_check = check_age_normal(base_rhythm["frequency_hz"], patient_age_years)
    else:
        base_rhythm = {"frequency_hz": 0, "amplitude_uv": 0}
        age_check = {"is_normal": None, "description": "Canais posteriores não encontrados"}

    # 4. Assimetria
    asymmetry = analyze_asymmetry(filtered, sfreq, channel_names)

    # 5. Classificação básica
    is_abnormal = asymmetry["has_asymmetry"] or (age_check.get("is_normal") is False)
    classification = "anormal" if is_abnormal else "normal"

    return {
        "metadata": metadata,
        "classification": classification,
        "base_rhythm_hz": base_rhythm["frequency_hz"],
        "base_rhythm_normal": age_check.get("is_normal"),
        "base_rhythm_description": age_check.get("description", ""),
        "has_asymmetry": asymmetry["has_asymmetry"],
        "asymmetry_details": asymmetry,
        "detected_patterns": {},  # Será expandido nos próximos meses
        "spike_count": 0,  # Será implementado no mês 4
        "artifacts_detected": {},
    }
