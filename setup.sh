#!/bin/bash
set -e  # Exit on any error

echo "Creating virtual environment..."
python3.10 -m venv vaicenv

echo "Activating virtual environment..."
source vaicenv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing wheel for faster build..."
pip install wheel

echo "Installing faster-whisper..."
pip install TTS

echo "Installing required transformers version..."
pip install transformers==4.36.2

sudo apt update

echo "Installing nvidia-cuda..."
sudo apt install nvidia-cuda-toolkit

echo "Installing ffmpeg..."
sudo apt install -y ffmpeg

echo "Installing ffmpeg..."
pip install -r requirements.txt

echo "🎵 IMPORTANT: Make sure you have an 'sample.wav' file in this directory before proceeding! 🎵"
echo "📁 The test script will look for 'sample.wav' to transcribe."
echo "⚠️ RUN tts with model xtts_v2 once, it should fail. After this place this in the xtts.py in line 771 before (checkpoint = self.get_compatible_checkpoint_state_dict(model_path)):

import torch.serialization
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig

torch.serialization.add_safe_globals([
    XttsConfig,
    XttsAudioConfig,
    XttsArgs,
    BaseDatasetConfig
])

"
echo "⏳ Press Enter when you're ready to run the test xtts, or Ctrl+C to exit..."
read -p "🚀 Ready to test xtts?? "

echo "🧪 Running xtts test..."
tts --text "A veces me detengo a pensar en lo increíble que es vivir en esta época. Hace unos años, hablar con una inteligencia artificial era ciencia ficción, y hoy, mi propia voz puede ser recreada por un modelo entrenado en segundos. Es como si el futuro hubiera llegado sin avisar, y ahora somos parte de él, experimentando posibilidades que antes solo existían en los sueños de los inventores." \
  --model_name tts_models/multilingual/multi-dataset/xtts_v2 \
  --speaker_wav voice-samples/sample.wav \
  --language_idx es \
  --out_path output.wav \

echo "🎉 Test for coqui-tts and xtts completed! Check 'output.wav' for the generated audio."

pip install faster-whisper

python3.10 fastwhisper-test.py

echo "🎉 Test for fast-whisper completed!"

echo "
En caso de que salga este error: 

--------------------------------------------------
Unable to load any of {libcudnn_ops.so.9.1.0, libcudnn_ops.so.9.1, libcudnn_ops.so.9, libcudnn_ops.so}
Invalid handle. Cannot load symbol cudnnCreateTensorDescriptor
Aborted (core dumped)
--------------------------------------------------

Es necesario descargar cuda: cudnn-linux-x86_64-9.10.2.21_cuda12-archive.tar.xz desde https://developer.nvidia.com/rdp/cudnn-download
y realizar symlinks asi:

# Descomprimir
cd ~/Downloads
tar -xvf cudnn-linux-x86_64-9.10.2.21_cuda12-archive.tar.xz
cd cudnn-linux-x86_64-9.10.2.21_cuda12-archive

# Copiar headers
sudo cp include/* /usr/local/cuda/include/

# Copiar librerías
sudo cp lib/* /usr/local/cuda/lib64/

# Recargar links dinámicos
sudo ldconfig

ls /usr/local/cuda/lib64 | grep cudnn

y finalmente volver a nuestro proyecto (cd /Fast-Whisper) y :
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

Despues ejecutar de nuevo:
python3.10 fastwhisper-test.py
"

