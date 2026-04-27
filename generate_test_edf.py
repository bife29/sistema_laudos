"""
Gera um arquivo .EDF fictício com dados EEG realistas para testes do sistema.

Os sinais simulam um EEG normal de adulto com:
- 19 canais no padrão 10-20 internacional
- Ritmo alfa dominante (~10 Hz) nas regiões posteriores (O1, O2, P3, P4)
- Atividade theta e delta em menor amplitude
- Atividade beta de baixa amplitude difusa
- Ruído muscular leve (EMG) nos canais frontais
- Artefatos de piscar (blink) em Fp1/Fp2
- Duração de 30 segundos
- Frequência de amostragem de 256 Hz

Uso:
    python generate_test_edf.py
    python generate_test_edf.py --output meu_arquivo.edf --duration 60 --abnormal
"""

import argparse
import numpy as np
import mne


# Canais padrão do sistema 10-20 (mesmos do analysis_pipeline.py)
STANDARD_CHANNELS = [
    "Fp1", "Fp2", "F3", "F4", "C3", "C4", "P3", "P4",
    "O1", "O2", "F7", "F8", "T3", "T4", "T5", "T6",
    "Fz", "Cz", "Pz",
]

# Classificação regional dos canais
FRONTAL_CHANNELS = {"Fp1", "Fp2", "F3", "F4", "F7", "F8", "Fz"}
CENTRAL_CHANNELS = {"C3", "C4", "Cz"}
PARIETAL_CHANNELS = {"P3", "P4", "Pz"}
OCCIPITAL_CHANNELS = {"O1", "O2"}
TEMPORAL_CHANNELS = {"T3", "T4", "T5", "T6"}
POSTERIOR_CHANNELS = {"O1", "O2", "P3", "P4"}

LEFT_CHANNELS = {"Fp1", "F3", "C3", "P3", "O1", "F7", "T3", "T5"}


def generate_band_signal(n_samples: int, sfreq: float, freq_range: tuple, amplitude: float) -> np.ndarray:
    """Gera um sinal numa faixa de frequência específica."""
    t = np.arange(n_samples) / sfreq
    signal = np.zeros(n_samples)
    # Combina várias frequências dentro da faixa
    n_components = np.random.randint(3, 7)
    for _ in range(n_components):
        freq = np.random.uniform(freq_range[0], freq_range[1])
        phase = np.random.uniform(0, 2 * np.pi)
        amp = amplitude * np.random.uniform(0.3, 1.0)
        signal += amp * np.sin(2 * np.pi * freq * t + phase)
    return signal


def generate_blink_artifacts(n_samples: int, sfreq: float, n_blinks: int = 5) -> np.ndarray:
    """Gera artefatos de piscar (ondas lentas e altas em Fp1/Fp2)."""
    signal = np.zeros(n_samples)
    duration = n_samples / sfreq
    for _ in range(n_blinks):
        # Posição aleatória do piscar
        center = np.random.uniform(1, duration - 1)
        center_sample = int(center * sfreq)
        # Duração do piscar: ~200-400 ms
        width = int(np.random.uniform(0.2, 0.4) * sfreq)
        # Amplitude: 100-200 µV
        amp = np.random.uniform(100e-6, 200e-6)
        start = max(0, center_sample - width)
        end = min(n_samples, center_sample + width)
        x = np.linspace(-np.pi, np.pi, end - start)
        signal[start:end] += amp * (np.cos(x) + 1) / 2
    return signal


def generate_eeg_channel(
    channel_name: str,
    n_samples: int,
    sfreq: float,
    abnormal: bool = False,
    asymmetry_side: str = "none",
) -> np.ndarray:
    """
    Gera dados EEG realistas para um canal específico.
    Amplitudes em Volts (padrão MNE).
    EEG típico: 10-100 µV = 10e-6 a 100e-6 V
    """
    # Amplitudes base por banda (em µV, convertendo para V no final)
    delta_amp = 15e-6   # 0.5-4 Hz
    theta_amp = 10e-6   # 4-8 Hz
    alpha_amp = 5e-6    # 8-13 Hz (base, aumenta em posterior)
    beta_amp = 3e-6     # 13-30 Hz
    noise_amp = 2e-6    # Ruído de fundo

    # Ajuste regional
    if channel_name in OCCIPITAL_CHANNELS:
        alpha_amp = 40e-6  # Alfa muito forte em occipital
    elif channel_name in PARIETAL_CHANNELS:
        alpha_amp = 25e-6  # Alfa moderado em parietal
    elif channel_name in POSTERIOR_CHANNELS:
        alpha_amp = 30e-6
    elif channel_name in FRONTAL_CHANNELS:
        beta_amp = 6e-6    # Mais beta em frontal
        delta_amp = 10e-6  # Menos delta em frontal

    if channel_name in TEMPORAL_CHANNELS:
        theta_amp = 12e-6  # Ligeiramente mais theta em temporal

    # Modo anormal: aumenta delta/theta, reduz alfa
    if abnormal:
        delta_amp *= 2.5
        theta_amp *= 2.0
        alpha_amp *= 0.5
        if channel_name in LEFT_CHANNELS and asymmetry_side == "left":
            delta_amp *= 1.8  # Lentificação focal à esquerda

    # Gera o sinal composto
    signal = np.zeros(n_samples)
    signal += generate_band_signal(n_samples, sfreq, (0.5, 4), delta_amp)
    signal += generate_band_signal(n_samples, sfreq, (4, 8), theta_amp)
    signal += generate_band_signal(n_samples, sfreq, (8, 13), alpha_amp)
    signal += generate_band_signal(n_samples, sfreq, (13, 30), beta_amp)

    # Ruído gaussiano de fundo
    signal += np.random.normal(0, noise_amp, n_samples)

    # Artefatos de piscar nos canais frontopolares
    if channel_name in ("Fp1", "Fp2"):
        signal += generate_blink_artifacts(n_samples, sfreq, n_blinks=np.random.randint(3, 8))

    return signal


