"""Leitor de arquivos EDF — extrai metadados e dados do sinal EEG.

Usa edfio (leve, ~1 MB) em vez de MNE (~300 MB) para funcionar
no Render free tier (512 MB RAM).
"""

import numpy as np

# Máximo de segundos a carregar (limita uso de memória)
MAX_DURATION_SECONDS = 60


def read_edf(file_path: str) -> dict:
    """
    Lê um arquivo .EDF e retorna metadados + dados brutos.
    Usa edfio (leve) em vez de MNE para economizar memória.
    Carrega dados de forma lazy para limitar uso de RAM.
    """
    from edfio import read_edf as edfio_read

    edf = edfio_read(file_path, lazy_load_data=True)

    channel_names = [signal.label.strip() for signal in edf.signals]
    sampling_rate = float(edf.signals[0].sampling_frequency)
    n_channels = len(edf.signals)
    # edf.duration pode ser float (segundos) ou timedelta dependendo da versão
    dur = edf.duration
    duration_seconds = float(dur.total_seconds()) if hasattr(dur, 'total_seconds') else float(dur)

    # Limite de amostras a carregar (60s max)
    max_samples = int(min(MAX_DURATION_SECONDS, duration_seconds) * sampling_rate)

    # Pre-alocar array e preencher canal por canal (evita pico de memória)
    data = np.empty((n_channels, max_samples), dtype=np.float64)
    for i, signal in enumerate(edf.signals):
        data[i] = signal.data[:max_samples]

    metadata = {
        "n_channels": n_channels,
        "sampling_rate": sampling_rate,
        "duration_seconds": duration_seconds,
        "channel_names": channel_names,
        "patient_info": {},
    }

    return {"data": data, "metadata": metadata}


def validate_edf(file_path: str) -> dict:
    """Valida se o arquivo é um EDF válido e retorna metadados."""
    try:
        from edfio import read_edf as edfio_read
        edf = edfio_read(file_path, lazy_load_data=True)
        dur = edf.duration
        duration_seconds = float(dur.total_seconds()) if hasattr(dur, 'total_seconds') else float(dur)
        return {
            "valid": True,
            "n_channels": len(edf.signals),
            "sampling_rate": float(edf.signals[0].sampling_frequency),
            "duration_seconds": duration_seconds,
            "channel_names": [s.label.strip() for s in edf.signals],
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}
