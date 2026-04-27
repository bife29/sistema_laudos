"""Leitor de arquivos EDF — extrai metadados e dados do sinal EEG."""


def read_edf(file_path: str) -> dict:
    """
    Lê um arquivo .EDF e retorna metadados + dados brutos.
    Requer MNE-Python instalado.
    """
    import mne

    raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)

    metadata = {
        "n_channels": raw.info["nchan"],
        "sampling_rate": raw.info["sfreq"],
        "duration_seconds": raw.times[-1],
        "channel_names": raw.ch_names,
        "patient_info": raw.info.get("subject_info", {}),
    }

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