def generate_test_edf(
    output_path: str = "data/uploads/test_eeg.edf",
    duration_seconds: float = 30.0,
    sfreq: float = 256.0,
    abnormal: bool = False,
    patient_name: str = "Paciente Teste",
):
    """Gera um arquivo EDF completo para testes."""

    n_samples = int(duration_seconds * sfreq)
    n_channels = len(STANDARD_CHANNELS)

    print(f"Gerando EDF de teste...")
    print(f"  Canais: {n_channels} ({', '.join(STANDARD_CHANNELS)})")
    print(f"  Duração: {duration_seconds}s")
    print(f"  Frequência de amostragem: {sfreq} Hz")
    print(f"  Tipo: {'ANORMAL (com assimetria e lentificação)' if abnormal else 'NORMAL'}")
    print(f"  Amostras por canal: {n_samples}")

    # Gera dados para cada canal
    data = np.zeros((n_channels, n_samples))
    asymmetry_side = "left" if abnormal else "none"

    for i, ch_name in enumerate(STANDARD_CHANNELS):
        data[i] = generate_eeg_channel(
            ch_name, n_samples, sfreq,
            abnormal=abnormal,
            asymmetry_side=asymmetry_side,
        )

    # Cria objeto MNE RawArray
    ch_types = ["eeg"] * n_channels
    info = mne.create_info(ch_names=STANDARD_CHANNELS, sfreq=sfreq, ch_types=ch_types)

    # Define montagem padrão 10-20
    montage = mne.channels.make_standard_montage("standard_1020")
    info.set_montage(montage, on_missing="ignore")

    raw = mne.io.RawArray(data, info, verbose=False)

    # Exporta para EDF
    raw.export(output_path, fmt="edf", overwrite=True, verbose=False)

    print(f"\n  Arquivo gerado: {output_path}")
    print(f"  Tamanho: {n_samples * n_channels * 2 / 1024:.0f} KB (estimado)")

    # Validação rápida: reabre e verifica
    print(f"\nValidando arquivo gerado...")
    raw_check = mne.io.read_raw_edf(output_path, preload=False, verbose=False)
    print(f"  Canais lidos: {raw_check.info['nchan']}")
    print(f"  Sfreq: {raw_check.info['sfreq']} Hz")
    print(f"  Duração: {raw_check.times[-1]:.1f}s")
    print(f"  Nomes dos canais: {raw_check.ch_names}")
    print(f"\nArquivo EDF pronto para uso no sistema!")

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Gera arquivo EDF fictício para testes do sistema de laudos EEG")
    parser.add_argument(
        "--output", "-o",
        default="data/uploads/test_eeg.edf",
        help="Caminho do arquivo de saída (default: data/uploads/test_eeg.edf)",
    )
    parser.add_argument(
        "--duration", "-d",
        type=float,
        default=30.0,
        help="Duração em segundos (default: 30)",
    )
    parser.add_argument(
        "--sfreq", "-s",
        type=float,
        default=256.0,
        help="Frequência de amostragem em Hz (default: 256)",
    )
    parser.add_argument(
        "--abnormal", "-a",
        action="store_true",
        help="Gera um EEG anormal (com assimetria e lentificação focal)",
    )
    parser.add_argument(
        "--both", "-b",
        action="store_true",
        help="Gera dois arquivos: um normal e um anormal",
    )

    args = parser.parse_args()

    if args.both:
        # Gera versão normal
        normal_path = args.output.replace(".edf", "_normal.edf")
        print("=" * 60)
        print("GERANDO EEG NORMAL")
        print("=" * 60)
        generate_test_edf(normal_path, args.duration, args.sfreq, abnormal=False)

        # Gera versão anormal
        abnormal_path = args.output.replace(".edf", "_anormal.edf")
        print()
        print("=" * 60)
        print("GERANDO EEG ANORMAL")
        print("=" * 60)
        generate_test_edf(abnormal_path, args.duration, args.sfreq, abnormal=True)
    else:
        generate_test_edf(args.output, args.duration, args.sfreq, args.abnormal)


if __name__ == "__main__":
    main()
