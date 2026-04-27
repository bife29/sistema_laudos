"""Leitor de arquivos EDF — extrai metadados e dados do sinal EEG."""

# Máximo de segundos a carregar (limita uso de memória em hosts free)
MAX_DURATION_SECONDS = 60


def read_edf(file_path: str) -> dict:
    """
    Lê um arquivo .EDF e retorna metadados + dados brutos.
    Carrega no máximo MAX_DURATION_SECONDS para limitar uso de RAM.
    Requer MNE-Python instalado.
    """
    import mne

    # Primeiro lê sem carregar dados para pegar metadados
    raw = mne.io.read_raw_edf(file_path, preload=False, verbose=False)

    metadata = {
        "n_channels": raw.info["nchan"],
        "sampling_rate": raw.info["sfreq"],
        "duration_seconds": raw.times[-1],
        "channel_names": raw.ch_names,
        "patient_info": raw.info.get("subject_info", {}),
    }

    # Carrega apenas os primeiros N segundos para economizar memória
    tmax = min(MAX_DURATION_SECONDS, raw.times[-1])
    raw.crop(tmin=0, tmax=tmax)
    raw.load_data(verbose=False)

    return {"raw": raw, "metadata": metadata}


def validate_edf(file_path: str) -> dict:
    """
    Valida se o arquivo é um EDF válido e retorna metadados.
    Não carrega os dados na memória (mais rápido).
    """
    import mne

    try:
        raw = mne.io.read_raw_edf(file_path, preload=False, verbose=False)
        return {
            "valid": True,
            "n_channels": raw.info["nchan"],
            "sampling_rate": raw.info["sfreq"],
            "duration_seconds": raw.times[-1],
            "channel_names": raw.ch_names,
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}
