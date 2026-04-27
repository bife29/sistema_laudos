"""Pré-processamento de sinais EEG."""

import numpy as np


def apply_bandpass_filter(data: np.ndarray, sfreq: float, low: float = 0.5, high: float = 70.0) -> np.ndarray:
    """Filtro passa-banda."""
    from scipy.signal import butter, filtfilt

    nyquist = sfreq / 2
    b, a = butter(4, [low / nyquist, high / nyquist], btype="band")
    return filtfilt(b, a, data, axis=-1)


def apply_notch_filter(data: np.ndarray, sfreq: float, freq: float = 60.0) -> np.ndarray:
    """Filtro notch (remove ruído da rede elétrica)."""
    from scipy.signal import iirnotch, filtfilt

    b, a = iirnotch(freq, Q=30, fs=sfreq)
    return filtfilt(b, a, data, axis=-1)


def compute_band_power(data: np.ndarray, sfreq: float) -> dict:
    """Calcula potência espectral por banda de frequência."""
    from scipy.signal import welch

    freqs, psd = welch(data, sfreq, nperseg=min(2048, data.shape[-1]))

    bands = {
        "delta": (0.5, 4),
        "theta": (4, 8),
        "alpha": (8, 13),
        "beta": (13, 30),
        "gamma": (30, 70),
    }

    result = {}
    for name, (low, high) in bands.items():
        mask = (freqs >= low) & (freqs <= high)
        result[name] = float(np.mean(psd[..., mask]))

    result["total"] = float(np.mean(psd))
    return result


def identify_base_rhythm(data: np.ndarray, sfreq: float, posterior_indices: list[int]) -> dict:
    """Identifica o ritmo de base nas regiões posteriores."""
    from scipy.signal import welch

    posterior_data = data[posterior_indices]
    freqs, psd = welch(posterior_data, sfreq, nperseg=min(2048, posterior_data.shape[-1]))

    # Faixa alfa (8-13 Hz)
    alpha_mask = (freqs >= 8) & (freqs <= 13)
    alpha_psd = np.mean(psd[:, alpha_mask], axis=0)
    alpha_freqs = freqs[alpha_mask]

    if len(alpha_psd) > 0 and np.max(alpha_psd) > 0:
        dominant_freq = float(alpha_freqs[np.argmax(alpha_psd)])
        amplitude = float(np.sqrt(np.max(alpha_psd)))
    else:
        dominant_freq = 0.0
        amplitude = 0.0

    return {
        "frequency_hz": dominant_freq,
        "amplitude_uv": amplitude,
    }


def check_age_normal(frequency_hz: float, age_years: int) -> dict:
    """Verifica se o ritmo de base é normal para a idade."""
    if age_years < 3:
        expected = (5, 7)
    elif age_years < 8:
        expected = (7, 9)
    else:
        expected = (8, 12)

    is_normal = expected[0] <= frequency_hz <= expected[1]
    return {
        "is_normal": is_normal,
        "expected_range": expected,
        "description": f"{frequency_hz:.1f} Hz ({'normal' if is_normal else 'alterado'} para {age_years} anos)",
    }
